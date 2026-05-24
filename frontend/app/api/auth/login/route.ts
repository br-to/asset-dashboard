import { NextResponse } from "next/server";
import { generateAuthenticationOptions } from "@simplewebauthn/server";
import { getCredentials, isRegistered, setChallenge } from "@/lib/auth-store";

const RP_ID = process.env.RP_ID || "localhost";

export async function GET() {
  if (!isRegistered()) {
    return NextResponse.json({ registered: false });
  }

  const credentials = getCredentials();

  const options = await generateAuthenticationOptions({
    rpID: RP_ID,
    allowCredentials: credentials.map((cred) => ({
      id: cred.credentialID,
      transports: cred.transports as AuthenticatorTransport[] | undefined,
    })),
    userVerification: "preferred",
  });

  setChallenge(options.challenge);

  return NextResponse.json(options);
}
