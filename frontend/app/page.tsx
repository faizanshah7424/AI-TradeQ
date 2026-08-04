import Link from "next/link";
import { Button } from "@/components/ui/button";

export default function Home() {
  return (
    <main className="flex min-h-screen flex-col items-center justify-center p-24 text-center">
      <div className="z-10 max-w-5xl w-full items-center justify-center font-mono text-sm flex flex-col gap-6">
        <h1 className="text-4xl font-bold tracking-tight sm:text-6xl text-primary">
          AI TradeQ
        </h1>
        <p className="text-xl text-muted-foreground max-w-2xl">
          Enterprise AI Market Research & Decision Intelligence Platform Foundation.
        </p>
        <div className="flex gap-4 mt-6">
          <Link href="/dashboard">
            <Button size="lg">Go to Dashboard</Button>
          </Link>
          <Link href="/login">
            <Button variant="outline" size="lg">Sign In</Button>
          </Link>
        </div>
      </div>
    </main>
  );
}
