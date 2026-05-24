import { NextRequest, NextResponse } from "next/server";
import { verifyRegistrationResponse } from "@simplewebauthn/server";
import { getChallenge, addCredential } from "@/lib/auth-store";
import { createSessionToken } from "@/lib/session";
import { isoBase64URL } from "@simplewebauthn/server/helpers";

const RP_ID = process.env.RP_ID || "localhost";
const ORIGIN = process.env.ORIGIN || "http://localhost:3099";

export async function POST(request: NextRequest) {
  const body = await request.json();
  const expectedChallenge = getChallenge();

  if (!expectedChallenge) {
    return NextResponse.json({ error: "No challenge found" }, { status: 400 });
  }

  try {
    const verification = await verifyRegistrationResponse({
      response: body,
      expectedChallenge,
      expectedOrigin: ORIGIN,
      expectedRPID: RP_ID,
    });

    if (!verification.verified || !verification.registrationInfo) {
      return NextResponse.json({ error: "Verification failed" }, { status: 400 });
    }

    const { credential } = verification.registrationInfo;

    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    const credentialID = typeof credential.id === "string"
      ? credential.id
      : isoBase64URL.fromBuffer(credential.id as any);
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    const credentialPublicKey = typeof credential.publicKey === "string"
      ? credential.publicKey
      : isoBase64URL.fromBuffer(credential.publicKey as any);

    addCredential({
      credentialID,
      credentialPublicKey,
      counter: credential.counter,
      transports: body.response.transports,
    });

    const token = await createSessionToken();
    const response = NextResponse.json({ verified: true });
    response.cookies.set("session", token, {
      httpOnly: true,
      secure: true,
      sameSite: "strict",
      maxAge: 60 * 60 * 24 * 30,
      path: "/",
    });

    return response;
  } catch (err: unknown) {
    const message = err instanceof Error ? err.message : "Unknown error";
    return NextResponse.json({ error: message }, { status: 400 });
  }
}
