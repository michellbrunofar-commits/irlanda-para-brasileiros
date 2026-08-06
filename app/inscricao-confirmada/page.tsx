import Link from "next/link";
import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "Inscrição confirmada | Irlanda para Brasileiros",
};

export default function InscricaoConfirmadaPage() {
  return (
    <div className="animate-slide-up text-center py-16">
      <p className="text-4xl mb-4">✅</p>
      <h1 className="text-2xl font-extrabold text-gray-900 mb-2">Inscrição confirmada</h1>
      <p className="text-gray-500 mb-8">
        Você vai passar a receber os próximos relatórios por e-mail.
      </p>
      <Link
        href="/"
        className="inline-flex items-center gap-1.5 text-sm font-semibold text-ireland-green hover:text-ireland-orange transition-colors"
      >
        ← Voltar para os relatórios
      </Link>
    </div>
  );
}
