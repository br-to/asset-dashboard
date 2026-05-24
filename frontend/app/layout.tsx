import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Asset Dashboard",
  description: "Personal asset management dashboard",
  manifest: "/manifest.json",
  themeColor: "#1e293b",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="ja">
      <body className="bg-slate-900 text-slate-100 min-h-screen">
        {children}
      </body>
    </html>
  );
}
