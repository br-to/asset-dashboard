"use client";

import { useEffect, useState } from "react";
import { BalanceCard } from "./components/BalanceCard";

interface Balance {
  service: string;
  asset_name: string;
  amount: number;
  jpy_value: number | null;
  fetched_at: string;
}

interface ServiceSummary {
  service: string;
  total_jpy: number;
  assets: Balance[];
  fetched_at: string;
}

function EyeIcon({ open }: { open: boolean }) {
  if (open) {
    return (
      <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
        <path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"/>
        <circle cx="12" cy="12" r="3"/>
      </svg>
    );
  }
  return (
    <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <path d="M17.94 17.94A10.07 10.07 0 0 1 12 20c-7 0-11-8-11-8a18.45 18.45 0 0 1 5.06-5.94"/>
      <path d="M9.9 4.24A9.12 9.12 0 0 1 12 4c7 0 11 8 11 8a18.5 18.5 0 0 1-2.16 3.19"/>
      <line x1="1" y1="1" x2="23" y2="23"/>
    </svg>
  );
}

export default function Home() {
  const [services, setServices] = useState<ServiceSummary[]>([]);
  const [totalJpy, setTotalJpy] = useState<number>(0);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [visible, setVisible] = useState(true);

  useEffect(() => {
    fetch("/api/balances")
      .then((res) => res.json())
      .then((data) => {
        if (data.error) {
          setError(data.error);
          return;
        }
        setServices(data.services || []);
        setTotalJpy(data.total_jpy || 0);
      })
      .catch((err) => setError(err.message))
      .finally(() => setLoading(false));
  }, []);

  return (
    <main className="max-w-4xl mx-auto px-4 py-8">
      <div className="flex items-center justify-between mb-2">
        <h1 className="text-3xl font-bold">Asset Dashboard</h1>
        <button
          onClick={() => setVisible(!visible)}
          className="text-slate-400 hover:text-slate-200 transition p-2"
          aria-label={visible ? "残高を隠す" : "残高を表示"}
        >
          <EyeIcon open={visible} />
        </button>
      </div>
      <p className="text-slate-400 mb-8">資産管理ダッシュボード</p>

      {loading && <p className="text-slate-400">読み込み中...</p>}
      {error && <p className="text-red-400">エラー: {error}</p>}

      {!loading && !error && (
        <>
          <div className="bg-slate-800 rounded-lg p-6 mb-8 border border-slate-700">
            <p className="text-slate-400 text-sm">総資産</p>
            <p className="text-4xl font-bold mt-1">
              {visible
                ? <>{totalJpy.toLocaleString()} <span className="text-lg">JPY</span></>
                : <span className="text-slate-500">*****</span>
              }
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {services.map((svc) => (
              <BalanceCard key={svc.service} summary={svc} visible={visible} />
            ))}
          </div>

          {services.length === 0 && (
            <p className="text-slate-500 text-center mt-8">
              データがありません。スクレイパーを実行してください。
            </p>
          )}
        </>
      )}
    </main>
  );
}
