#!/usr/bin/env python3
"""
Fetch economic news + generate markdown report via Claude API.
Saves to ../posts/YYYY-MM-DD.md

Required env vars:
  NEWS_API_KEY      — https://newsapi.org/register
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

# ── News API ──────────────────────────────────────────────────────────────────

NEWSAPI_BASE = "https://newsapi.org/v2/everything"

IRELAND_QUERY = (
    '"Ireland economy" OR "Irish economy" OR "Ireland jobs" OR '
    '"housing Ireland" OR "Ireland visa" OR "Ireland inflation" OR '
    '"Ireland rent" OR "Irish housing" OR "Irish immigration" OR '
    '"IDA Ireland" OR "Ireland unemployment" OR "Ireland GDP" OR '
    '"Ireland cost of living" OR "GNIB" OR "IRP permit" OR '
    '"Critical Skills permit Ireland" OR "General Employment permit Ireland"'
)

GLOBAL_QUERY = (
    '"global economy" OR "world economy" OR "eurozone" OR '
    '"ECB interest rates" OR "European Central Bank" OR '
    '"IMF forecast" OR "global recession" OR "inflation Europe" OR '
    '"EU economy" OR "Fed interest rate" OR "global GDP"'
)

IRRELEVANT = [
    "sport", "football", "soccer", "rugby", "cricket", "golf",
    "celebrity", "entertainment", "oscar", "grammy", "film", "movie",
    "tv show", "reality show", "singer", "actor", "actress",
]


def _fetch(query: str, api_key: str, page_size: int = 10) -> list[dict]:
    from_date = (datetime.now(timezone.utc) - timedelta(days=7)).strftime("%Y-%m-%d")
    params = urllib.parse.urlencode({
        "q": query, "language": "en", "sortBy": "publishedAt",
        "pageSize": page_size, "from": from_date, "apiKey": api_key,
    })
    url = f"{NEWSAPI_BASE}?{params}"
    try:
        with urllib.request.urlopen(url, timeout=15, context=SSL_CTX) as r:
            data = json.loads(r.read().decode())
    except urllib.error.HTTPError as e:
        msg = json.loads(e.read().decode()).get("message", str(e))
        print(f"Erro News API: {msg}", file=sys.stderr)
        sys.exit(1)
    except urllib.error.URLError as e:
        print(f"Erro de rede: {e.reason}", file=sys.stderr)
        sys.exit(1)

    articles = data.get("articles", [])
    result = []
    for a in articles:
        text = f"{a.get('title','')} {a.get('description','')}".lower()
        if any(kw in text for kw in IRRELEVANT):
            continue
        result.append({
            "title": a.get("title", ""),
            "source": a.get("source", {}).get("name", ""),
            "description": a.get("description", ""),
            "url": a.get("url", ""),
            "publishedAt": a.get("publishedAt", ""),
        })
    return result


def fetch_news(news_api_key: str) -> dict:
    return {
        "fetched_at": datetime.now(timezone.utc).isoformat(),
        "ireland": _fetch(IRELAND_QUERY, news_api_key),
        "global": _fetch(GLOBAL_QUERY, news_api_key),
    }


# ── Claude API ────────────────────────────────────────────────────────────────

SYSTEM_PROMPT = """Você é um analista econômico especializado em Irlanda, escrevendo para imigrantes brasileiros.
Sua tarefa é transformar as notícias fornecidas em um relatório estruturado em Português Brasileiro.

O relatório deve seguir EXATAMENTE este formato markdown:

# Análise Econômica — {DATA}
> Gerado em {HORA} | Fonte: News API (newsapi.org)

---

## Economia Irlandesa

### Visão Geral
[2-3 parágrafos sobre o estado da economia irlandesa com base nas notícias]

### Mercado de Trabalho
- **Em alta:** [setores contratando]
- **Em queda / atenção:** [setores com demissões ou desaceleração]
- **Taxa de desemprego:** [dado mais recente ou "Não disponível esta semana"]
- **Notícias relevantes:**
  - [Título traduzido] — Fonte | Data

### Habitação e Custo de Vida
- **Aluguel:** [tendência]
- **Inflação geral:** [tendência]
- **Medidas do governo:** [políticas relevantes]
- **Notícias relevantes:**
  - [Título traduzido] — Fonte | Data

