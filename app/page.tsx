import Link from "next/link";
import { getAllPostsMeta } from "@/lib/posts";

export default function Home() {
  const posts = getAllPostsMeta();
  const latest = posts[0];
  const older = posts.slice(1);

  return (
    <div className="animate-slide-up">

      {/* Intro pill */}
      <div className="inline-flex items-center gap-2 bg-ireland-green-light text-ireland-green text-xs font-semibold px-3 py-1.5 rounded-full mb-6">
        <span className="w-2 h-2 rounded-full bg-ireland-green animate-pulse" />
        Atualizado toda semana
      </div>

      <h2 className="text-3xl font-extrabold text-gray-900 leading-tight mb-2">
        Seu briefing econômico
      </h2>
      <p className="text-gray-500 mb-10 text-base">
        O que está acontecendo na Irlanda — em português, filtrado para quem veio do Brasil.
      </p>

      {posts.length === 0 ? (
        <div className="text-center py-20 text-gray-400">
          Nenhum relatório publicado ainda.
        </div>
      ) : (
        <div className="space-y-4">

          {/* Latest report — destaque */}
          {latest && (
            <Link href={`/relatorio/${latest.slug}`} className="block group">
              <div className="report-card bg-gradient-to-br from-white to-ireland-green-light border-ireland-green/30 overflow-hidden">
                {/* Thumbnail */}
                <div className="relative -mx-6 -mt-6 mb-5 h-36 overflow-hidden">
                  {/* eslint-disable-next-line @next/next/no-img-element */}
                  <img
                    src={`https://picsum.photos/seed/${latest.slug}-card/700/280`}
                    alt=""
                    aria-hidden="true"
                    className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-500"
                  />
                  <div className="absolute inset-0 bg-gradient-to-b from-transparent to-white/80" />
                </div>
                <div className="flex items-start justify-between gap-4">
                  <div className="flex-1">
                    <div className="flex items-center gap-2 mb-3">
                      <span className="badge bg-ireland-green text-white">
                        Mais recente
                      </span>
                      <span className="badge bg-ireland-orange/10 text-ireland-orange">
                        {formatDate(latest.date)}
                      </span>
                    </div>
                    <h3 className="text-xl font-bold text-gray-900 leading-snug mb-2">
                      {latest.title}
                    </h3>
                    <span className="text-ireland-green font-semibold text-sm group-hover:gap-2 flex items-center gap-1 transition-all">
                      Ler relatório <span className="group-hover:translate-x-1 transition-transform inline-block">→</span>
                    </span>
                  </div>
                </div>
              </div>
            </Link>
          )}

          {/* Older reports */}
          {older.length > 0 && (
            <>
              <h3 className="text-xs font-semibold uppercase tracking-widest text-gray-400 pt-4 pb-1">
                Relatórios anteriores
              </h3>
              {older.map((post) => (
                <Link key={post.slug} href={`/relatorio/${post.slug}`} className="block group">
                  <div className="report-card">
                    <div className="flex items-center justify-between gap-4">
                      <div>
                        <time className="text-xs font-semibold text-ireland-orange uppercase tracking-wide">
                          {formatDate(post.date)}
                        </time>
                        <h3 className="mt-0.5 text-base font-semibold text-gray-800 group-hover:text-ireland-green transition-colors">
                          {post.title}
                        </h3>
                      </div>
                      <span className="text-gray-300 group-hover:text-ireland-green transition-colors text-xl">→</span>
                    </div>
                  </div>
                </Link>
              ))}
            </>
          )}
        </div>
      )}
    </div>
  );
}

function formatDate(raw: string): string {
  const d = new Date(raw + "T12:00:00Z");
  return d.toLocaleDateString("pt-BR", {
    day: "2-digit",
    month: "long",
    year: "numeric",
  });
}
