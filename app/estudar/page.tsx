import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "Como estudar na Irlanda | Irlanda para Brasileiros",
  description:
    "O caminho de curso de inglês a mestrado na Irlanda para brasileiros: vistos, Stamp 1G e como a Go Sem Fronteiras pode ajudar.",
};

export default function EstudarPage() {
  return (
    <div className="animate-slide-up">
      <h1 className="text-3xl font-extrabold text-gray-900 leading-tight mb-2">
        Como estudar na Irlanda
      </h1>
      <p className="text-gray-500 mb-10 text-base">
        O caminho mais comum para brasileiros que querem estudar e trabalhar na Irlanda.
      </p>

      <div className="space-y-6">
        <div className="report-card cursor-default hover:translate-y-0 hover:shadow-none">
          <h2 className="text-lg font-bold text-gray-900 mb-2">1. Curso de inglês (opcional)</h2>
          <p className="text-gray-700 leading-relaxed">
            Quem ainda não tem o nível de inglês exigido (geralmente IELTS ou TOEFL) costuma
            começar por um curso de inglês na Irlanda, o que já permite entrar no país com o
            visto de estudante Stamp 2.
          </p>
        </div>

        <div className="report-card cursor-default hover:translate-y-0 hover:shadow-none">
          <h2 className="text-lg font-bold text-gray-900 mb-2">2. Mestrado numa universidade irlandesa</h2>
          <p className="text-gray-700 leading-relaxed">
            Um mestrado de tempo integral numa universidade reconhecida dá acesso ao Stamp 1G
            depois de formado — até 24 meses de autorização de trabalho em tempo integral,
            sem precisar de patrocínio de empregador nesse período.
          </p>
        </div>

        <div className="report-card cursor-default hover:translate-y-0 hover:shadow-none">
          <h2 className="text-lg font-bold text-gray-900 mb-2">3. Bolsas e financiamento</h2>
          <p className="text-gray-700 leading-relaxed">
            Programas como a bolsa GOI-IES do governo irlandês exigem que a candidatura ao curso
            já esteja feita antes da janela de bolsas abrir — por isso o calendário do processo
            importa tanto quanto a escolha do curso.
          </p>
        </div>
      </div>

      <div className="mt-10 rounded-2xl border border-ireland-green/20 bg-ireland-green-light px-6 py-6">
        <p className="text-sm font-bold text-ireland-green uppercase tracking-wide mb-2">
          Quer ajuda com o seu caso?
        </p>
        <p className="text-gray-700 leading-relaxed mb-4">
          A Go Sem Fronteiras ajuda brasileiros a montar a candidatura para universidades
          irlandesas, do curso de inglês ao mestrado. Diagnóstico gratuito de 30 minutos.
        </p>
        <a
          href="https://gosemfronteiras.vercel.app/bio"
          className="inline-flex items-center gap-1.5 text-sm font-semibold text-ireland-green hover:text-ireland-orange transition-colors"
        >
          Falar com a Go Sem Fronteiras
          <span aria-hidden="true">→</span>
        </a>
      </div>
    </div>
  );
}
