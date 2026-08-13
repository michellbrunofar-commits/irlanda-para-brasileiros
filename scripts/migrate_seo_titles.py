"""
Script one-off: preenche title/description factuais (SEO) nos relatórios
publicados antes do commit ef77f01 (06/08/2026), que introduziu essa regra
só para gerações futuras. Não roda como parte da automação diária.

Título e descrição de cada relatório antigo foram escritos à mão a partir
do "Resumo Executivo (TL;DR)" de cada edição (sem chamada de API — não
depende de ANTHROPIC_API_KEY nem de crédito na conta).

Uso: python3 scripts/migrate_seo_titles.py
"""
import re
import sys
from pathlib import Path

POSTS_DIR = Path(__file__).parent.parent / "posts"

GENERIC_TITLE_RE = re.compile(r"^(Irlanda em Foco|Análise Econômica) — ")

# slug -> (título ≤70 caracteres, descrição 120-155 caracteres)
SEO_FIELDS: dict[str, tuple[str, str]] = {
    "2026-06-02": (
        "Inflação cai em maio na Irlanda com energia mais barata",
        "A inflação irlandesa recuou em maio puxada pela queda no preço da energia, mas a automação por IA já começa a sacudir o mercado de trabalho no país.",
    ),
    "2026-06-04": (
        "Inflação desacelera em maio na Irlanda com energia mais barata",
        "A inflação na Irlanda desacelerou em maio de 2026 puxada pela energia mais barata — mas a melhora pode ser temporária se a guerra EUA-Irã se prolongar.",
    ),
    "2026-06-09": (
        "PIB da Irlanda cai no 1º trimestre por distorção estatística",
        "O PIB irlandês caiu no primeiro trimestre de 2026, mas o recuo é considerado distorção estatística — o risco real é a pressão dos EUA sobre multinacionais no país.",
    ),
    "2026-06-12": (
        "Indústria irlandesa recua após pico artificial de 2025",
        "A produção industrial da Irlanda caiu após um pico artificial em 2025, mas os setores de tecnologia e data centers continuam investindo pesado no país.",
    ),
    "2026-06-15": (
        "OpenText cria 400 vagas de tecnologia em Cork e Galway",
        "A OpenText anunciou 400 novos empregos de tecnologia em Cork e Galway, mesmo com as tarifas dos EUA representando ameaça estrutural ao emprego na Irlanda.",
    ),
    "2026-06-16": (
        "Setor de tecnologia aquece na Irlanda com OpenText e Intel",
        "O setor de tecnologia aquece na Irlanda com novas contratações da OpenText e Intel, mas as tarifas americanas seguem como ameaça estrutural ao emprego.",
    ),
    "2026-06-17": (
        "Desemprego cai a 4,5% na Irlanda, mas inflação sobe a 3,7%",
        "O desemprego na Irlanda caiu para 4,5% com a demanda doméstica crescendo 2,8%, mas a inflação em 3,7% e o custo da moradia seguem pressionando o orçamento.",
    ),
    "2026-06-18": (
        "Emprego bate recorde na Irlanda, mas inflação de 3,5% corrói salário",
        "O emprego na Irlanda atingiu nível histórico com desemprego em 4,9%, mas a inflação de 3,5% e o custo da moradia continuam corroendo o poder de compra real.",
    ),
    "2026-06-19": (
        "Desemprego cai a 4,7% na Irlanda, mas aluguel dispara",
        "A demanda doméstica da Irlanda cresceu 2,8% e o desemprego caiu para 4,7%, mas o aluguel segue disparando e a construção de novas casas segue insuficiente.",
    ),
    "2026-06-20": (
        "Emprego sobe e desemprego cai a 4,7% na Irlanda",
        "A economia irlandesa cresce cerca de 2,8% na demanda doméstica e o desemprego caiu para 4,7%, mas a habitação segue sendo o maior gargalo do país.",
    ),
    "2026-06-21": (
        "Desemprego sobe a 4,9% na Irlanda com cortes no setor de TI",
        "O desemprego na Irlanda subiu levemente para 4,9%, puxado por cortes no setor de TI, enquanto construção e saúde seguem contratando e o aluguel dispara.",
    ),
    "2026-06-22": (
        "Emprego em TI cai forte na Irlanda; desemprego sobe a 4,9%",
        "O mercado de trabalho em TI na Irlanda registra queda expressiva de vagas e o desemprego geral subiu para 4,9%, mesmo com a demanda doméstica crescendo 2,8%.",
    ),
    "2026-06-23": (
        "Inflação de 3,5% e aluguel em alta corroem salário na Irlanda",
        "A economia irlandesa segue crescendo e o emprego está aquecido em setores especializados, mas a inflação de 3,5% e o aluguel em disparada corroem o salário.",
    ),
    "2026-07-01": (
        "FMI pede cautela com gastos públicos na Irlanda",
        "O FMI recomendou cautela com os gastos públicos da Irlanda, enquanto o setor de hostelaria pede socorro e a tecnologia segue no radar das tarifas americanas.",
    ),
    "2026-07-08": (
        "Desemprego chega a 5% na Irlanda com inflação em 3,6%",
        "A economia irlandesa deve crescer cerca de 3% em 2026 e o desemprego chegou a 5%, mas a inflação de 3,6% e a escassez de moradia mantêm o custo de vida alto.",
    ),
    "2026-07-09": (
        "Demissões em massa por IA atingem setor de TI na Irlanda",
        "O setor de TI na Irlanda sofre demissões em massa ligadas à automação por IA, o desemprego geral subiu para 5% e o aluguel segue em alta em todo o país.",
    ),
    "2026-07-10": (
        "Irlanda deve crescer 3% em 2026 com desemprego em 5%",
        "A Irlanda deve crescer 3% em 2026 com desemprego em 5% e inflação de 3,6%, mas a habitação segue sendo o maior desafio para quem vive no país.",
    ),
    "2026-07-13": (
        "PIB da Irlanda deve contrair em 2026 por efeito das multinacionais",
        "O PIB da Irlanda deve contrair em 2026 por fatores ligados às multinacionais, mesmo com a economia interna resiliente e a inflação em queda — a moradia segue cara.",
    ),
    "2026-07-14": (
        "Desemprego sobe a 5,3% na Irlanda com retração em tecnologia",
        "O desemprego na Irlanda subiu para 5,3%, puxado pela retração do setor de tecnologia, enquanto a inflação caiu para 3,4% e o custo da moradia segue muito alto.",
    ),
    "2026-07-15": (
        "Aluguel médio chega a €1.980/mês na Irlanda",
        "O aluguel médio na Irlanda chegou a €1.980 por mês, com desemprego em 5% e inflação em 3,4% — mais casas estão sendo construídas, mas os preços seguem altos.",
    ),
    "2026-07-16": (
        "Desemprego chega a 5% na Irlanda com setor de tech perdendo força",
        "O desemprego na Irlanda chegou a 5% com o setor de tecnologia perdendo força, mas nova oferta de moradia começa a chegar ao mercado, ainda com preços altos.",
    ),
    "2026-07-17": (
        "Setor de TI perde 20 mil vagas na Irlanda em 2026",
        "O setor de TI da Irlanda perdeu 20 mil vagas em 2026, mas construção e saúde compensam parte das perdas; desemprego subiu a 5% e a inflação caiu para 3,4%.",
    ),
    "2026-07-18": (
        "Aluguel começa a estabilizar na Irlanda com inflação em 3,4%",
        "O aluguel na Irlanda começa a estabilizar mesmo ainda caro, enquanto o emprego em tecnologia cai e a inflação recua para 3,4% em meio à desaceleração.",
    ),
    "2026-07-19": (
        "PIB da Irlanda recua 2,5% em desaceleração técnica",
        "O PIB da Irlanda recuou 2,5% numa desaceleração técnica, sem configurar crise — desemprego subiu a 5% e o setor de TI segue em retração, com aluguel alto.",
    ),
    "2026-07-20": (
        "Aluguel médio de €1.980/mês na Irlanda com desemprego perto de 5%",
        "O aluguel médio na Irlanda se mantém em torno de €1.980 por mês e o desemprego chegou perto de 5%, com a economia desacelerando após o boom de 2025.",
    ),
    "2026-07-21": (
        "Só 1.800 imóveis para alugar em toda a Irlanda",
        "A Irlanda tem menos de 1.800 imóveis disponíveis para alugar no país inteiro, crise severa de moradia que coincide com PIB em contração de 2,5%.",
    ),
    "2026-07-22": (
        "PIB da Irlanda cai 3% por efeito técnico do setor farmacêutico",
        "O PIB da Irlanda caiu 3% por um efeito técnico ligado ao setor farmacêutico, mesmo com a economia doméstica crescendo 3,5% — a crise de habitação persiste.",
    ),
    "2026-07-24": (
        "Brasileiros já podem entrar na Irlanda sem visto por 90 dias",
        "Brasileiros agora podem entrar na Irlanda sem visto por até 90 dias, enquanto o desemprego subiu levemente para 4,9% e o setor de tecnologia encolhe.",
    ),
    "2026-07-25": (
        "Desemprego se mantém baixo na Irlanda apesar da desaceleração",
        "O desemprego na Irlanda se mantém baixo, entre 4% e 4,2%, apesar da desaceleração econômica — tecnologia perde vagas enquanto construção e saúde contratam.",
    ),
    "2026-07-26": (
        "Governo da Irlanda investe €9 bilhões em habitação",
        "O governo irlandês vai investir €9 bilhões em habitação, com o mercado de trabalho sólido (desemprego em 4,9%) mas o setor de tecnologia ainda em queda.",
    ),
    "2026-07-27": (
        "IRP vencendo? Extensão vai só até 31 de agosto na Irlanda",
        "Quem tem o IRP vencendo na Irlanda precisa agir logo — a extensão emergencial vale só até 31 de agosto, enquanto a economia segue estável e a inflação cai.",
    ),
    "2026-07-28": (
        "Desemprego chega a 5% na Irlanda liderado por cortes em tecnologia",
        "O desemprego na Irlanda chegou a 5%, liderado por cortes no setor de tecnologia, mesmo com a demanda doméstica ainda crescendo 2,8% no ano.",
    ),
    "2026-07-29": (
        "Irlanda deve crescer cerca de 3% em 2026 com inflação em queda",
        "A economia irlandesa deve crescer cerca de 3% em 2026 com a inflação em queda, mercado de trabalho saudável e oportunidades em tecnologia e construção.",
    ),
    "2026-07-30": (
        "Inflação da habitação chega a 7,3% na Irlanda",
        "A inflação no setor de habitação da Irlanda chegou a 7,3%, pressionando o orçamento das famílias mesmo com a demanda doméstica crescendo 3,5%.",
    ),
    "2026-07-31": (
        "Desemprego na Irlanda chega ao maior nível em 3 anos",
        "O desemprego na Irlanda chegou a 5%, o maior nível em três anos, puxado pelo esfriamento do setor de tecnologia mesmo com a economia crescendo 3,5%.",
    ),
    "2026-08-01": (
        "Aluguel médio passa de €2.000/mês na Irlanda",
        "O aluguel médio nacional na Irlanda passou de €2.000 por mês, com salários crescendo só 3% ao ano — abaixo da inflação de 3,6% que pressiona o custo de vida.",
    ),
    "2026-08-02": (
        "Apenas 1.777 imóveis disponíveis para alugar em toda a Irlanda",
        "A Irlanda tem apenas 1.777 imóveis disponíveis para alugar no país inteiro — pior nível histórico —, com o PIB em queda de 2,5% e a inflação da habitação em 7%.",
    ),
    "2026-08-03": (
        "Setor de tecnologia soma 20 mil demissões na Irlanda",
        "O setor de tecnologia da Irlanda soma 20 mil demissões, com o desemprego geral subindo levemente para 5% e a moradia cada vez mais cara para os imigrantes.",
    ),
    "2026-08-04": (
        "Aluguel em Dublin sobe 8% e desemprego em tech chega a 5%",
        "Aluguel em Dublin sobe 8% e chega a €1.520/mês para um apartamento de um quarto, enquanto o desemprego na Irlanda avança para 5% com queda de vagas em tecnologia.",
    ),
}


