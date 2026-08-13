"use client";

import { useState, type FormEvent } from "react";
import { WHATSAPP_URL } from "@/lib/contact";

export default function NewsletterForm({ id }: { id: string }) {
  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [status, setStatus] = useState<"idle" | "loading" | "done" | "error">("idle");
  const [errorMsg, setErrorMsg] = useState("");

  async function handleSubmit(e: FormEvent) {
    e.preventDefault();
    setStatus("loading");
    setErrorMsg("");

    try {
      const res = await fetch("/api/newsletter", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ name, email }),
      });
      const data = await res.json();
      if (!res.ok) {
        setErrorMsg(data.error || "Não foi possível concluir a inscrição.");
        setStatus("error");
        return;
      }
      setStatus("done");
    } catch {
      setErrorMsg("Erro de conexão. Tente novamente.");
      setStatus("error");
    }
  }

  if (status === "done") {
    return (
      <div className="rounded-2xl border border-ireland-green/20 bg-ireland-green-light px-6 py-6 text-center">
        <p className="font-semibold text-ireland-green">Quase lá!</p>
        <p className="text-sm text-gray-600 mt-1">
          Enviamos um e-mail de confirmação — clique no link para começar a receber os relatórios.
        </p>
      </div>
    );
  }

  return (
    <div className="rounded-2xl border border-ireland-green/20 bg-ireland-green-light px-6 py-6">
      <p className="text-sm font-bold text-ireland-green uppercase tracking-wide mb-2">
        Receba a análise no seu e-mail
      </p>
      <p className="text-gray-700 text-sm mb-4">
        Sem precisar voltar ao site. Cancele quando quiser.
      </p>
      <form onSubmit={handleSubmit} className="flex flex-col sm:flex-row gap-2">
        <label htmlFor={`${id}-name`} className="sr-only">Nome</label>
        <input
          id={`${id}-name`}
          type="text"
          placeholder="Nome"
          value={name}
          onChange={(e) => setName(e.target.value)}
          className="flex-1 rounded-lg border border-gray-200 px-3 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-ireland-green"
        />
        <label htmlFor={`${id}-email`} className="sr-only">E-mail</label>
        <input
          id={`${id}-email`}
          type="email"
          required
          placeholder="seu@email.com"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          className="flex-1 rounded-lg border border-gray-200 px-3 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-ireland-green"
        />
        <button
          type="submit"
          disabled={status === "loading"}
          className="rounded-lg bg-ireland-green px-4 py-2.5 text-sm font-semibold text-white hover:bg-ireland-green/90 transition-colors disabled:opacity-60"
        >
          {status === "loading" ? "Enviando..." : "Inscrever"}
        </button>
      </form>
      {status === "error" && (
        <p className="text-sm text-red-600 mt-2">{errorMsg}</p>
      )}
      <a
        href={WHATSAPP_URL}
        target="_blank"
        rel="noopener noreferrer"
        className="inline-block mt-3 text-xs font-semibold text-gray-500 hover:text-ireland-green transition-colors"
      >
        Prefere WhatsApp? Fale direto por lá →
      </a>
    </div>
  );
}
