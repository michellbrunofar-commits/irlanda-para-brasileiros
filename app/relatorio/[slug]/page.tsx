import { getPostBySlug, getAllPostSlugs } from "@/lib/posts";
import Link from "next/link";
import { notFound } from "next/navigation";
import NewsletterForm from "@/components/NewsletterForm";

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
  return {
    title: post.title + " | Irlanda para Brasileiros",
    description: post.description || undefined,
    alternates: {
      canonical: `https://irlandaparabrasileiros.vercel.app/relatorio/${slug}`,
    },
    openGraph: {
      title: post.title,
      description: post.description || undefined,
      type: "article",
      publishedTime: post.date,
      locale: "pt_BR",
      images: ["/og-image.png"],
    },
  };
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

      {/* Masthead da edição */}
      <div className="relative bg-hero-gradient text-white rounded-2xl px-6 py-8 mb-8 overflow-hidden shadow-lg">
        {/* Background decoration */}
        <div className="absolute right-4 top-4 text-7xl opacity-10 select-none">🇮🇪</div>
        <div className="absolute right-20 bottom-2 text-4xl opacity-10 select-none">🇧🇷</div>

        <div className="relative">
          <div className="flex items-center flex-wrap gap-2 mb-3">
            <span className="badge bg-white/20 text-white/90 backdrop-blur-sm">
              Edição
            </span>
            <span className="badge bg-ireland-orange/80 text-white">
              {formatDate(post.date)}
            </span>
          </div>
          <h1 className="text-2xl font-extrabold leading-tight">{post.title}</h1>
          {post.description && (
            <p className="mt-2 text-sm text-white/80 leading-relaxed max-w-md">
              {post.description}
            </p>
          )}
          <p className="mt-4 text-xs text-white/60">
            Pesquisa e redação 100% automáticas com apoio de IA · sem revisão humana antes de publicar
          </p>
        </div>

        {/* Brazil stripe — único elemento decorativo do cabeçalho, sem repetir mais abaixo */}
        <div className="absolute bottom-0 left-0 right-0 flex h-1.5">
          <div className="flex-1 bg-brazil-green" />
          <div className="flex-1 bg-brazil-yellow" />
          <div className="flex-1 bg-brazil-blue" />
        </div>
      </div>

      {/* Report content */}
      <div
        className="report-prose prose prose-gray sm:prose-lg max-w-none
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

      <p className="mt-8 text-sm text-gray-400 text-center">
        Até a próxima edição — só publicamos quando tem novidade de verdade.
      </p>

      {/* Captura de e-mail */}
      <div className="mt-10">
        <NewsletterForm id="fim" />
      </div>
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
