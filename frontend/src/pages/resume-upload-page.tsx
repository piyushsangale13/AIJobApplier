import { useState } from "react";

import { useResumes, useUploadResume } from "../hooks/use-resumes";

export function ResumeUploadPage() {
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const { data: resumes } = useResumes();
  const uploadMutation = useUploadResume();

  async function handleSubmit(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!selectedFile) {
      return;
    }
    await uploadMutation.mutateAsync(selectedFile);
    setSelectedFile(null);
    event.currentTarget.reset();
  }

  return (
    <section className="grid gap-6 xl:grid-cols-[0.95fr_1.05fr]">
      <article className="glass-panel p-6">
        <p className="text-sm uppercase tracking-[0.3em] text-slate">Resume Upload</p>
        <h3 className="mt-3 font-display text-3xl">Parse your latest resume into structured data</h3>
        <form className="mt-6 space-y-4" onSubmit={handleSubmit}>
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
        <div className="mt-4 space-y-4">
          {resumes?.map((resume) => (
            <div key={resume.id} className="rounded-3xl bg-white/70 p-5">
              <div className="flex items-center justify-between gap-4">
                <div>
                  <h4 className="text-lg font-semibold text-ink">
                    {resume.parsed_data.name ?? resume.filename}
                  </h4>
                  <p className="text-sm text-slate">{resume.parsed_data.email ?? "No email detected"}</p>
                </div>
                <span className="rounded-full bg-spruce/10 px-3 py-1 text-xs uppercase tracking-[0.2em] text-spruce">
                  {resume.file_type}
                </span>
              </div>
              <p className="mt-4 text-sm leading-6 text-slate">
                {resume.summary ?? "No summary generated yet."}
              </p>
              <div className="mt-4 flex flex-wrap gap-2">
                {resume.parsed_data.skills.map((skill) => (
                  <span
                    key={skill}
                    className="rounded-full bg-ember/10 px-3 py-1 text-xs font-medium text-ember"
                  >
                    {skill}
                  </span>
                ))}
              </div>
            </div>
          ))}
          {!resumes?.length ? <p className="text-sm text-slate">No resumes uploaded yet.</p> : null}
        </div>
      </article>
    </section>
  );
}
