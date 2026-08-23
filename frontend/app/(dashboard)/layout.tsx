'use client';

import { useEffect } from 'react';
import Link from 'next/link';
import { useRouter } from 'next/navigation';
import { Button } from '@/components/ui/button';
import { useAuthStore } from '@/store/useAuthStore';

export default function DashboardLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const router = useRouter();
  const { user, isAuthenticated, isLoading, initializeAuth, logout } = useAuthStore();

  useEffect(() => {
    initializeAuth();
  }, [initializeAuth]);

  const handleLogout = async () => {
    await logout();
    router.push('/login');
  };

  return (
    <div className="min-h-screen flex flex-col bg-background">
      <header className="border-b border-border bg-card px-6 py-4 flex items-center justify-between shadow-sm">
        <div className="flex items-center gap-6">
          <Link href="/" className="font-bold text-xl text-primary tracking-tight">
            AI TradeQ
          </Link>
          <nav className="hidden md:flex gap-4 text-sm text-muted-foreground">
            <Link href="/dashboard" className="text-foreground font-medium hover:text-primary transition-colors">
              Dashboard
            </Link>
            <span className="opacity-40 cursor-not-allowed">Markets</span>
            <span className="opacity-40 cursor-not-allowed">AI Research</span>
            <span className="opacity-40 cursor-not-allowed">Portfolio</span>
          </nav>
        </div>

        <div className="flex items-center gap-4">
          {isLoading ? (
            <span className="text-xs text-muted-foreground animate-pulse">Checking session...</span>
          ) : isAuthenticated && user ? (
            <div className="flex items-center gap-3">
              <div className="text-right hidden sm:block">
                <p className="text-xs font-semibold text-foreground">{user.full_name || user.email}</p>
                <p className="text-[10px] text-muted-foreground uppercase font-mono">
                  {user.roles.join(', ') || 'USER'}
                </p>
              </div>
              <Button variant="outline" size="sm" onClick={handleLogout} className="text-xs">
                Sign Out
              </Button>
            </div>
          ) : (
            <div className="flex items-center gap-2">
              <Link href="/login">
                <Button variant="outline" size="sm">Sign In</Button>
              </Link>
              <Link href="/register">
                <Button size="sm">Register</Button>
              </Link>
            </div>
          )}
        </div>
      </header>

      <main className="flex-1 p-6 max-w-7xl w-full mx-auto">{children}</main>
    </div>
  );
}
