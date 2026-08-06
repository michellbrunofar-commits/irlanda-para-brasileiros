import { NextRequest, NextResponse } from "next/server";

const EMAIL_RE = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

export async function POST(req: NextRequest) {
  const apiKey = process.env.BREVO_API_KEY;
  const listId = process.env.BREVO_LIST_ID;
  const templateId = process.env.BREVO_DOI_TEMPLATE_ID;

  if (!apiKey || !listId || !templateId) {
    console.error("Newsletter: variáveis BREVO_API_KEY/BREVO_LIST_ID/BREVO_DOI_TEMPLATE_ID não configuradas.");
    return NextResponse.json(
      { error: "Inscrição indisponível no momento. Tente novamente mais tarde." },
      { status: 503 }
    );
  }

  const body = await req.json().catch(() => null);
  const email = typeof body?.email === "string" ? body.email.trim() : "";
  const name = typeof body?.name === "string" ? body.name.trim() : "";

  if (!EMAIL_RE.test(email)) {
    return NextResponse.json({ error: "E-mail inválido." }, { status: 400 });
  }

  const origin = req.nextUrl.origin;

  const brevoRes = await fetch("https://api.brevo.com/v3/contacts/doubleOptinConfirmation", {
    method: "POST",
    headers: {
      "api-key": apiKey,
      "Content-Type": "application/json",
      Accept: "application/json",
    },
    body: JSON.stringify({
      email,
      attributes: { FIRSTNAME: name, ORIGIN: "portal" },
      includeListIds: [Number(listId)],
      templateId: Number(templateId),
      redirectionUrl: `${origin}/inscricao-confirmada`,
    }),
  });

  if (!brevoRes.ok) {
    const detail = await brevoRes.text().catch(() => "");
    console.error("Newsletter: erro Brevo", brevoRes.status, detail);
    return NextResponse.json(
      { error: "Não foi possível concluir a inscrição. Tente novamente." },
      { status: 502 }
    );
  }

  return NextResponse.json({ ok: true });
}
