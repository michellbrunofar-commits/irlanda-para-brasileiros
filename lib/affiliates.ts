export interface AffiliateLink {
  slug: string;
  nome: string;
  categoria: "Remessa" | "Banco" | "Seguro" | "Telefonia";
  descricao: string;
  url: string;
  /** true = link institucional normal, ainda não é link de afiliado de verdade */
  pending: boolean;
}

export const AFFILIATE_LINKS: AffiliateLink[] = [
  {
    slug: "wise",
    nome: "Wise",
    categoria: "Remessa",
    descricao:
      "A que eu mesmo uso pra mandar dinheiro entre Irlanda e Brasil — taxa de câmbio real, sem o spread escondido dos bancos tradicionais.",
    url: "https://wise.com/pt-br/",
    pending: true,
  },
  {
    slug: "remitly",
    nome: "Remitly",
    categoria: "Remessa",
    descricao:
      "Alternativa à Wise, útil pra comparar taxa antes de mandar uma remessa maior — vale checar as duas no dia.",
    url: "https://www.remitly.com/",
    pending: true,
  },
  {
    slug: "revolut",
    nome: "Revolut",
    categoria: "Banco",
    descricao:
      "Conta digital que dá pra abrir do Brasil antes mesmo de embarcar — resolve o cartão pros primeiros dias, antes de ter comprovante de endereço pra um banco irlandês.",
    url: "https://www.revolut.com/",
    pending: true,
  },
  {
    slug: "seguro-saude-viagem",
    nome: "Seguro de saúde e viagem",
    categoria: "Seguro",
    descricao:
      "Exigido na candidatura do visto de estudante — precisa cobrir o período todo do curso, sem lacunas entre chegada e início das aulas.",
    url: "https://safetywing.com/",
    pending: true,
  },
  {
    slug: "esim",
    nome: "eSIM de viagem",
    categoria: "Telefonia",
    descricao:
      "Pra ter internet funcionando assim que o avião pousa, antes de conseguir um chip irlandês — não precisa trocar chip físico nem depender do wifi do aeroporto.",
    url: "https://www.holafly.com/pt/",
    pending: true,
  },
];
