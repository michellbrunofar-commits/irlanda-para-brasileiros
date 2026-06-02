import { getPostBySlug, getAllPostSlugs } from "@/lib/posts";
import Link from "next/link";
import { notFound } from "next/navigation";

export async function generateStaticParams() {
  return getAllPostSlugs().map((slug) => ({ slug }));
}

export async function generateMetadata({
  params,
}: {
  params: Promise<{ slug: string }>;
}) {
  const { slug } = await params;
  const post = await getPostBySlug(slug).catch(() => null);
  if (!post) return {};
  return { title: post.title + " | Irlanda para Brasileiros" };
}

export default async function ReportPage({
  params,
}: {
  params: Promise<{ slug: string }>;
}) {
  const { slug } = await params;

  let post;
  try {
    post = await getPostBySlug(slug);
  } catch {
    notFound();
  }

  return (
    <div className="animate-slide-up">
      {/* Nav */}
      <Link
        href="/"
        className="inline-flex items-center gap-1.5 text-sm text-gray-400 hover:text-ireland-green transition-colors mb-8 font-medium"
      >
        ← Todos os relatórios
      </Link>

      {/* Report header card */}
      <div className="relative bg-hero-gradient text-white rounded-2xl px-6 py-8 mb-8 overflow-hidden shadow-lg">
        {/* Background decoration */}
        <div className="absolute right-4 top-4 text-7xl opacity-10 select-none">🇮🇪</div>
        <div className="absolute right-20 bottom-2 text-4xl opacity-10 select-none">🇧🇷</div>

        <div className="relative">
          <div className="flex items-center gap-2 mb-3">
            <span className="badge bg-white/20 text-white/90 backdrop-blur-sm">
              Análise Semanal
            </span>
            <span className="badge bg-ireland-orange/80 text-white">
              {formatDate(post.date)}
            </span>
          </div>
          <h1 className="text-2xl font-extrabold leading-tight">{post.title}</h1>
        </div>

        {/* Brazil stripe */}
        <div className="absolute bottom-0 left-0 right-0 flex h-1">
          <div className="flex-1 bg-brazil-green" />
          <div className="flex-1 bg-brazil-yellow" />
          <div className="flex-1 bg-brazil-blue" />
        </div>
      </div>

      {/* Report content */}
      <div
        className="report-prose prose prose-gray max-w-none
          prose-headings:font-bold
          prose-h1:hidden
          prose-h2:text-xl prose-h2:text-gray-900
          prose-h3:text-base
          prose-a:text-ireland-green prose-a:no-underline hover:prose-a:underline
          prose-strong:text-gray-900
          prose-li:text-gray-700
          prose-p:text-gray-700 prose-p:leading-relaxed"
        dangerouslySetInnerHTML={{ __html: post.contentHtml }}
      />
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
