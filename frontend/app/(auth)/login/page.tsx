'use client';

import Link from "next/link";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Card } from "@/components/ui/card";

export default function LoginPage() {
  return (
    <div className="flex min-h-screen items-center justify-center p-6">
      <Card className="w-full max-w-md p-8 space-y-6">
        <div className="text-center space-y-2">
          <h1 className="text-2xl font-bold tracking-tight">Sign In to AI TradeQ</h1>
          <p className="text-sm text-muted-foreground">Enter your credentials to access your account</p>
        </div>
        <form className="space-y-4" onSubmit={(e) => e.preventDefault()}>
          <div className="space-y-2">
            <label className="text-sm font-medium">Email</label>
            <Input type="email" placeholder="name@company.com" disabled />
          </div>
          <div className="space-y-2">
            <label className="text-sm font-medium">Password</label>
            <Input type="password" placeholder="••••••••" disabled />
          </div>
          <Button type="submit" className="w-full" disabled>
            Sign In (Foundation UI Only)
          </Button>
        </form>
        <p className="text-xs text-center text-muted-foreground">
          Don&apos;t have an account? <Link href="/register" className="text-primary underline">Register</Link>
        </p>
      </Card>
    </div>
  );
}
