#!/usr/bin/env python3
"""
Fetch economic news + generate newsletter-style markdown post via Claude API.
Saves to ../posts/YYYY-MM-DD.md and updates ../data/seen-articles.json.

Skips (exits 0, no file written) if there aren't at least 2 genuinely new
(never-published-before) and fresh (<48h) articles.

Required env vars:
  NEWSDATA_API_KEY  — https://newsdata.io
  ANTHROPIC_API_KEY — https://console.anthropic.com
"""

import json
import os
import re
import ssl
import sys
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timedelta, timezone
from pathlib import Path

try:
    import certifi
    SSL_CTX = ssl.create_default_context(cafile=certifi.where())
except ImportError:
    SSL_CTX = ssl.create_default_context()

try:
    import anthropic
except ImportError:
    print("Erro: instale o pacote anthropic com: pip install anthropic")
    sys.exit(1)

ROOT = Path(__file__).parent.parent
SEEN_PATH = ROOT / "data" / "seen-articles.json"
POSTS_DIR = ROOT / "posts"

IRRELEVANT = [
    "sport", "football", "soccer", "rugby", "cricket", "golf",
    "celebrity", "entertainment", "oscar", "grammy", "film", "movie",
    "tv show", "reality show", "singer", "actor", "actress",
]


def fetch_article_text(url: str, max_chars: int = 4000) -> str:
    """Busca o HTML da notícia original e extrai texto legível (best-effort).

    NewsData.io no plano free costuma mandar `description` vazio ou truncado
    demais pra escrever com precisão (números, nuance de "planeja" vs "fez",
    contexto tipo "empresa já estava em recuperação judicial há meses"). Ter
    o texto completo do artigo original resolve isso na maioria dos casos.
    Falha silenciosamente (retorna "") se o site bloquear ou der timeout —
    nesse caso o gerador cai de volta pro description curto da API.
    """
    if not url:
        return ""
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (compatible; IrlandaEmFocoBot/1.0)"})
    try:
        with urllib.request.urlopen(req, timeout=8, context=SSL_CTX) as r:
            raw = r.read(300_000).decode("utf-8", errors="ignore")
    except Exception:
        return ""

    raw = re.sub(r"<script.*?</script>", " ", raw, flags=re.DOTALL | re.IGNORECASE)
    raw = re.sub(r"<style.*?</style>", " ", raw, flags=re.DOTALL | re.IGNORECASE)
    text = re.sub(r"<[^>]+>", " ", raw)
    text = re.sub(r"&amp;", "&", text)
    text = re.sub(r"&nbsp;", " ", text)
    text = re.sub(r"&#?\w+;", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text[:max_chars]

# ── NewsData.io ──────────────────────────────────────────────────────────────
# qInTitle tem limite de tamanho da API — por isso termos curtos, sem aspas.

NEWSDATA_BASE = "https://newsdata.io/api/1/latest"


def _fetch(q_in_title: str, api_key: str, country: str | None = None, category: str | None = "business") -> list[dict]:
    params_dict = {"qInTitle": q_in_title, "language": "en", "apikey": api_key}
    if category:
        params_dict["category"] = category
    if country:
        params_dict["country"] = country
    params = urllib.parse.urlencode(params_dict)
    url = f"{NEWSDATA_BASE}?{params}"
    try:
        with urllib.request.urlopen(url, timeout=15, context=SSL_CTX) as r:
            data = json.loads(r.read().decode())
    except urllib.error.HTTPError as e:
        msg = json.loads(e.read().decode()).get("results", {}).get("message", str(e))
        print(f"Erro NewsData.io: {msg}", file=sys.stderr)
        sys.exit(1)
    except urllib.error.URLError as e:
        print(f"Erro de rede: {e.reason}", file=sys.stderr)
        sys.exit(1)

    articles = data.get("results") or []
    result = []
    for a in articles:
        title = a.get("title", "") or ""
        desc = a.get("description", "") or ""
        text = f"{title} {desc}".lower()
        if any(kw in text for kw in IRRELEVANT):
            continue
        result.append({
            "title": title,
            "source": a.get("source_id", "") or "",
            "description": desc,
            "url": a.get("link", "") or "",
            "publishedAt": a.get("pubDate", "") or "",
        })
    return result


def load_seen() -> list[dict]:
    try:
        return json.loads(SEEN_PATH.read_text(encoding="utf-8"))
    except FileNotFoundError:
        return []


def is_fresh(article: dict, cutoff: datetime) -> bool:
    try:
        pub = datetime.strptime(article["publishedAt"], "%Y-%m-%d %H:%M:%S").replace(tzinfo=timezone.utc)
        return pub > cutoff
    except (ValueError, KeyError):
        return False


def fetch_fresh_new_news(news_key: str) -> dict:
    seen_urls = {a["url"] for a in load_seen() if a.get("url")}
    cutoff_48h = datetime.now(timezone.utc) - timedelta(hours=48)

    # Consultas separadas e específicas pros temas que mais importam pro leitor
    # (aluguel/moradia, emprego, custo de vida) em vez de só "Ireland" genérico,
    # que trazia demais notícia de negócio corporativo pouco relevante.
    # IMPORTANTE: qInTitle do NewsData.io só funciona bem com termos de UMA palavra
    # separados por OR — frases de várias palavras ("Ireland rent") retornam 0
    # resultados mesmo quando existem artigos relevantes. Por isso usamos country=ie
    # + termos soltos em vez de frases.
    ireland_housing = _fetch("rent OR housing", news_key, country="ie", category=None)
    ireland_jobs = _fetch("jobs OR unemployment OR hiring", news_key, country="ie", category=None)
    ireland_general = _fetch("Ireland", news_key, category="business")
    seen_ids = set()
    ireland = []
    for a in ireland_housing + ireland_jobs + ireland_general:
        if a["url"] and a["url"] not in seen_ids:
            seen_ids.add(a["url"])
            ireland.append(a)

    world = _fetch("eurozone OR ECB OR inflation", news_key)

    def is_new(article: dict) -> bool:
        return bool(article.get("url")) and article["url"] not in seen_urls

    fresh_ireland = [a for a in ireland if is_fresh(a, cutoff_48h) and is_new(a)]
    fresh_world = [a for a in world if is_fresh(a, cutoff_48h) and is_new(a)]

    # Enriquecer com o texto completo do artigo original — o `description` da
    # NewsData.io no plano free costuma ser curto/vazio demais pra escrever
    # com precisão (números exatos, nuance tipo "empresa já estava em
    # recuperação judicial há meses"). Falha por artigo é ignorada (fica só
    # com o description curto nesse caso) — não derruba o script inteiro.
    for a in fresh_ireland + fresh_world:
        full_text = fetch_article_text(a["url"])
        if full_text:
            a["full_text"] = full_text

    return {
        "fetched_at": datetime.now(timezone.utc).isoformat(),
        "ireland": fresh_ireland,
        "world": fresh_world,
    }


def update_seen(used_articles: list[dict]) -> None:
    seen = load_seen()
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    for a in used_articles:
        seen.append({"url": a["url"], "title": a["title"], "publishedAt": a["publishedAt"], "used_date": today})

    cutoff = datetime.now(timezone.utc).timestamp() - 30 * 86400

    def keep(entry: dict) -> bool:
        try:
            d = datetime.strptime(entry["used_date"], "%Y-%m-%d").replace(tzinfo=timezone.utc)
            return d.timestamp() > cutoff
        except Exception:
            return True

    seen = [e for e in seen if keep(e)]
    SEEN_PATH.parent.mkdir(exist_ok=True)
    SEEN_PATH.write_text(json.dumps(seen, ensure_ascii=False, indent=2), encoding="utf-8")


# ── Claude API ────────────────────────────────────────────────────────────────

SYSTEM_PROMPT = """Você é o autor da newsletter "Irlanda em Foco", escrita para imigrantes brasileiros na Irlanda.
Sua tarefa é transformar as notícias fornecidas numa edição curta e escaneável em Português Brasileiro.

Sua resposta deve começar EXATAMENTE com duas linhas assim, antes de qualquer outra coisa:

TITULO: [manchete factual sobre o fato mais relevante da edição, estilo jornalístico — não genérico. Máximo 70 caracteres. Exemplo real: "Aluguel em Dublin sobe 8% e desemprego em tech chega a 5%"]
DESCRICAO: [resumo do fato mais importante para meta description, 120 a 155 caracteres, frase completa]

Depois de uma linha em branco, o corpo deve seguir EXATAMENTE este formato markdown (sem repetir título ou data como cabeçalho — isso já fica no frontmatter da página):

Bom dia! Aqui está o que você precisa saber hoje [se houver conteúdo de Irlanda E de Mundo: "sobre a economia da Irlanda e do mundo"] [se só houver Irlanda: "sobre a economia da Irlanda"] [se só houver Mundo: "sobre a economia mundial"].

---

## 🇮🇪 Irlanda

- **[Manchete traduzida]** — resumo direto em 1-2 frases. _[[Fonte]]([url da notícia]), [data]_
- **[Manchete traduzida]** — resumo direto em 1-2 frases. _[[Fonte]]([url da notícia]), [data]_

## 🌍 Mundo

- **[Manchete traduzida]** — resumo direto em 1-2 frases. _[[Fonte]]([url da notícia]), [data]_
- **[Manchete traduzida]** — resumo direto em 1-2 frases. _[[Fonte]]([url da notícia]), [data]_

---

## 💡 O que isso significa pra você

- [1 bullet de implicação prática para o imigrante brasileiro na Irlanda]
- [1 bullet de implicação prática para o imigrante brasileiro na Irlanda]

---

*Fontes desta edição: [liste só as fontes realmente usadas]*

*Pesquisa e redação 100% automáticas com apoio de IA — sem revisão humana antes de publicar.*

REGRAS:
- Escreva TODO o conteúdo em Português Brasileiro
- Traduza os títulos das notícias para PT-BR ao citá-los
- Se só houver notícias de Irlanda (ou só de Mundo), omita a seção vazia em vez de forçar conteúdo
- NÃO invente dados. Use apenas o que está nas notícias fornecidas — quando um item tiver o campo `full_text` (texto completo do artigo original), prefira ele ao `description` (que costuma vir curto/vazio) pra pegar números exatos e contexto que mudam o sentido da notícia (ex.: uma empresa "fechou de repente" pode na verdade já estar em recuperação judicial há meses — isso só aparece no texto completo, não no resumo)
- Se houver artigos com título muito parecido (a mesma notícia repetida por vários veículos), trate como uma coisa só — não repita o mesmo fato várias vezes
- Mantenha os bullets curtos — isso é uma newsletter, não um relatório longo
- NÃO afirme regras específicas de visto, IRP ou permits (Critical Skills, General Employment, etc.) a menos que a notícia fornecida já cite a fonte oficial (Citizens Information, Departamento de Justiça) — se a notícia só menciona o tema sem fonte oficial, trate como "segundo [veículo]" e não como fato confirmado, ou omita
- O TITULO nunca pode ser genérico ("Irlanda em Foco — [data]"). Precisa nomear o fato mais relevante da edição
- TESTE DO NÚMERO: toda afirmação de tendência ("subiu", "recuperou", "acelerou", "caiu") precisa carregar o número primário entre parênteses no mesmo bullet (ex.: "PMI subiu para 54,2 pontos, de 51,8 em junho"). Se a notícia fornecida não dá o número, reescreva o bullet pra citar só o que é verificável, ou corte o bullet
- TESTE DA JURISDIÇÃO: na seção "O que isso significa pra você", qualquer causalidade entre política monetária e custo de vida na Irlanda só pode ser afirmada se a notícia citada for sobre o BCE/Irlanda especificamente — NUNCA infira consequência pra Irlanda a partir de dado do Fed/EUA (são bancos centrais diferentes, hipotecas irlandesas são precificadas pelo BCE). Se a notícia é sobre o Fed/EUA, a implicação pra Irlanda deve virar pergunta em aberto ("ainda não está claro se isso afeta a zona do euro") em vez de afirmação direta, ou seja omitida
- Bullets vagos sem conteúdo verificável (ex.: "9 empresas estão contratando" sem nomear nenhuma) são proibidos — ou cite pelo menos 1-2 exemplos concretos (nome da empresa/cargo) que estejam na notícia fornecida, ou omita o bullet inteiro
- TESTE DA RELEVÂNCIA: cada item selecionado precisa passar o teste "por que isso importa pra você" com um mecanismo concreto e SEM ressalva — aluguel, salário, vaga de emprego, câmbio EUR/BRL, IRP/visto, ou custo de vida direto. Se você só consegue justificar a inclusão com uma ressalva tipo "ainda não está claro se isso afeta..." ou "não é bem a mesma coisa, mas...", CORTE o item em vez de publicar com a ressalva. Notícia de banco central que não é do BCE/Irlanda só entra se tiver um link explícito e calculável com a zona do euro — não basta ser "sobre economia"
- COBERTURA MÍNIMA: dado que as notícias de Irlanda já vêm filtradas por aluguel/moradia, emprego e economia geral, priorize ter pelo menos 1 item sobre moradia/aluguel OU emprego na seção Irlanda quando houver algo disponível nesses temas — são os que mais afetam o leitor no dia a dia. Só recorra a notícia de economia geral da Irlanda se genuinamente não houver nada de moradia/emprego disponível
- TESTE DA MODALIDADE: o verbo em português precisa ter exatamente a mesma certeza que a fonte original. Se a notícia diz "planeja criar", "pode criar", "sujeito a aprovação", "pretende", "vai pedir permissão para" — NUNCA escreva como se já tivesse acontecido ("criou", "confirmou", "abriu vagas"). Vagas de emprego anunciadas como projeto/plano futuro (comum em notícia de expansão de empresa) DEVEM manter o verbo no futuro/condicional em português ("a empresa planeja criar até X vagas, sujeito a aprovação de...") — nunca vire manchete de fato consumado
- ÂNGULO DO IMIGRANTE: o leitor não é um candidato irlandês genérico — ele frequentemente precisa de patrocínio de visto/permit de trabalho (Critical Skills Permit, General Employment Permit) pra ser contratado. Sempre que citar vagas de emprego específicas, SE a notícia fornecida mencionar (ou você souber com certeza pela empresa/setor) se a vaga costuma exigir cidadania UE/EEE ou aceita patrocínio de visto, inclua essa informação em 1 frase curta. Se a notícia não der esse dado, NÃO invente — pode citar a vaga normalmente sem essa informação, só não finja que ela existe
- CITAÇÃO VERIFICÁVEL: toda fonte citada precisa ser um link markdown de verdade usando a URL exata do campo `url` da notícia fornecida — nunca cite "Fonte: [nome]" sem link. Isso permite que qualquer leitor (ou editor) confira a notícia original com 1 clique, sem precisar confiar cegamente na citação
- Frases com números que podem gerar ambiguidade (ex.: preço por pessoa vs. preço total, "compartilhar cama" vs. "compartilhar quarto") precisam ser reescritas de um jeito que não deixe dúvida de leitura na primeira passada — releia cada bullet como se fosse a primeira vez lendo, sem o contexto de quem escreveu
- Se um anúncio/vaga/oferta citado tiver restrição de elegibilidade relevante (ex.: "só para mulheres", "só para EU/EEA", "só CV em inglês"), inclua isso entre parênteses — evita que o leitor perca tempo com algo que não se aplica a ele
- A saudação de abertura deve refletir o conteúdo real da edição (não prometer "Irlanda e mundo" se só houver uma das duas seções) — use a variação certa entre as opções descritas no formato acima"""


def generate_post(news: dict, anthropic_api_key: str) -> str:
    today = datetime.now(timezone.utc)
    data_str = today.strftime("%d de %B de %Y").replace(
        "January", "Janeiro").replace("February", "Fevereiro").replace(
        "March", "Março").replace("April", "Abril").replace(
        "May", "Maio").replace("June", "Junho").replace(
        "July", "Julho").replace("August", "Agosto").replace(
        "September", "Setembro").replace("October", "Outubro").replace(
        "November", "Novembro").replace("December", "Dezembro")

    user_content = f"""Data de hoje: {data_str}
Hora da coleta: {news['fetched_at']}

=== NOTÍCIAS SOBRE A IRLANDA (só as genuinamente novas e recentes) ===
{json.dumps(news['ireland'], ensure_ascii=False, indent=2)}

=== NOTÍCIAS GLOBAIS (só as genuinamente novas e recentes) ===
{json.dumps(news['world'], ensure_ascii=False, indent=2)}

Gere a edição completa seguindo o formato do sistema."""

    client = anthropic.Anthropic(api_key=anthropic_api_key)
    message = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=2048,
        system=[
            {
                "type": "text",
                "text": SYSTEM_PROMPT,
                "cache_control": {"type": "ephemeral"},
            }
        ],
        messages=[{"role": "user", "content": user_content}],
    )
    return message.content[0].text


