import type { MetadataRoute } from "next";

export default function robots(): MetadataRoute.Robots {
  return {
    rules: { userAgent: "*", allow: "/", disallow: "/progresso" },
    sitemap: "https://irlandaparabrasileiros.vercel.app/sitemap.xml",
  };
}