### Imigração e Vistos
- **Critical Skills Permit:** [mudanças ou "Nenhuma atualização esta semana"]
- **General Employment Permit:** [atualizações ou "Nenhuma atualização esta semana"]
- **IRP (Irish Residence Permit):** [prazos, mudanças ou "Nenhuma atualização esta semana"]
- **Notícias relevantes:** [se houver]

---

## Panorama da Economia Mundial

### Destaques Globais
[2 parágrafos sobre economia mundial com foco no que afeta a Irlanda/Europa]

### Zona do Euro
- **BCE — Taxa de juros:** [decisão ou expectativa]
- **Inflação na Eurozona:** [tendência]
- **Crescimento do PIB da UE:** [dado ou projeção]
- **Notícias relevantes:**
  - [Título traduzido] — Fonte | Data

### Tendências Globais que Afetam a Irlanda
- [Ponto 1]
- [Ponto 2]

---

## O Que Isso Significa Para Você — Imigrante Brasileiro na Irlanda

### Oportunidades
- [Oportunidade concreta 1]
- [Oportunidade concreta 2]

### Pontos de Atenção
- [Alerta prático 1]
- [Alerta prático 2]

### Resumo Executivo (TL;DR)
- [Fato mais importante sobre Irlanda esta semana]
- [Fato mais importante sobre economia global]
- [Ação recomendada para o imigrante brasileiro]
- [Tendência a acompanhar nas próximas semanas]

---

*Fontes consultadas: [lista]*
*Dados baseados em notícias publicadas entre {DATA_INICIO} e {DATA_FIM}.*

REGRAS:
- Escreva TODO o conteúdo em Português Brasileiro
- Traduza os títulos das notícias para PT-BR ao citá-los
- Se não houver notícias para uma seção, escreva: "Nenhuma atualização significativa esta semana nesta área."
- NÃO invente dados. Use apenas o que está nas notícias fornecidas
- Seja direto e prático, sem jargões excessivos"""


def generate_report(news: dict, anthropic_api_key: str) -> str:
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

=== NOTÍCIAS SOBRE A IRLANDA ===
{json.dumps(news['ireland'], ensure_ascii=False, indent=2)}

=== NOTÍCIAS GLOBAIS ===
{json.dumps(news['global'], ensure_ascii=False, indent=2)}

Gere o relatório completo seguindo o formato do sistema."""

    client = anthropic.Anthropic(api_key=anthropic_api_key)
    message = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=4096,
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


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    news_key = os.environ.get("NEWS_API_KEY", "")
    anthropic_key = os.environ.get("ANTHROPIC_API_KEY", "")

    if not news_key:
        print("Erro: NEWS_API_KEY não definida.", file=sys.stderr)
        sys.exit(1)
    if not anthropic_key:
        print("Erro: ANTHROPIC_API_KEY não definida.", file=sys.stderr)
        sys.exit(1)

    print("Buscando notícias...", file=sys.stderr)
    news = fetch_news(news_key)
    print(f"  {len(news['ireland'])} notícias da Irlanda", file=sys.stderr)
    print(f"  {len(news['global'])} notícias globais", file=sys.stderr)

    print("Gerando relatório com Claude...", file=sys.stderr)
    report_body = generate_report(news, anthropic_key)

    today = datetime.now(timezone.utc)
    slug = today.strftime("%Y-%m-%d")
    title_date = today.strftime("%d de %B de %Y").replace(
        "January", "Janeiro").replace("February", "Fevereiro").replace(
        "March", "Março").replace("April", "Abril").replace(
        "May", "Maio").replace("June", "Junho").replace(
        "July", "Julho").replace("August", "Agosto").replace(
        "September", "Setembro").replace("October", "Outubro").replace(
        "November", "Novembro").replace("December", "Dezembro")

    frontmatter = f"---\ntitle: Análise Econômica — {title_date}\ndate: {slug}\n---\n\n"
    final = frontmatter + report_body

    posts_dir = Path(__file__).parent.parent / "posts"
    posts_dir.mkdir(exist_ok=True)
    out_path = posts_dir / f"{slug}.md"
    out_path.write_text(final, encoding="utf-8")

    print(f"Relatório salvo em: {out_path}", file=sys.stderr)


if __name__ == "__main__":
    main()
