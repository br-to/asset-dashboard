import { NextRequest, NextResponse } from "next/server";
import { jwtVerify } from "jose";

export const runtime = "nodejs";

const PUBLIC_PATHS = ["/login", "/api/auth/register", "/api/auth/login", "/api/auth/register/verify", "/api/auth/login/verify"];

// 認証を一時的に無効化する場合はtrueにする
const AUTH_DISABLED = true;

export async function middleware(request: NextRequest) {
  if (AUTH_DISABLED) {
    return NextResponse.next();
  }

  const { pathname } = request.nextUrl;

  if (PUBLIC_PATHS.some((p) => pathname.startsWith(p))) {
    return NextResponse.next();
  }

  // 静的ファイルはスキップ
  if (pathname.startsWith("/_next") || pathname.startsWith("/manifest.json") || pathname.startsWith("/favicon")) {
    return NextResponse.next();
  }

  const token = request.cookies.get("session")?.value;
  if (!token) {
    return NextResponse.redirect(new URL("/login", request.url));
  }

  try {
    const secret = new TextEncoder().encode(process.env.JWT_SECRET || "asset-dashboard-secret-change-me");
    await jwtVerify(token, secret);
    return NextResponse.next();
  } catch {
    return NextResponse.redirect(new URL("/login", request.url));
  }
}

export const config = {
  matcher: ["/((?!_next/static|_next/image|favicon.ico).*)"],
};
