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
    <div className="card-glow rounded-xl p-5">
      <div className="flex justify-between items-start mb-4">
        <h3 className="font-semibold text-sm text-purple-300 uppercase tracking-wider">{summary.service}</h3>
        <span className="text-[10px] text-gray-600">{summary.fetched_at}</span>
      </div>
      <p className="text-2xl font-bold mb-4">
        {visible
          ? <span className="neon-amount">{summary.total_jpy.toLocaleString()}<span className="text-xs text-gray-500 ml-1">JPY</span></span>
          : <span className="text-gray-700">*****</span>
        }
      </p>
      <ul className="space-y-2">
        {summary.assets.map((asset, i) => (
          <li
            key={i}
            className="flex justify-between text-xs"
          >
            <span className="text-gray-400">{asset.asset_name}</span>
            <span className="text-gray-300 font-mono">
              {visible ? asset.amount.toLocaleString(undefined, { maximumFractionDigits: 6 }) : "***"}
            </span>
          </li>
        ))}
      </ul>
    </div>
  );
}
