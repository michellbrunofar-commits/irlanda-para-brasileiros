import fs from "fs";
import path from "path";
import matter from "gray-matter";
import { remark } from "remark";
import html from "remark-html";

const postsDir = path.join(process.cwd(), "posts");

export interface PostMeta {
  slug: string;
  title: string;
  date: string;
}

export interface Post extends PostMeta {
  contentHtml: string;
}

export function getAllPostSlugs(): string[] {
  if (!fs.existsSync(postsDir)) return [];
  return fs
    .readdirSync(postsDir)
    .filter((f) => f.endsWith(".md"))
    .map((f) => f.replace(/\.md$/, ""))
    .sort()
    .reverse();
}

export function getAllPostsMeta(): PostMeta[] {
  return getAllPostSlugs().map((slug) => {
    const { data } = matter(fs.readFileSync(path.join(postsDir, `${slug}.md`), "utf8"));
    const rawDate = data.date;
    const date =
      rawDate instanceof Date
        ? rawDate.toISOString().slice(0, 10)
        : rawDate != null
        ? String(rawDate)
        : slug;
    return { slug, title: data.title ?? slug, date };
  });
}

export async function getPostBySlug(slug: string): Promise<Post> {
  const raw = fs.readFileSync(path.join(postsDir, `${slug}.md`), "utf8");
  const { data, content } = matter(raw);
  const processed = await remark().use(html).process(content);
  return {
    slug,
    title: data.title ?? slug,
    date:
      data.date instanceof Date
        ? data.date.toISOString().slice(0, 10)
        : data.date != null
        ? String(data.date)
        : slug,
    contentHtml: processed.toString(),
  };
}
