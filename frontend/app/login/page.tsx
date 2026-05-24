"use client";

import { useState, useEffect } from "react";
import { startRegistration, startAuthentication } from "@simplewebauthn/browser";

export default function LoginPage() {
  const [registered, setRegistered] = useState<boolean | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    // ログインオプション取得して登録済みか判定
    fetch("/api/auth/login")
      .then((res) => res.json())
      .then((data) => {
        if (data.registered === false) {
          setRegistered(false);
        } else {
          setRegistered(true);
        }
      })
      .catch(() => setRegistered(false));
  }, []);

  async function handleRegister() {
    setLoading(true);
    setError(null);
    try {
      const optionsRes = await fetch("/api/auth/register");
      const options = await optionsRes.json();
      if (options.error) {
        setError(options.error);
        return;
      }

      const credential = await startRegistration({ optionsJSON: options });

      const verifyRes = await fetch("/api/auth/register/verify", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(credential),
      });
      const result = await verifyRes.json();

      if (result.verified) {
        window.location.href = "/";
      } else {
        setError(result.error || "Registration failed");
      }
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : "Registration error");
    } finally {
      setLoading(false);
    }
  }

  async function handleLogin() {
    setLoading(true);
    setError(null);
    try {
      const optionsRes = await fetch("/api/auth/login");
      const options = await optionsRes.json();

      const credential = await startAuthentication({ optionsJSON: options });

      const verifyRes = await fetch("/api/auth/login/verify", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(credential),
      });
      const result = await verifyRes.json();

      if (result.verified) {
        window.location.href = "/";
      } else {
        setError(result.error || "Authentication failed");
      }
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : "Authentication error");
    } finally {
      setLoading(false);
    }
  }

  return (
    <main className="min-h-screen flex items-center justify-center bg-slate-900">
      <div className="bg-slate-800 rounded-lg p-8 border border-slate-700 w-full max-w-sm">
        <h1 className="text-2xl font-bold text-center mb-6">Asset Dashboard</h1>

        {registered === null && (
          <p className="text-slate-400 text-center">Loading...</p>
        )}

        {registered === false && (
          <div className="text-center">
            <p className="text-slate-400 mb-4">初回セットアップ: Passkeyを登録してください</p>
            <button
              onClick={handleRegister}
              disabled={loading}
              className="w-full bg-blue-600 hover:bg-blue-500 text-white font-semibold py-3 px-4 rounded-lg disabled:opacity-50 transition"
            >
              {loading ? "処理中..." : "Passkeyを登録"}
            </button>
          </div>
        )}

        {registered === true && (
          <div className="text-center">
            <p className="text-slate-400 mb-4">Passkeyで認証してください</p>
            <button
              onClick={handleLogin}
              disabled={loading}
              className="w-full bg-blue-600 hover:bg-blue-500 text-white font-semibold py-3 px-4 rounded-lg disabled:opacity-50 transition"
            >
              {loading ? "認証中..." : "ログイン"}
            </button>
          </div>
        )}

        {error && (
          <p className="text-red-400 text-sm text-center mt-4">{error}</p>
        )}
      </div>
    </main>
  );
}
