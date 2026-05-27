import { useState } from "react";

import { useResumes, useUploadResume } from "../hooks/use-resumes";
import type { ATSAnalysis, ResumeRecord } from "../types/api";

function atsColor(score: number) {
  if (score >= 75) return { ring: "ring-spruce/40", text: "text-spruce", bg: "bg-spruce/10" };
  if (score >= 50) return { ring: "ring-amber-400/40", text: "text-amber-600", bg: "bg-amber-50" };
  return { ring: "ring-rose-400/40", text: "text-rose-600", bg: "bg-rose-50" };
}

function ATSBadge({ score }: { score: number }) {
  const c = atsColor(score);
  return (
    <span className={`shrink-0 inline-flex items-center gap-1 rounded-full ring-1 ${c.ring} ${c.bg} px-2.5 py-0.5 text-xs font-semibold ${c.text}`}>
      ATS {score}
    </span>
  );
}

function ATSBreakdown({ analysis }: { analysis: ATSAnalysis }) {
  const dimensions = [
    { label: "Contact", score: analysis.contact_score, max: 15 },
    { label: "Skills", score: analysis.skills_score, max: 20 },
    { label: "Experience", score: analysis.experience_score, max: 25 },
    { label: "Education", score: analysis.education_score, max: 15 },
    { label: "Keywords", score: analysis.keywords_score, max: 15 },
    { label: "Formatting", score: analysis.formatting_score, max: 10 },
  ];
  const c = atsColor(analysis.overall_score);

  return (
    <div className="space-y-3">
      {/* Overall score bar */}
      <div className="flex items-center gap-3">
        <span className={`text-2xl font-bold ${c.text}`}>{analysis.overall_score}</span>
        <div className="flex-1">
          <div className="h-2 w-full rounded-full bg-slate/10">
            <div
              className={`h-2 rounded-full transition-all ${analysis.overall_score >= 75 ? "bg-spruce" : analysis.overall_score >= 50 ? "bg-amber-400" : "bg-rose-500"}`}
              style={{ width: `${analysis.overall_score}%` }}
            />
          </div>
          <p className="mt-0.5 text-xs text-slate">ATS Compatibility Score</p>
        </div>
      </div>

      {/* Dimension breakdown */}
      <div className="grid grid-cols-2 gap-x-4 gap-y-1.5">
        {dimensions.map((d) => (
          <div key={d.label} className="flex items-center gap-2">
            <div className="flex-1">
              <div className="flex justify-between text-xs text-slate mb-0.5">
                <span>{d.label}</span>
                <span className="font-medium text-ink">{d.score}/{d.max}</span>
              </div>
              <div className="h-1.5 w-full rounded-full bg-slate/10">
                <div
                  className="h-1.5 rounded-full bg-spruce/60"
                  style={{ width: `${(d.score / d.max) * 100}%` }}
                />
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* Issues */}
      {analysis.issues.length > 0 && (
        <div>
          <p className="mb-1 text-xs font-semibold uppercase tracking-[0.2em] text-rose-600/70">Issues</p>
          <ul className="space-y-0.5">
            {analysis.issues.map((issue, i) => (
              <li key={i} className="flex gap-1.5 text-xs text-slate">
                <span className="mt-0.5 shrink-0 text-rose-500">✕</span>
                {issue}
              </li>
            ))}
          </ul>
        </div>
      )}

      {/* Recommendations */}
      {analysis.recommendations.length > 0 && (
        <div>
          <p className="mb-1 text-xs font-semibold uppercase tracking-[0.2em] text-spruce/70">Recommendations</p>
          <ul className="space-y-0.5">
            {analysis.recommendations.map((rec, i) => (
              <li key={i} className="flex gap-1.5 text-xs text-slate">
                <span className="mt-0.5 shrink-0 text-spruce">→</span>
                {rec}
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}

function Section({ title, items }: { title: string; items: string[] }) {
  if (!items.length) return null;
  return (
    <div>
      <p className="mb-1 text-xs font-semibold uppercase tracking-[0.2em] text-slate/70">{title}</p>
      <ul className="space-y-0.5">
        {items.map((item, i) => (
          <li key={i} className="flex gap-1.5 text-sm text-ink">
            <span className="mt-1 h-1.5 w-1.5 shrink-0 rounded-full bg-spruce/60" />
            <span className="leading-snug">{item}</span>
          </li>
        ))}
      </ul>
    </div>
  );
}

function ResumeCard({ resume }: { resume: ResumeRecord }) {
  const [expanded, setExpanded] = useState(false);
  const pd = resume.parsed_data;

  const uploadedAt = new Date(resume.created_at).toLocaleDateString("en-IN", {
    day: "numeric",
    month: "short",
    year: "numeric",
  });

  const skillPreview = pd.skills.slice(0, 4);
  const extraSkills = pd.skills.length - skillPreview.length;

  return (
    <div className="rounded-3xl bg-white/70 overflow-hidden">
      {/* Collapsed header — always visible */}
      <button
        onClick={() => setExpanded((v) => !v)}
        className="w-full text-left px-5 py-4 flex items-center justify-between gap-4 hover:bg-white/50 transition"
      >
        <div className="min-w-0 flex-1">
          <div className="flex items-center gap-2 flex-wrap">
            <h4 className="font-semibold text-ink">{pd.name ?? resume.filename}</h4>
            <span className="rounded-full bg-spruce/10 px-2.5 py-0.5 text-xs uppercase tracking-[0.15em] text-spruce">
              {resume.file_type}
            </span>
            {resume.ats_score != null && <ATSBadge score={resume.ats_score} />}
          </div>
          <div className="mt-0.5 flex flex-wrap items-center gap-x-2 gap-y-0.5 text-xs text-slate">
            {pd.email && <span>{pd.email}</span>}
            {pd.email && <span className="text-slate/40">·</span>}
            <span>{uploadedAt}</span>
            {skillPreview.length > 0 && <span className="text-slate/40">·</span>}
            {skillPreview.length > 0 && (
              <span>
                {skillPreview.join(", ")}
                {extraSkills > 0 && ` +${extraSkills}`}
              </span>
            )}
          </div>
        </div>
        <span className="shrink-0 text-slate text-xs">{expanded ? "▲" : "▼"}</span>
      </button>

      {/* Expanded detail panel */}
      {expanded && (
        <div className="px-5 pb-5 space-y-4 border-t border-slate/10">
          {resume.ats_analysis && (
            <div className="pt-4">
              <ATSBreakdown analysis={resume.ats_analysis} />
            </div>
          )}

          {resume.summary && (
            <p className="text-sm leading-6 text-slate border-t border-slate/10 pt-4">{resume.summary}</p>
          )}

          {pd.preferred_roles.length > 0 && (
            <div className="flex flex-wrap gap-2">
              {pd.preferred_roles.map((role) => (
                <span key={role} className="rounded-full bg-ink/5 px-3 py-1 text-xs font-medium text-ink">
                  {role}
                </span>
              ))}
            </div>
          )}

          {(pd.experience.length > 0 || pd.education.length > 0) && (
            <div className="grid gap-4 sm:grid-cols-2">
              <Section title="Experience" items={pd.experience} />
              <Section title="Education" items={pd.education} />
            </div>
          )}

          <Section title="Projects" items={pd.projects} />

          {pd.skills.length > 0 && (
            <div>
              <p className="mb-2 text-xs font-semibold uppercase tracking-[0.2em] text-slate/70">Skills</p>
              <div className="flex flex-wrap gap-2">
                {pd.skills.map((skill) => (
                  <span key={skill} className="rounded-full bg-ember/10 px-3 py-1 text-xs font-medium text-ember">
                    {skill}
                  </span>
                ))}
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
}

export function ResumeUploadPage() {
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const { data: resumes } = useResumes();
  const uploadMutation = useUploadResume();

  return (
    <section className="grid items-start gap-6 xl:grid-cols-[0.95fr_1.05fr]">
      <article className="glass-panel p-6">
        <p className="text-sm uppercase tracking-[0.3em] text-slate">Resume Upload</p>
        <h3 className="mt-3 font-display text-3xl">Parse your latest resume into structured data</h3>
        <form
          className="mt-6 space-y-4"
          onSubmit={async (event) => {
            event.preventDefault();
            if (!selectedFile) return;
            await uploadMutation.mutateAsync(selectedFile);
            setSelectedFile(null);
            event.currentTarget.reset();
          }}
        >
          <label className="block rounded-3xl border border-dashed border-slate/30 bg-white/70 p-6">
            <span className="text-sm text-slate">Upload a PDF or DOCX resume</span>
            <input
              type="file"
              accept=".pdf,.docx"
              className="mt-4 block w-full text-sm"
              onChange={(event) => setSelectedFile(event.target.files?.[0] ?? null)}
            />
          </label>
          <button
            type="submit"
            disabled={!selectedFile || uploadMutation.isPending}
            className="rounded-2xl bg-ink px-5 py-3 text-sm font-medium text-mist transition hover:bg-slate disabled:cursor-not-allowed disabled:opacity-60"
          >
            {uploadMutation.isPending ? "Parsing..." : "Upload and Parse Resume"}
          </button>
          {uploadMutation.error ? (
            <p className="text-sm text-rose-600">Upload failed. Check backend logs and file format.</p>
          ) : null}
        </form>
      </article>

      <article className="glass-panel p-6">
        <p className="text-sm uppercase tracking-[0.3em] text-slate">Parsed Resumes</p>
        <div className="mt-4 max-h-[70vh] space-y-4 overflow-y-auto pr-1">
          {resumes?.map((resume) => (
            <ResumeCard key={resume.id} resume={resume} />
          ))}
          {!resumes?.length ? <p className="text-sm text-slate">No resumes uploaded yet.</p> : null}
        </div>
      </article>
    </section>
  );
}
