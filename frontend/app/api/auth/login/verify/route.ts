import { NextRequest, NextResponse } from "next/server";
import { verifyAuthenticationResponse } from "@simplewebauthn/server";
import { getChallenge, getCredentials, updateCredentialCounter } from "@/lib/auth-store";
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

  const credentials = getCredentials();
  const credential = credentials.find(
    (c) => c.credentialID === body.id
  );

  if (!credential) {
    return NextResponse.json({ error: "Credential not found" }, { status: 400 });
  }

  try {
    const verification = await verifyAuthenticationResponse({
      response: body,
      expectedChallenge,
      expectedOrigin: ORIGIN,
      expectedRPID: RP_ID,
      credential: {
        id: credential.credentialID,
        publicKey: isoBase64URL.toBuffer(credential.credentialPublicKey),
        counter: credential.counter,
        transports: credential.transports as AuthenticatorTransport[] | undefined,
      },
    });

    if (!verification.verified) {
      return NextResponse.json({ error: "Verification failed" }, { status: 400 });
    }

    updateCredentialCounter(credential.credentialID, verification.authenticationInfo.newCounter);

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
