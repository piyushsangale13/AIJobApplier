import { useState } from "react";

import { useResumes } from "../hooks/use-resumes";
import { useDiscoverJobs, useJobs, useRescoreJob } from "../hooks/use-jobs";

const discoverySourceOptions = ["linkedin", "google", "wellfound"] as const;

export function JobsFeedPage() {
  const [company, setCompany] = useState("");
  const [location, setLocation] = useState("");
  const [atsType, setAtsType] = useState("");
  const [source, setSource] = useState("");
  const [minScore, setMinScore] = useState("");
  const [keywords, setKeywords] = useState("python, fastapi, react");
  const [experienceLevels, setExperienceLevels] = useState("SDE1, backend engineer");
  const [resumeId, setResumeId] = useState("");
  const [remoteOnly, setRemoteOnly] = useState(true);
  const [selectedSources, setSelectedSources] = useState<string[]>([
    "linkedin",
    "google",
    "wellfound"
  ]);

  const { data: resumes } = useResumes();
  const jobsQuery = useJobs({
    company: company || undefined,
    location: location || undefined,
    ats_type: atsType || undefined,
    source: source || undefined,
    min_relevance_score: minScore ? Number(minScore) : undefined
  });
  const discoverMutation = useDiscoverJobs();
  const rescoreMutation = useRescoreJob();

  async function handleDiscover(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    await discoverMutation.mutateAsync({
      keywords: keywords
        .split(",")
        .map((item) => item.trim())
        .filter(Boolean),
      locations: location ? [location] : ["India"],
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
                  value={location}
                  onChange={(event) => setLocation(event.target.value)}
                  className="mt-2 w-full rounded-2xl border border-slate/20 bg-white/80 px-4 py-3 text-sm"
                  placeholder="Remote, Bengaluru, London"
                />
              </label>
              <label className="block">
                <span className="text-sm text-slate">Resume</span>
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
              {discoverMutation.isPending ? "Discovering..." : "Discover and Score Jobs"}
            </button>
          </form>
        </article>

        <article className="glass-panel p-6">
          <p className="text-sm uppercase tracking-[0.3em] text-slate">Filter Stored Jobs</p>
          <div className="mt-6 grid gap-4 md:grid-cols-2">
            <label className="block">
              <span className="text-sm text-slate">Company</span>
              <input
                value={company}
                onChange={(event) => setCompany(event.target.value)}
                className="mt-2 w-full rounded-2xl border border-slate/20 bg-white/80 px-4 py-3 text-sm"
              />
            </label>
            <label className="block">
              <span className="text-sm text-slate">Discovery Source</span>
              <select
                value={source}
                onChange={(event) => setSource(event.target.value)}
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
                value={location}
                onChange={(event) => setLocation(event.target.value)}
                className="mt-2 w-full rounded-2xl border border-slate/20 bg-white/80 px-4 py-3 text-sm"
              />
            </label>
            <label className="block">
              <span className="text-sm text-slate">Minimum Relevance Score</span>
              <input
                value={minScore}
                onChange={(event) => setMinScore(event.target.value)}
                type="number"
                min="0"
                max="100"
                className="mt-2 w-full rounded-2xl border border-slate/20 bg-white/80 px-4 py-3 text-sm"
              />
            </label>
            <label className="block">
              <span className="text-sm text-slate">ATS Type</span>
              <select
                value={atsType}
                onChange={(event) => setAtsType(event.target.value)}
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
              <p className="mt-2">Resume used: {discoverMutation.data.used_resume_id ?? "latest"}</p>
              <div className="mt-3 flex flex-wrap gap-2">
                {Object.entries(discoverMutation.data.source_counts).map(([itemSource, count]) => (
                  <span key={itemSource} className="rounded-full bg-spruce/10 px-3 py-1 text-xs text-spruce">
                    {itemSource}: {count}
                  </span>
                ))}
              </div>
            </div>
          ) : null}
        </article>
      </div>

      <article className="glass-panel p-6">
        <p className="text-sm uppercase tracking-[0.3em] text-slate">Jobs Feed</p>
        <div className="mt-6 space-y-4">
          {jobsQuery.data?.map((job) => (
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
                  <p className="text-sm uppercase tracking-[0.2em] text-slate">Relevance</p>
                  <p className="font-display text-4xl text-ink">
                    {job.relevance_score ? Math.round(job.relevance_score) : "--"}
                  </p>
                </div>
              </div>
              <p className="mt-4 line-clamp-4 text-sm leading-7 text-slate">{job.description}</p>
              <div className="mt-4 flex flex-wrap gap-2">
                {(job.ai_analysis.missing_skills ?? []).map((skill) => (
                  <span key={skill} className="rounded-full bg-rose-100 px-3 py-1 text-xs text-rose-700">
                    Missing: {skill}
                  </span>
                ))}
              </div>
              <p className="mt-4 text-sm text-slate">
                {job.ai_analysis.reasoning ?? "No reasoning stored yet."}
              </p>
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
                  onClick={() => rescoreMutation.mutate({ jobId: job.id, resumeId: resumeId || undefined })}
                  className="rounded-2xl bg-white px-4 py-2 text-sm font-medium text-ink"
                >
                  Rescore
                </button>
              </div>
            </div>
          ))}
          {jobsQuery.isLoading ? <p className="text-sm text-slate">Loading jobs...</p> : null}
          {!jobsQuery.data?.length && !jobsQuery.isLoading ? (
            <p className="text-sm text-slate">
              No jobs stored yet. Run a dynamic discovery pass or create enabled search preferences.
            </p>
          ) : null}
        </div>
      </article>
    </section>
  );
}
