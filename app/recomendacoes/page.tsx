import type { Metadata } from "next";
import { AFFILIATE_LINKS } from "@/lib/affiliates";

export const metadata: Metadata = {
  title: "Recomendações | Irlanda para Brasileiros",
  description:
    "Remessa, banco digital, seguro de visto e eSIM — as ferramentas que eu realmente uso pra viver na Irlanda, com transparência total sobre comissão.",
};

const CATEGORIAS = ["Remessa", "Banco", "Seguro", "Telefonia"] as const;

export default function RecomendacoesPage() {
  return (
    <div className="animate-slide-up">
      <h1 className="text-3xl font-extrabold text-gray-900 leading-tight mb-2">Recomendações</h1>
      <p className="text-gray-500 mb-6 text-base">
        As ferramentas que eu mesmo uso ou usaria pra viver na Irlanda — sem enrolação.
      </p>

      <div className="rounded-2xl border border-ireland-orange/20 bg-ireland-orange/5 px-5 py-4 mb-10">
        <p className="text-sm text-gray-700 leading-relaxed">
          <strong>Transparência:</strong> alguns links abaixo são (ou vão ser) de afiliado — se
          você usar, eu posso ganhar uma comissão, sem custo extra pra você. Só recomendo o que
          eu mesmo usaria, comissão ou não.
        </p>
      </div>

      <div className="space-y-10">
        {CATEGORIAS.map((categoria) => {
          const items = AFFILIATE_LINKS.filter((l) => l.categoria === categoria);
          if (items.length === 0) return null;
          return (
            <div key={categoria}>
              <h2 className="text-xs font-semibold uppercase tracking-widest text-gray-400 mb-3">
                {categoria}
              </h2>
              <div className="space-y-4">
                {items.map((link) => (
                  <div key={link.slug} className="report-card cursor-default hover:translate-y-0 hover:shadow-none">
                    <div className="flex items-start justify-between gap-3 mb-1">
                      <h3 className="text-base font-bold text-gray-900">{link.nome}</h3>
                      {link.pending && (
                        <span className="shrink-0 badge bg-gray-100 text-gray-500">
                          Em breve — ainda não é link de afiliado
                        </span>
                      )}
                    </div>
                    <p className="text-gray-700 text-sm leading-relaxed mb-3">{link.descricao}</p>
                    <a
                      href={link.url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="inline-flex items-center gap-1.5 text-sm font-semibold text-ireland-green hover:text-ireland-orange transition-colors"
                    >
                      Conhecer {link.nome}
                      <span aria-hidden="true">→</span>
                    </a>
                  </div>
                ))}
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
