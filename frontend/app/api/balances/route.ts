import { NextResponse } from "next/server";
import Database from "better-sqlite3";
import path from "path";
import fs from "fs";

const DB_PATH = path.resolve(
  process.cwd(),
  "..",
  "scraper",
  "data",
  "balances.db"
);

export async function GET() {
  if (!fs.existsSync(DB_PATH)) {
    return NextResponse.json({
      total_jpy: 0,
      services: [],
      error: "DB not found. Run scraper first.",
    });
  }

  const db = new Database(DB_PATH, { readonly: true });

  try {
    // 各サービスの最新取得時刻を取得
    const latestTimes = db
      .prepare(
        `SELECT service, MAX(fetched_at) as latest
         FROM balances
         GROUP BY service`
      )
      .all() as { service: string; latest: string }[];

    const services = latestTimes.map(({ service, latest }) => {
      const assets = db
        .prepare(
          `SELECT service, asset_name, amount, jpy_value, fetched_at
           FROM balances
           WHERE service = ? AND fetched_at = ?`
        )
        .all(service, latest) as {
        service: string;
        asset_name: string;
        amount: number;
        jpy_value: number | null;
        fetched_at: string;
      }[];

      const total_jpy = assets.reduce(
        (sum, a) => sum + (a.jpy_value || 0),
        0
      );

      return {
        service,
        total_jpy,
        assets,
        fetched_at: latest,
      };
    });

    const total_jpy = services.reduce((sum, s) => sum + s.total_jpy, 0);

    return NextResponse.json({ total_jpy, services });
  } finally {
    db.close();
  }
}
