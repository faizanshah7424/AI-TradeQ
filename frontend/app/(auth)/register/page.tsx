'use client';

import { useState } from 'react';
import Link from 'next/link';
import { useRouter } from 'next/navigation';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Card } from '@/components/ui/card';
import { useAuthStore } from '@/store/useAuthStore';

export default function RegisterPage() {
  const router = useRouter();
  const { register, isLoading, error, clearError } = useAuthStore();

  const [firstName, setFirstName] = useState('');
  const [lastName, setLastName] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [validationError, setValidationError] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    clearError();
    setValidationError(null);

    if (!email.trim() || !password) {
      setValidationError('Please fill in all required fields.');
      return;
    }

    if (password.length < 8) {
      setValidationError('Password must be at least 8 characters long.');
      return;
    }

    if (password !== confirmPassword) {
      setValidationError('Passwords do not match.');
      return;
    }

    try {
      await register({
        email: email.trim(),
        password,
        first_name: firstName.trim() || undefined,
        last_name: lastName.trim() || undefined,
      });
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
          <h1 className="text-xl font-bold tracking-tight text-foreground">Create Account</h1>
          <p className="text-sm text-muted-foreground">Register for institutional market research and AI decision support</p>
        </div>

        {displayedError && (
          <div className="p-3 rounded-md bg-destructive/15 border border-destructive/30 text-destructive text-sm font-medium">
            {displayedError}
          </div>
        )}

        <form className="space-y-4" onSubmit={handleSubmit}>
          <div className="grid grid-cols-2 gap-3">
            <div className="space-y-2">
              <label className="text-sm font-medium text-foreground">First Name</label>
              <Input
                type="text"
                placeholder="Jane"
                value={firstName}
                onChange={(e) => setFirstName(e.target.value)}
                disabled={isLoading}
              />
            </div>
            <div className="space-y-2">
              <label className="text-sm font-medium text-foreground">Last Name</label>
              <Input
                type="text"
                placeholder="Doe"
                value={lastName}
                onChange={(e) => setLastName(e.target.value)}
                disabled={isLoading}
              />
            </div>
          </div>

          <div className="space-y-2">
            <label className="text-sm font-medium text-foreground">Work Email Address</label>
            <Input
              type="email"
              placeholder="jane.doe@firm.com"
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
              placeholder="At least 8 characters"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              disabled={isLoading}
              required
              autoComplete="new-password"
            />
          </div>

          <div className="space-y-2">
            <label className="text-sm font-medium text-foreground">Confirm Password</label>
            <Input
              type="password"
              placeholder="Re-type password"
              value={confirmPassword}
              onChange={(e) => setConfirmPassword(e.target.value)}
              disabled={isLoading}
              required
              autoComplete="new-password"
            />
          </div>

          <Button type="submit" className="w-full font-semibold" disabled={isLoading}>
            {isLoading ? 'Creating Account...' : 'Complete Registration'}
          </Button>
        </form>

        <div className="pt-2 text-center text-xs text-muted-foreground border-t border-border">
          Already have an account?{' '}
          <Link href="/login" className="text-primary hover:underline font-semibold">
            Sign In
          </Link>
        </div>
      </Card>
    </div>
  );
}