def parse_title_and_description(report: str) -> tuple[str, str, str]:
    lines = report.strip().split("\n")
    if len(lines) < 2 or not lines[0].startswith("TITULO:") or not lines[1].startswith("DESCRICAO:"):
        print("Erro: resposta do Claude não começou com TITULO:/DESCRICAO: como exigido.", file=sys.stderr)
        sys.exit(1)
    titulo = lines[0].removeprefix("TITULO:").strip()
    descricao = lines[1].removeprefix("DESCRICAO:").strip()
    body = "\n".join(lines[2:]).lstrip("\n")
    return titulo, descricao, body


def yaml_quote(value: str) -> str:
    return '"' + value.replace('"', '\\"') + '"'


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    news_key = os.environ.get("NEWSDATA_API_KEY", "")
    anthropic_key = os.environ.get("ANTHROPIC_API_KEY", "")

    if not news_key:
        print("Erro: NEWSDATA_API_KEY não definida.", file=sys.stderr)
        sys.exit(1)
    if not anthropic_key:
        print("Erro: ANTHROPIC_API_KEY não definida.", file=sys.stderr)
        sys.exit(1)

    slug = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    out_path = POSTS_DIR / f"{slug}.md"
    if out_path.exists():
        print(f"Edição de hoje já existe em {out_path}, encerrando.", file=sys.stderr)
        return

    print("Buscando notícias novas e inéditas...", file=sys.stderr)
    news = fetch_fresh_new_news(news_key)
    total = len(news["ireland"]) + len(news["world"])
    print(f"  {len(news['ireland'])} da Irlanda + {len(news['world'])} do mundo = {total}", file=sys.stderr)

    if total < 2:
        print("SKIP: menos de 2 artigos novos e inéditos nas últimas 48h. Sem edição hoje.", file=sys.stderr)
        return

    print("Gerando edição com Claude...", file=sys.stderr)
    report_raw = generate_post(news, anthropic_key)
    titulo, descricao, report_body = parse_title_and_description(report_raw)

    frontmatter = (
        "---\n"
        f"title: {yaml_quote(titulo)}\n"
        f"description: {yaml_quote(descricao)}\n"
        f"date: {slug}\n"
        "---\n\n"
    )
    final = frontmatter + report_body

    POSTS_DIR.mkdir(exist_ok=True)
    out_path.write_text(final, encoding="utf-8")
    print(f"Edição salva em: {out_path}", file=sys.stderr)

    update_seen(news["ireland"] + news["world"])
    print(f"seen-articles.json atualizado.", file=sys.stderr)


if __name__ == "__main__":
    main()