def yaml_quote(value: str) -> str:
    return '"' + value.replace('"', '\\"') + '"'


def parse_frontmatter(raw: str) -> tuple[dict, str]:
    parts = raw.split("---\n", 2)
    if len(parts) < 3:
        raise ValueError("frontmatter mal formado")
    fm_lines = parts[1].strip("\n").split("\n")
    fm = {}
    for line in fm_lines:
        if ":" not in line:
            continue
        key, _, value = line.partition(":")
        fm[key.strip()] = value.strip().strip('"')
    body = parts[2]
    return fm, body


def needs_migration(fm: dict) -> bool:
    title = fm.get("title", "")
    description = fm.get("description", "")
    return not description or bool(GENERIC_TITLE_RE.match(title))


def extract_first_bullet_headline(body: str) -> str | None:
    match = re.search(r"## 🇮🇪 Irlanda\n+- \*\*(.+?)\*\*", body)
    return match.group(1).strip() if match else None


def write_frontmatter(path: Path, fm: dict, body: str, titulo: str, descricao: str) -> None:
    new_frontmatter = (
        "---\n"
        f"title: {yaml_quote(titulo)}\n"
        f"description: {yaml_quote(descricao)}\n"
        f"date: {fm['date']}\n"
        "---\n"
    )
    path.write_text(new_frontmatter + body, encoding="utf-8")


def main():
    paths = sorted(POSTS_DIR.glob("*.md"))
    migrated = 0
    seen_titles: set[str] = set()

    for path in paths:
        slug = path.stem
        raw = path.read_text(encoding="utf-8")
        fm, body = parse_frontmatter(raw)

        if not needs_migration(fm):
            continue

        if slug in SEO_FIELDS:
            titulo, descricao = SEO_FIELDS[slug]
        else:
            headline = extract_first_bullet_headline(body)
            if not headline:
                print(f"AVISO: {path.name} sem entrada em SEO_FIELDS e sem bullet de Irlanda, pulando.", file=sys.stderr)
                continue
            titulo = headline[:70]
            descricao = fm.get("description", "")

        if titulo in seen_titles:
            print(f"AVISO: título duplicado gerado para {path.name}: {titulo}", file=sys.stderr)
        seen_titles.add(titulo)

        write_frontmatter(path, fm, body, titulo, descricao)
        migrated += 1
        print(f"{path.name}: {titulo}")

    print(f"\n{migrated}/{len(paths)} relatórios migrados.", file=sys.stderr)


if __name__ == "__main__":
    main()
