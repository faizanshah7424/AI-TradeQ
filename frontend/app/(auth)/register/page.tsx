'use client';

import Link from "next/link";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Card } from "@/components/ui/card";

export default function RegisterPage() {
  return (
    <div className="flex min-h-screen items-center justify-center p-6">
      <Card className="w-full max-w-md p-8 space-y-6">
        <div className="text-center space-y-2">
          <h1 className="text-2xl font-bold tracking-tight">Create AI TradeQ Account</h1>
          <p className="text-sm text-muted-foreground">Sign up for enterprise decision intelligence</p>
        </div>
        <form className="space-y-4" onSubmit={(e) => e.preventDefault()}>
          <div className="space-y-2">
            <label className="text-sm font-medium">Full Name</label>
            <Input type="text" placeholder="Jane Doe" disabled />
          </div>
          <div className="space-y-2">
            <label className="text-sm font-medium">Work Email</label>
            <Input type="email" placeholder="name@company.com" disabled />
          </div>
          <div className="space-y-2">
            <label className="text-sm font-medium">Password</label>
            <Input type="password" placeholder="••••••••" disabled />
          </div>
          <Button type="submit" className="w-full" disabled>
            Register (Foundation UI Only)
          </Button>
        </form>
        <p className="text-xs text-center text-muted-foreground">
          Already registered? <Link href="/login" className="text-primary underline">Sign In</Link>
        </p>
      </Card>
    </div>
  );
}
