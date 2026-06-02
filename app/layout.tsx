import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Irlanda para Brasileiros",
  description:
    "Análise econômica semanal da Irlanda com foco em imigrantes brasileiros.",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="pt-BR">
      <body className="bg-gray-50 text-gray-900">

        {/* Hero Header */}
        <header className="bg-hero-gradient text-white shadow-md">
          <div className="mx-auto max-w-3xl px-4 py-8">
            {/* Flags */}
            <div className="flex items-center gap-2 mb-3">
              <span className="text-2xl drop-shadow">🇮🇪</span>
              <div className="h-0.5 w-6 bg-white/30 rounded" />
              <span className="text-2xl drop-shadow">🇧🇷</span>
            </div>

            <a href="/" className="group block">
              <h1 className="text-2xl font-extrabold tracking-tight text-white group-hover:text-ireland-orange transition-colors">
                Irlanda para Brasileiros
              </h1>
              <p className="mt-1 text-sm text-white/75 font-medium">
                Análise econômica semanal · emprego, moradia e imigração
              </p>
            </a>

            {/* Decorative stripe — Brazil colors */}
            <div className="mt-6 flex h-1.5 rounded-full overflow-hidden gap-px">
              <div className="flex-1 bg-brazil-green" />
              <div className="flex-1 bg-brazil-yellow" />
              <div className="flex-1 bg-brazil-blue" />
              <div className="flex-1 bg-white/40" />
              <div className="flex-1 bg-ireland-orange" />
            </div>
          </div>
        </header>

        <main className="mx-auto max-w-3xl px-4 py-10 animate-fade-in">
          {children}
        </main>

        <footer className="mt-16 border-t border-gray-200 bg-white">
          <div className="mx-auto max-w-3xl px-4 py-6 flex items-center justify-between text-sm text-gray-400">
            <span className="flex items-center gap-1.5">
              🇮🇪 <span className="font-medium text-ireland-green">Irlanda para Brasileiros</span>
            </span>
            <span>Gerado com Claude AI · News API</span>
          </div>
        </footer>

      </body>
    </html>
  );
}
