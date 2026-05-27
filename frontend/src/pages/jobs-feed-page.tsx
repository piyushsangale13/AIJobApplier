import { useState } from "react";

import { useResumes } from "../hooks/use-resumes";
import { useDiscoverJobs, useJobs, useRescoreJob, useTailorResume } from "../hooks/use-jobs";
import type { TailoredResumeResponse } from "../types/api";

const discoverySourceOptions = ["linkedin", "google", "wellfound"] as const;

export function JobsFeedPage() {
  // Discover form state
  const [keywords, setKeywords] = useState("python, fastapi, react");
  const [experienceLevels, setExperienceLevels] = useState("SDE1, backend engineer");
  const [discoverLocation, setDiscoverLocation] = useState("");
  const [resumeId, setResumeId] = useState("");
  const [remoteOnly, setRemoteOnly] = useState(true);
  const [selectedSources, setSelectedSources] = useState<string[]>([
    "linkedin",
    "google",
    "wellfound"
  ]);

  // Filter form state (separate from discover)
  const [filterCompany, setFilterCompany] = useState("");
  const [filterLocation, setFilterLocation] = useState("");
  const [filterAtsType, setFilterAtsType] = useState("");
  const [filterSource, setFilterSource] = useState("");
  const [filterMinScore, setFilterMinScore] = useState("");

  function updateFilter<T>(setter: (v: T) => void) {
    return (v: T) => { setter(v); setPage(1); };
  }

  // Pagination
  const [page, setPage] = useState(1);
  const PAGE_SIZE = 20;

  // Per-job action state
  const [scoringJobId, setScoringJobId] = useState<string | null>(null);
  const [tailoringJobId, setTailoringJobId] = useState<string | null>(null);
  const [tailorResults, setTailorResults] = useState<Record<string, TailoredResumeResponse>>({});
  const [expandedTailorJobId, setExpandedTailorJobId] = useState<string | null>(null);

  const { data: resumes } = useResumes();
  const jobsQuery = useJobs(
    {
      company: filterCompany || undefined,
      location: filterLocation || undefined,
      ats_type: filterAtsType || undefined,
      source: filterSource || undefined,
      min_relevance_score: filterMinScore ? Number(filterMinScore) : undefined
    },
    page,
    PAGE_SIZE
  );
  const discoverMutation = useDiscoverJobs();
  const rescoreMutation = useRescoreJob();
  const tailorMutation = useTailorResume();

  async function handleDiscover(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    await discoverMutation.mutateAsync({
      keywords: keywords
        .split(",")
        .map((item) => item.trim())
        .filter(Boolean),
      locations: discoverLocation ? [discoverLocation] : ["India"],
      experience_levels: experienceLevels
        .split(",")
        .map((item) => item.trim())
        .filter(Boolean),
      sources: selectedSources as Array<"linkedin" | "google" | "wellfound">,
      resume_id: resumeId || null,
      limit_per_source: 10,
      remote_only: remoteOnly
    });
  }

  async function handleAtsScore(jobId: string) {
    setScoringJobId(jobId);
    try {
      await rescoreMutation.mutateAsync({ jobId, resumeId: resumeId || undefined });
    } finally {
      setScoringJobId(null);
    }
  }

  async function handleTailorResume(jobId: string) {
    setTailoringJobId(jobId);
    try {
      const result = await tailorMutation.mutateAsync({ jobId, resumeId: resumeId || undefined });
      setTailorResults((prev) => ({ ...prev, [jobId]: result }));
      setExpandedTailorJobId(jobId);
    } finally {
      setTailoringJobId(null);
    }
  }

  function toggleSource(selected: string) {
    setSelectedSources((current) =>
      current.includes(selected)
        ? current.filter((item) => item !== selected)
        : [...current, selected]
    );
  }

  return (
    <section className="space-y-6">
      <div className="grid gap-6 xl:grid-cols-[0.95fr_1.05fr]">
        <article className="glass-panel p-6">
          <p className="text-sm uppercase tracking-[0.3em] text-slate">Discover Jobs</p>
          <h3 className="mt-3 font-display text-3xl">Discover jobs dynamically across India</h3>
          <form className="mt-6 space-y-4" onSubmit={handleDiscover}>
            <label className="block">
              <span className="text-sm text-slate">Keywords</span>
              <input
                value={keywords}
                onChange={(event) => setKeywords(event.target.value)}
                className="mt-2 w-full rounded-2xl border border-slate/20 bg-white/80 px-4 py-3 text-sm"
                placeholder="python, backend, fastapi"
              />
            </label>
            <div className="grid gap-4 md:grid-cols-2">
              <label className="block">
                <span className="text-sm text-slate">Experience Levels</span>
                <input
                  value={experienceLevels}
                  onChange={(event) => setExperienceLevels(event.target.value)}
                  className="mt-2 w-full rounded-2xl border border-slate/20 bg-white/80 px-4 py-3 text-sm"
                  placeholder="SDE1, backend engineer, full stack engineer"
                />
              </label>
              <label className="block">
                <span className="text-sm text-slate">Preferred Location</span>
                <input
                  value={discoverLocation}
                  onChange={(event) => setDiscoverLocation(event.target.value)}
                  className="mt-2 w-full rounded-2xl border border-slate/20 bg-white/80 px-4 py-3 text-sm"
                  placeholder="Remote, Bengaluru, London"
                />
              </label>
              <label className="block">
                <span className="text-sm text-slate">Resume (for ATS Score &amp; Tailor)</span>
                <select
                  value={resumeId}
                  onChange={(event) => setResumeId(event.target.value)}
                  className="mt-2 w-full rounded-2xl border border-slate/20 bg-white/80 px-4 py-3 text-sm"
                >
                  <option value="">Use latest resume</option>
                  {resumes?.map((resume) => (
                    <option key={resume.id} value={resume.id}>
                      {resume.parsed_data.name ?? resume.filename}
                    </option>
                  ))}
                </select>
              </label>
            </div>
            <div className="flex flex-wrap gap-2">
              {discoverySourceOptions.map((selected) => (
                <button
                  key={selected}
                  type="button"
                  onClick={() => toggleSource(selected)}
                  className={[
                    "rounded-full px-4 py-2 text-xs font-medium uppercase tracking-[0.2em]",
                    selectedSources.includes(selected)
                      ? "bg-ink text-mist"
                      : "bg-white/70 text-slate"
                  ].join(" ")}
                >
                  {selected}
                </button>
              ))}
            </div>
            <label className="flex items-center gap-3 text-sm text-slate">
              <input
                type="checkbox"
                checked={remoteOnly}
                onChange={(event) => setRemoteOnly(event.target.checked)}
              />
              Remote jobs only
            </label>
            <button
              type="submit"
              disabled={discoverMutation.isPending || selectedSources.length === 0}
              className="rounded-2xl bg-ink px-5 py-3 text-sm font-medium text-mist disabled:cursor-not-allowed disabled:opacity-60"
            >
              {discoverMutation.isPending ? "Discovering..." : "Discover Jobs"}
            </button>
            {discoverMutation.isError ? (
              <p className="text-sm text-red-600">
                Discovery failed: {(discoverMutation.error as Error)?.message ?? "Unknown error"}
              </p>
            ) : null}
          </form>
        </article>

        <article className="glass-panel p-6">
          <p className="text-sm uppercase tracking-[0.3em] text-slate">Filter Stored Jobs</p>
          <div className="mt-6 grid gap-4 md:grid-cols-2">
            <label className="block">
              <span className="text-sm text-slate">Company</span>
              <input
                value={filterCompany}
                onChange={(event) => updateFilter(setFilterCompany)(event.target.value)}
                className="mt-2 w-full rounded-2xl border border-slate/20 bg-white/80 px-4 py-3 text-sm"
              />
            </label>
            <label className="block">
              <span className="text-sm text-slate">Discovery Source</span>
              <select
                value={filterSource}
                onChange={(event) => updateFilter(setFilterSource)(event.target.value)}
                className="mt-2 w-full rounded-2xl border border-slate/20 bg-white/80 px-4 py-3 text-sm"
              >
                <option value="">All</option>
                <option value="linkedin">LinkedIn</option>
                <option value="google">Google</option>
                <option value="wellfound">Wellfound</option>
              </select>
            </label>
            <label className="block">
              <span className="text-sm text-slate">Location</span>
              <input
                value={filterLocation}
                onChange={(event) => updateFilter(setFilterLocation)(event.target.value)}
                className="mt-2 w-full rounded-2xl border border-slate/20 bg-white/80 px-4 py-3 text-sm"
              />
            </label>
            <label className="block">
              <span className="text-sm text-slate">Minimum ATS Score</span>
              <input
                value={filterMinScore}
                onChange={(event) => updateFilter(setFilterMinScore)(event.target.value)}
                type="number"
                min="0"
                max="100"
                className="mt-2 w-full rounded-2xl border border-slate/20 bg-white/80 px-4 py-3 text-sm"
              />
            </label>
            <label className="block">
              <span className="text-sm text-slate">ATS Type</span>
              <select
                value={filterAtsType}
                onChange={(event) => updateFilter(setFilterAtsType)(event.target.value)}
                className="mt-2 w-full rounded-2xl border border-slate/20 bg-white/80 px-4 py-3 text-sm"
              >
                <option value="">All</option>
                <option value="greenhouse">Greenhouse</option>
                <option value="lever">Lever</option>
                <option value="workday">Workday</option>
                <option value="linkedin_easy_apply">LinkedIn Easy Apply</option>
                <option value="unknown">Unknown</option>
              </select>
            </label>
          </div>
          {discoverMutation.data ? (
            <div className="mt-6 rounded-3xl bg-white/70 p-5 text-sm text-slate">
              <p className="font-semibold text-ink">Latest discovery run</p>
              <div className="mt-3 flex flex-wrap gap-2">
                {Object.entries(discoverMutation.data.source_counts).map(([src, count]) => (
                  <span
                    key={src}
                    className={[
                      "rounded-full px-3 py-1 text-xs",
                      count > 0 ? "bg-spruce/10 text-spruce" : "bg-slate/10 text-slate"
                    ].join(" ")}
                  >
                    {src}: {count} jobs
                  </span>
                ))}
              </div>
              {Object.values(discoverMutation.data.source_counts).every((c) => c === 0) ? (
                <p className="mt-3 text-xs text-amber-600">
                  All sources returned 0 jobs — sources may be rate-limiting or blocking. Try again later.
                </p>
              ) : null}
            </div>
          ) : null}
          {jobsQuery.isError ? (
            <p className="mt-4 text-sm text-red-600">
              Failed to load jobs: {(jobsQuery.error as Error)?.message ?? "Unknown error"}
            </p>
          ) : null}
        </article>
      </div>

      <article className="glass-panel p-6">
        <div className="flex items-center justify-between">
          <p className="text-sm uppercase tracking-[0.3em] text-slate">Jobs Feed</p>
          {jobsQuery.data ? (
            <span className="text-sm text-slate">
              {jobsQuery.data.total} jobs · page {jobsQuery.data.page} of {jobsQuery.data.total_pages}
            </span>
          ) : null}
        </div>
        <div className="mt-6 space-y-4">
          {jobsQuery.data?.items.map((job) => (
            <div key={job.id} className="rounded-3xl bg-white/75 p-5">
              <div className="flex flex-col gap-4 md:flex-row md:items-start md:justify-between">
                <div>
                  <div className="flex flex-wrap items-center gap-2">
                    <h4 className="text-xl font-semibold text-ink">{job.title}</h4>
                    <span className="rounded-full bg-spruce px-3 py-1 text-xs uppercase tracking-[0.2em] text-white">
                      {job.source}
                    </span>
                    <span className="rounded-full bg-ink px-3 py-1 text-xs uppercase tracking-[0.2em] text-mist">
                      {job.ats_type}
                    </span>
                  </div>
                  <p className="mt-1 text-sm text-slate">
                    {job.company} • {job.location ?? "Unknown"}
                  </p>
                </div>
                <div className="text-right">
                  <p className="text-sm uppercase tracking-[0.2em] text-slate">ATS Score</p>
                  <p className="font-display text-4xl text-ink">
                    {job.relevance_score != null ? Math.round(job.relevance_score) : "--"}
                  </p>
                </div>
              </div>

              <p className="mt-4 line-clamp-4 text-sm leading-7 text-slate">{job.description}</p>

              {(job.ai_analysis.missing_skills ?? []).length > 0 ? (
                <div className="mt-4 flex flex-wrap gap-2">
                  {(job.ai_analysis.missing_skills ?? []).map((skill) => (
                    <span key={skill} className="rounded-full bg-rose-100 px-3 py-1 text-xs text-rose-700">
                      Missing: {skill}
                    </span>
                  ))}
                </div>
              ) : null}

              {job.ai_analysis.reasoning ? (
                <p className="mt-3 text-sm text-slate">{job.ai_analysis.reasoning}</p>
              ) : null}

              <div className="mt-5 flex flex-wrap gap-3">
                <a
                  href={job.apply_url}
                  target="_blank"
                  rel="noreferrer"
                  className="rounded-2xl bg-ember px-4 py-2 text-sm font-medium text-white"
                >
                  Open Job
                </a>
                <button
                  type="button"
                  disabled={scoringJobId === job.id}
                  onClick={() => handleAtsScore(job.id)}
                  className="rounded-2xl bg-spruce/10 px-4 py-2 text-sm font-medium text-spruce disabled:cursor-not-allowed disabled:opacity-60"
                >
                  {scoringJobId === job.id ? "Scoring..." : "ATS Score"}
                </button>
                <button
                  type="button"
                  disabled={tailoringJobId === job.id}
                  onClick={() => handleTailorResume(job.id)}
                  className="rounded-2xl bg-ink/10 px-4 py-2 text-sm font-medium text-ink disabled:cursor-not-allowed disabled:opacity-60"
                >
                  {tailoringJobId === job.id ? "Tailoring..." : "Tailor Resume"}
                </button>
              </div>

              {tailorResults[job.id] && expandedTailorJobId === job.id ? (
                <div className="mt-5 rounded-2xl border border-slate/20 bg-white/80 p-5">
                  <div className="flex items-center justify-between">
                    <p className="text-sm font-semibold text-ink">Tailored Resume</p>
                    <div className="flex gap-3">
                      <button
                        type="button"
                        onClick={() => {
                          void navigator.clipboard.writeText(tailorResults[job.id].tailored_resume);
                        }}
                        className="text-xs text-slate underline"
                      >
                        Copy
                      </button>
                      <button
                        type="button"
                        onClick={() => setExpandedTailorJobId(null)}
                        className="text-xs text-slate underline"
                      >
                        Collapse
                      </button>
                    </div>
                  </div>

                  {tailorResults[job.id].matched_keywords.length > 0 ? (
                    <div className="mt-3 flex flex-wrap gap-2">
                      {tailorResults[job.id].matched_keywords.map((kw) => (
                        <span key={kw} className="rounded-full bg-spruce/10 px-3 py-1 text-xs text-spruce">
                          {kw}
                        </span>
                      ))}
                    </div>
                  ) : null}

                  {tailorResults[job.id].key_changes.length > 0 ? (
                    <ul className="mt-3 space-y-1">
                      {tailorResults[job.id].key_changes.map((change, index) => (
                        <li key={index} className="text-xs text-slate before:mr-2 before:content-['→']">
                          {change}
                        </li>
                      ))}
                    </ul>
                  ) : null}

                  <pre className="mt-4 whitespace-pre-wrap text-xs leading-6 text-slate">
                    {tailorResults[job.id].tailored_resume}
                  </pre>
                </div>
              ) : tailorResults[job.id] && expandedTailorJobId !== job.id ? (
                <button
                  type="button"
                  onClick={() => setExpandedTailorJobId(job.id)}
                  className="mt-3 text-xs text-spruce underline"
                >
                  Show tailored resume
                </button>
              ) : null}
            </div>
          ))}
          {jobsQuery.isLoading ? <p className="text-sm text-slate">Loading jobs...</p> : null}
          {!jobsQuery.isLoading && !jobsQuery.isError && jobsQuery.data?.total === 0 ? (
            <p className="text-sm text-slate">
              No jobs stored yet. Run a discovery pass above, or clear any active filters.
            </p>
          ) : null}
        </div>

        {jobsQuery.data && jobsQuery.data.total_pages > 1 ? (
          <div className="mt-6 flex items-center justify-center gap-3">
            <button
              type="button"
              disabled={page <= 1}
              onClick={() => setPage((p) => p - 1)}
              className="rounded-2xl border border-slate/20 bg-white/80 px-4 py-2 text-sm text-slate disabled:cursor-not-allowed disabled:opacity-40"
            >
              ← Previous
            </button>
            <div className="flex gap-1">
              {Array.from({ length: jobsQuery.data.total_pages }, (_, i) => i + 1)
                .filter((p) => p === 1 || p === jobsQuery.data!.total_pages || Math.abs(p - page) <= 2)
                .reduce<(number | "…")[]>((acc, p, idx, arr) => {
                  if (idx > 0 && p - (arr[idx - 1] as number) > 1) acc.push("…");
                  acc.push(p);
                  return acc;
                }, [])
                .map((p, idx) =>
                  p === "…" ? (
                    <span key={`ellipsis-${idx}`} className="px-2 py-2 text-sm text-slate">…</span>
                  ) : (
                    <button
                      key={p}
                      type="button"
                      onClick={() => setPage(p as number)}
                      className={[
                        "min-w-[2rem] rounded-xl px-3 py-2 text-sm",
                        p === page
                          ? "bg-ink text-mist"
                          : "bg-white/80 text-slate hover:bg-white"
                      ].join(" ")}
                    >
                      {p}
                    </button>
                  )
                )}
            </div>
            <button
              type="button"
              disabled={page >= jobsQuery.data.total_pages}
              onClick={() => setPage((p) => p + 1)}
              className="rounded-2xl border border-slate/20 bg-white/80 px-4 py-2 text-sm text-slate disabled:cursor-not-allowed disabled:opacity-40"
            >
              Next →
            </button>
          </div>
        ) : null}
      </article>
    </section>
  );
}
