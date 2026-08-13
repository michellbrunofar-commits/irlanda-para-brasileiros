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

# ── NewsData.io ──────────────────────────────────────────────────────────────
# qInTitle tem limite de tamanho da API — por isso termos curtos, sem aspas.

NEWSDATA_BASE = "https://newsdata.io/api/1/latest"


def _fetch(q_in_title: str, api_key: str) -> list[dict]:
    params = urllib.parse.urlencode({
        "qInTitle": q_in_title, "category": "business", "language": "en", "apikey": api_key,
    })
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

    ireland = _fetch("Ireland", news_key)
    world = _fetch("eurozone OR ECB OR inflation", news_key)

    def is_new(article: dict) -> bool:
        return bool(article.get("url")) and article["url"] not in seen_urls

    fresh_ireland = [a for a in ireland if is_fresh(a, cutoff_48h) and is_new(a)]
    fresh_world = [a for a in world if is_fresh(a, cutoff_48h) and is_new(a)]

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

Bom dia! Aqui está o que você precisa saber hoje sobre a economia da Irlanda e do mundo.

---

## 🇮🇪 Irlanda

- **[Manchete traduzida]** — resumo direto em 1-2 frases. _[Fonte], [data]_
- **[Manchete traduzida]** — resumo direto em 1-2 frases. _[Fonte], [data]_

## 🌍 Mundo

- **[Manchete traduzida]** — resumo direto em 1-2 frases. _[Fonte], [data]_
- **[Manchete traduzida]** — resumo direto em 1-2 frases. _[Fonte], [data]_

---

## 💡 O que isso significa pra você

- [1 bullet de implicação prática para o imigrante brasileiro na Irlanda]
- [1 bullet de implicação prática para o imigrante brasileiro na Irlanda]

---

*Fontes desta edição: [liste só as fontes realmente usadas]*

*Pesquisa e primeira versão com apoio de IA, publicação automática.*

REGRAS:
- Escreva TODO o conteúdo em Português Brasileiro
- Traduza os títulos das notícias para PT-BR ao citá-los
- Se só houver notícias de Irlanda (ou só de Mundo), omita a seção vazia em vez de forçar conteúdo
- NÃO invente dados. Use apenas o que está nas notícias fornecidas
- Se houver artigos com título muito parecido (a mesma notícia repetida por vários veículos), trate como uma coisa só — não repita o mesmo fato várias vezes
- Mantenha os bullets curtos — isso é uma newsletter, não um relatório longo
- NÃO afirme regras específicas de visto, IRP ou permits (Critical Skills, General Employment, etc.) a menos que a notícia fornecida já cite a fonte oficial (Citizens Information, Departamento de Justiça) — se a notícia só menciona o tema sem fonte oficial, trate como "segundo [veículo]" e não como fato confirmado, ou omita
- O TITULO nunca pode ser genérico ("Irlanda em Foco — [data]"). Precisa nomear o fato mais relevante da edição"""


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
