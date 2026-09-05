import { getPostBySlug, getAllEnglishPostSlugs } from "@/lib/posts";
import Link from "next/link";
import { notFound } from "next/navigation";

export async function generateStaticParams() {
  return getAllEnglishPostSlugs().map((slug) => ({ slug }));
}

export async function generateMetadata({
  params,
}: {
  params: Promise<{ slug: string }>;
}) {
  const { slug } = await params;
  const post = await getPostBySlug(slug, "en").catch(() => null);
  if (!post) return {};
  return {
    title: post.title + " | Ireland for Brazilians",
    description: post.description || undefined,
    alternates: {
      canonical: `https://irlandaparabrasileiros.vercel.app/relatorio/${slug}/en`,
      languages: {
        "pt-BR": `https://irlandaparabrasileiros.vercel.app/relatorio/${slug}`,
        "en": `https://irlandaparabrasileiros.vercel.app/relatorio/${slug}/en`,
      },
    },
    openGraph: {
      title: post.title,
      description: post.description || undefined,
      type: "article",
      publishedTime: post.date,
      locale: "en_IE",
      images: ["/og-image.png"],
    },
  };
}

export default async function EnglishReportPage({
  params,
}: {
  params: Promise<{ slug: string }>;
}) {
  const { slug } = await params;

  let post;
  try {
    post = await getPostBySlug(slug, "en");
  } catch {
    notFound();
  }

  return (
    <div className="animate-slide-up">
      {/* Nav */}
      <div className="flex items-center justify-between mb-8">
        <Link
          href="/"
          className="inline-flex items-center gap-1.5 text-sm text-gray-400 hover:text-ireland-green transition-colors font-medium"
        >
          ← All reports
        </Link>
        <Link
          href={`/relatorio/${slug}`}
          className="inline-flex items-center gap-1.5 text-sm font-semibold text-ireland-green hover:text-ireland-green-dark transition-colors"
        >
          🇧🇷 Ler em português
        </Link>
      </div>

      {/* Masthead da edição */}
      <div className="relative bg-hero-gradient text-white rounded-2xl px-6 py-8 mb-8 overflow-hidden shadow-lg">
        <div className="absolute right-4 top-4 text-7xl opacity-10 select-none">🇮🇪</div>
        <div className="absolute right-20 bottom-2 text-4xl opacity-10 select-none">🇧🇷</div>

        <div className="relative">
          <div className="flex items-center flex-wrap gap-2 mb-3">
            <span className="badge bg-white/20 text-white/90 backdrop-blur-sm">
              Edition
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
            Automated research and writing with AI support · no human review before publishing. Translated from the original Portuguese edition.
          </p>
        </div>

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
        This is a daily newsletter about Ireland written in Portuguese for Brazilian immigrants —{" "}
        <Link href={`/relatorio/${slug}`} className="text-ireland-green hover:underline">
          read the original edition
        </Link>
        .
      </p>
    </div>
  );
}

function formatDate(raw: string): string {
  const d = new Date(raw + "T12:00:00Z");
  return d.toLocaleDateString("en-IE", {
    day: "2-digit",
    month: "long",
    year: "numeric",
  });
}
