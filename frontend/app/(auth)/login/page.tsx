'use client';

import { useState } from 'react';
import Link from 'next/link';
import { useRouter } from 'next/navigation';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Card } from '@/components/ui/card';
import { useAuthStore } from '@/store/useAuthStore';

export default function LoginPage() {
  const router = useRouter();
  const { login, isLoading, error, clearError } = useAuthStore();

  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [validationError, setValidationError] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    clearError();
    setValidationError(null);

    if (!email.trim() || !password) {
      setValidationError('Please enter both email and password.');
      return;
    }

    try {
      await login({ email: email.trim(), password });
      router.push('/dashboard');
    } catch {
      // Handled by store error state
    }
  };

  const displayedError = validationError || error;

  return (
    <div className="flex min-h-screen items-center justify-center p-6 bg-background">
      <Card className="w-full max-w-md p-8 space-y-6 border border-border shadow-lg">
        <div className="text-center space-y-2">
          <Link href="/" className="inline-block text-2xl font-black tracking-tight text-primary">
            AI TradeQ
          </Link>
          <h1 className="text-xl font-bold tracking-tight text-foreground">Sign In</h1>
          <p className="text-sm text-muted-foreground">Access your institutional trading intelligence portal</p>
        </div>

        {displayedError && (
          <div className="p-3 rounded-md bg-destructive/15 border border-destructive/30 text-destructive text-sm font-medium">
            {displayedError}
          </div>
        )}

        <form className="space-y-4" onSubmit={handleSubmit}>
          <div className="space-y-2">
            <label className="text-sm font-medium text-foreground">Email Address</label>
            <Input
              type="email"
              placeholder="analyst@firm.com"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              disabled={isLoading}
              required
              autoComplete="email"
            />
          </div>
          <div className="space-y-2">
            <label className="text-sm font-medium text-foreground">Password</label>
            <Input
              type="password"
              placeholder="••••••••"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              disabled={isLoading}
              required
              autoComplete="current-password"
            />
          </div>
          <Button type="submit" className="w-full font-semibold" disabled={isLoading}>
            {isLoading ? 'Authenticating...' : 'Sign In'}
          </Button>
        </form>

        <div className="pt-2 text-center text-xs text-muted-foreground border-t border-border">
          Don&apos;t have an account?{' '}
          <Link href="/register" className="text-primary hover:underline font-semibold">
            Create Account
          </Link>
        </div>
      </Card>
    </div>
  );
}
