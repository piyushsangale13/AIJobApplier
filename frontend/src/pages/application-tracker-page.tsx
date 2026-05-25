import { useApplications } from "../hooks/use-applications";

export function ApplicationTrackerPage() {
  const { data: applications, isLoading } = useApplications();

  return (
    <section className="glass-panel p-6">
      <p className="text-sm uppercase tracking-[0.3em] text-slate">Application Tracker</p>
      <h3 className="mt-3 font-display text-3xl">Tracked submissions and automation outcomes</h3>
      <div className="mt-6 space-y-4">
        {applications?.map((application) => (
          <div key={application.id} className="rounded-3xl bg-white/70 p-5">
            <div className="flex items-center justify-between gap-4">
              <div>
                <h4 className="text-lg font-semibold text-ink">{application.role}</h4>
                <p className="text-sm text-slate">{application.company}</p>
              </div>
              <span className="rounded-full bg-ink px-3 py-1 text-xs uppercase tracking-[0.2em] text-mist">
                {application.status}
              </span>
            </div>
            <p className="mt-3 text-sm text-slate">{application.notes ?? "No notes yet."}</p>
          </div>
        ))}
        {isLoading ? <p className="text-sm text-slate">Loading applications...</p> : null}
        {!applications?.length && !isLoading ? (
          <p className="text-sm text-slate">No applications tracked yet.</p>
        ) : null}
      </div>
    </section>
  );
}
