import type { Metadata } from "next";
import { WHATSAPP_URL } from "@/lib/contact";

export const metadata: Metadata = {
  title: "Sobre | Irlanda para Brasileiros",
  description: "Como o Irlanda em Foco é produzido, de onde vêm as notícias e como corrigimos erros.",
};

export default function SobrePage() {
  return (
    <div className="animate-slide-up">
      <h1 className="text-3xl font-extrabold text-gray-900 leading-tight mb-2">Sobre</h1>
      <p className="text-gray-500 mb-10 text-base">
        Como o Irlanda em Foco é produzido, de onde vêm as notícias e o que fazer se algo estiver errado.
      </p>

      <div className="space-y-6">
        <div className="report-card cursor-default hover:translate-y-0 hover:shadow-none">
          <h2 className="text-lg font-bold text-gray-900 mb-2">Quem faz</h2>
          <p className="text-gray-700 leading-relaxed">
            O Irlanda para Brasileiros é um projeto do Michell Lago, brasileiro que mora em
            Dublin. O objetivo é filtrar o que realmente importa da economia irlandesa — emprego,
            aluguel, custo de vida, imigração — pra quem veio do Brasil.
          </p>
        </div>

        <div className="report-card cursor-default hover:translate-y-0 hover:shadow-none">
          <h2 className="text-lg font-bold text-gray-900 mb-2">Como cada edição é feita</h2>
          <p className="text-gray-700 leading-relaxed mb-3">
            O processo é <strong>100% automático, sem revisão humana antes de publicar</strong>.
            Todo dia, um sistema busca notícias recentes sobre a Irlanda e a economia mundial
            (via NewsData.io), lê o texto completo dos artigos originais, e usa um modelo de IA
            (Claude, da Anthropic) pra selecionar e traduzir o que é genuinamente relevante e
            verificável.
          </p>
          <p className="text-gray-700 leading-relaxed mb-3">
            Regras que o sistema segue em toda edição:
          </p>
          <ul className="space-y-2 text-gray-700">
            <li className="flex items-start gap-2">
              <span className="text-ireland-green mt-0.5">✓</span>
              <span>Só entra o que tem número verificável na fonte — sem "subiu muito" sem dizer quanto</span>
            </li>
            <li className="flex items-start gap-2">
              <span className="text-ireland-green mt-0.5">✓</span>
              <span>Plano/projeto de empresa nunca vira manchete de fato já acontecido</span>
            </li>
            <li className="flex items-start gap-2">
              <span className="text-ireland-green mt-0.5">✓</span>
              <span>Toda fonte é um link direto pro artigo original — dá pra conferir com 1 clique</span>
            </li>
            <li className="flex items-start gap-2">
              <span className="text-ireland-green mt-0.5">✓</span>
              <span>Se não houver notícia genuinamente nova e relevante, não sai edição naquele dia</span>
            </li>
            <li className="flex items-start gap-2">
              <span className="text-ireland-green mt-0.5">✓</span>
              <span>Nunca conecta política monetária de outro país (ex.: Fed dos EUA) a custos na Irlanda sem uma fonte específica sobre a zona do euro</span>
            </li>
          </ul>
        </div>

        <div className="report-card cursor-default hover:translate-y-0 hover:shadow-none">
          <h2 className="text-lg font-bold text-gray-900 mb-2">Achou um erro?</h2>
          <p className="text-gray-700 leading-relaxed">
            Como não há revisão humana antes de publicar, erros podem acontecer. Se você notar
            algo errado numa edição, manda mensagem no{" "}
            <a
              href={WHATSAPP_URL}
              target="_blank"
              rel="noopener noreferrer"
              className="text-ireland-green font-semibold hover:underline"
            >
              WhatsApp
            </a>{" "}
            — a edição é corrigida assim que possível.
          </p>
        </div>
      </div>
    </div>
  );
}
