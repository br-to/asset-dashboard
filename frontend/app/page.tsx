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

export default function Home() {
  const [services, setServices] = useState<ServiceSummary[]>([]);
  const [totalJpy, setTotalJpy] = useState<number>(0);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

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
      <h1 className="text-3xl font-bold mb-2">Asset Dashboard</h1>
      <p className="text-slate-400 mb-8">資産管理ダッシュボード</p>

      {loading && <p className="text-slate-400">読み込み中...</p>}
      {error && <p className="text-red-400">エラー: {error}</p>}

      {!loading && !error && (
        <>
          <div className="bg-slate-800 rounded-lg p-6 mb-8 border border-slate-700">
            <p className="text-slate-400 text-sm">総資産</p>
            <p className="text-4xl font-bold mt-1">
              {totalJpy.toLocaleString()} <span className="text-lg">JPY</span>
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {services.map((svc) => (
              <BalanceCard key={svc.service} summary={svc} />
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
