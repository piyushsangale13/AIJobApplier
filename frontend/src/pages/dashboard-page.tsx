import { useDashboardStats } from "../hooks/use-dashboard-stats";
import { StatCard } from "../components/stat-card";

export function DashboardPage() {
  const { data, isLoading } = useDashboardStats();

  const stats = data ?? {
    jobs_found_today: 0,
    applications_submitted: 0,
    pending_applications: 0,
    failed_applications: 0
  };

  return (
    <section className="space-y-6">
      <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
        <StatCard
          label="Jobs Found Today"
          value={stats.jobs_found_today}
          accent="bg-spruce"
        />
        <StatCard
          label="Applications Submitted"
          value={stats.applications_submitted}
          accent="bg-ember"
        />
        <StatCard
          label="Pending Applications"
          value={stats.pending_applications}
          accent="bg-ink"
        />
        <StatCard
          label="Failed Applications"
          value={stats.failed_applications}
          accent="bg-rose-500"
        />
      </div>

      <div className="grid gap-6 lg:grid-cols-[1.3fr_0.9fr]">
        <article className="glass-panel p-6">
          <p className="text-sm uppercase tracking-[0.3em] text-slate">System Overview</p>
          <h3 className="mt-3 font-display text-3xl">Pipeline ready for job discovery.</h3>
          <p className="mt-4 max-w-2xl text-sm leading-7 text-slate">
            Phase 1 covers resume ingestion, AI parsing, persistence, and the monitoring shell.
            The next phases plug job providers and browser agents into this same foundation.
          </p>
        </article>

        <article className="glass-panel p-6">
          <p className="text-sm uppercase tracking-[0.3em] text-slate">Status</p>
          <ul className="mt-4 space-y-3 text-sm text-slate">
            <li>Resume upload API: live</li>
            <li>OpenAI structured parsing: configured</li>
            <li>Application tracking surface: live</li>
            <li>Browser automation handlers: queued for next phases</li>
          </ul>
          {isLoading ? <p className="mt-4 text-sm text-slate">Loading dashboard data...</p> : null}
        </article>
      </div>
    </section>
  );
}
