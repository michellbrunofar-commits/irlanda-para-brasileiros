import type { Metadata } from "next";
import progressData from "@/data/progress.json";

export const metadata: Metadata = { robots: { index: false, follow: false } };
export const dynamic = "force-static";

const STATUS_LABEL: Record<string, string> = {
  not_started: "Não iniciado",
  in_progress: "Em andamento",
  approved: "Aprovado pelo crítico",
  escalated: "Travou no teto de rodadas",
};

const STATUS_COLOR: Record<string, string> = {
  not_started: "bg-gray-100 text-gray-500",
  in_progress: "bg-ireland-orange/10 text-ireland-orange",
  approved: "bg-ireland-green-light text-ireland-green",
  escalated: "bg-red-50 text-red-600",
};

export default function ProgressPage() {
  const data = progressData as {
    updated_at: string;
    summary: string;
    pieces: {
      id: string;
      name: string;
      description: string;
      status: string;
      round: number;
      max_rounds: number;
      note: string | null;
    }[];
  };

  return (
    <div className="animate-slide-up">
      <h1 className="text-2xl font-extrabold text-gray-900 mb-1">Progresso da reforma</h1>
      <p className="text-sm text-gray-400 mb-6">
        Atualizado em {new Date(data.updated_at).toLocaleString("pt-BR", { dateStyle: "short", timeStyle: "short" })}
      </p>

      <div className="rounded-xl bg-ireland-green-light border border-ireland-green/20 px-5 py-4 mb-8">
        <p className="text-sm text-gray-700">{data.summary}</p>
      </div>

      <div className="space-y-3">
        {data.pieces.map((p) => (
          <div key={p.id} className="report-card cursor-default hover:translate-y-0 hover:shadow-none">
            <div className="flex items-start justify-between gap-3">
              <div>
                <h2 className="font-bold text-gray-900">{p.name}</h2>
                <p className="text-sm text-gray-500 mt-0.5">{p.description}</p>
              </div>
              <span className={`shrink-0 badge ${STATUS_COLOR[p.status] ?? "bg-gray-100 text-gray-500"}`}>
                {STATUS_LABEL[p.status] ?? p.status}
              </span>
            </div>
            {p.status === "in_progress" && (
              <p className="mt-2 text-xs text-gray-400">
                Rodada {p.round} de {p.max_rounds}
              </p>
            )}
            {p.note && <p className="mt-2 text-sm text-gray-600">{p.note}</p>}
          </div>
        ))}
      </div>
    </div>
  );
}
