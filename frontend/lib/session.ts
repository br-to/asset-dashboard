import { SignJWT } from "jose";

const JWT_SECRET = process.env.JWT_SECRET || "asset-dashboard-secret-change-me";

export async function createSessionToken(): Promise<string> {
  const secret = new TextEncoder().encode(JWT_SECRET);
  return new SignJWT({ sub: "owner" })
    .setProtectedHeader({ alg: "HS256" })
    .setIssuedAt()
    .setExpirationTime("30d")
    .sign(secret);
}
