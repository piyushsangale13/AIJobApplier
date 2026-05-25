import { NavLink, Outlet } from "react-router-dom";

const navItems = [
  { to: "/", label: "Dashboard" },
  { to: "/resume-upload", label: "Resume Upload" },
  { to: "/jobs-feed", label: "Jobs Feed" },
  { to: "/applications", label: "Application Tracker" },
  { to: "/settings", label: "Settings" },
  { to: "/logs", label: "Logs" }
];

export function LayoutShell() {
  return (
    <div className="min-h-screen px-4 py-6 md:px-8">
      <div className="mx-auto grid max-w-7xl gap-6 lg:grid-cols-[280px_1fr]">
        <aside className="glass-panel p-6">
          <p className="text-sm uppercase tracking-[0.3em] text-slate">Personal Automation</p>
          <h1 className="mt-3 font-display text-4xl leading-tight text-ink">
            AI Job Applier
          </h1>
          <p className="mt-4 text-sm leading-6 text-slate">
            Resume-aware job discovery and application automation for your own workflow.
          </p>
          <nav className="mt-8 flex flex-col gap-2">
            {navItems.map((item) => (
              <NavLink
                key={item.to}
                to={item.to}
                className={({ isActive }) =>
                  [
                    "rounded-2xl px-4 py-3 text-sm font-medium transition",
                    isActive
                      ? "bg-ink text-mist"
                      : "bg-white/60 text-ink hover:bg-white"
                  ].join(" ")
                }
              >
                {item.label}
              </NavLink>
            ))}
          </nav>
        </aside>

        <main className="space-y-6">
          <header className="glass-panel flex flex-col justify-between gap-4 p-6 md:flex-row md:items-end">
            <div>
              <p className="text-sm uppercase tracking-[0.3em] text-slate">Phase 1</p>
              <h2 className="mt-2 font-display text-3xl text-ink">
                Resume ingestion and parsing foundation
              </h2>
            </div>
            <div className="rounded-2xl bg-ember/10 px-4 py-3 text-sm text-ink">
              Non-SaaS, local-first architecture with FastAPI, Postgres, React, and OpenAI.
            </div>
          </header>
          <Outlet />
        </main>
      </div>
    </div>
  );
}
