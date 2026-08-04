import Link from "next/link";

export default function DashboardLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <div className="min-h-screen flex flex-col">
      <header className="border-b bg-card px-6 py-4 flex items-center justify-between">
        <Link href="/" className="font-bold text-xl text-primary">
          AI TradeQ
        </Link>
        <nav className="flex gap-4 text-sm text-muted-foreground">
          <Link href="/dashboard" className="hover:text-foreground">Dashboard</Link>
          <span className="opacity-50">Markets</span>
          <span className="opacity-50">AI Research</span>
          <span className="opacity-50">Portfolio</span>
        </nav>
      </header>
      <main className="flex-1 p-6">{children}</main>
    </div>
  );
}
