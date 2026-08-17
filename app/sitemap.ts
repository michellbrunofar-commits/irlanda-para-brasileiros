import type { MetadataRoute } from "next";
import { getAllPostsMeta } from "@/lib/posts";

const BASE = "https://irlandaparabrasileiros.vercel.app";

export default function sitemap(): MetadataRoute.Sitemap {
  const posts = getAllPostsMeta();
  return [
    { url: BASE, changeFrequency: "daily", priority: 1 },
    { url: `${BASE}/sobre`, changeFrequency: "monthly", priority: 0.5 },
    { url: `${BASE}/estudar`, changeFrequency: "monthly", priority: 0.5 },
    { url: `${BASE}/recomendacoes`, changeFrequency: "monthly", priority: 0.5 },
    ...posts.map((p) => ({
      url: `${BASE}/relatorio/${p.slug}`,
      lastModified: new Date(p.date),
      changeFrequency: "monthly" as const,
      priority: 0.7,
    })),
  ];
}
