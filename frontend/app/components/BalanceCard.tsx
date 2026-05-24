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

export function BalanceCard({ summary, visible }: { summary: ServiceSummary; visible: boolean }) {
  return (
    <div className="bg-slate-800 rounded-lg p-4 border border-slate-700">
      <div className="flex justify-between items-start mb-3">
        <h3 className="font-semibold text-lg">{summary.service}</h3>
        <span className="text-xs text-slate-500">{summary.fetched_at}</span>
      </div>
      <p className="text-2xl font-bold mb-3">
        {visible
          ? <>{summary.total_jpy.toLocaleString()}{" "}<span className="text-sm text-slate-400">JPY</span></>
          : <span className="text-slate-500">*****</span>
        }
      </p>
      <ul className="space-y-1">
        {summary.assets.map((asset, i) => (
          <li
            key={i}
            className="flex justify-between text-sm text-slate-300"
          >
            <span>{asset.asset_name}</span>
            <span>{visible ? asset.amount.toLocaleString() : "***"}</span>
          </li>
        ))}
      </ul>
    </div>
  );
}
