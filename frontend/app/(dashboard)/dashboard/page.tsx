import { Card } from "@/components/ui/card";

export default function DashboardPage() {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold tracking-tight">Market Intelligence Dashboard</h1>
        <p className="text-muted-foreground">AI TradeQ Platform Enterprise Overview Placeholder</p>
      </div>

      <div className="grid gap-4 md:grid-cols-3">
        <Card className="p-6">
          <h3 className="font-medium text-sm text-muted-foreground">System Status</h3>
          <p className="text-2xl font-bold text-emerald-500 mt-2">Operational</p>
        </Card>
        <Card className="p-6">
          <h3 className="font-medium text-sm text-muted-foreground">Backend API</h3>
          <p className="text-2xl font-bold mt-2">Connected (v1.0)</p>
        </Card>
        <Card className="p-6">
          <h3 className="font-medium text-sm text-muted-foreground">AI Agent Engine</h3>
          <p className="text-2xl font-bold text-amber-500 mt-2">MCP Ready (Idle)</p>
        </Card>
      </div>
    </div>
  );
}
