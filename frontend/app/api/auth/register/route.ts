import { NextResponse } from "next/server";
import { generateRegistrationOptions } from "@simplewebauthn/server";
import { isRegistered, setChallenge } from "@/lib/auth-store";

const RP_NAME = "Asset Dashboard";
const RP_ID = process.env.RP_ID || "localhost";

export async function GET() {
  if (isRegistered()) {
    return NextResponse.json({ error: "Already registered" }, { status: 400 });
  }

  const options = await generateRegistrationOptions({
    rpName: RP_NAME,
    rpID: RP_ID,
    userName: "owner",
    userDisplayName: "Owner",
    attestationType: "none",
    authenticatorSelection: {
      residentKey: "preferred",
      userVerification: "preferred",
    },
  });

  setChallenge(options.challenge);

  return NextResponse.json(options);
}
