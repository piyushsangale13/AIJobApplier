export interface DashboardStats {
  jobs_found_today: number;
  applications_submitted: number;
  pending_applications: number;
  failed_applications: number;
}

export interface ResumeParsedData {
  name: string | null;
  email: string | null;
  skills: string[];
  experience: string[];
  preferred_roles: string[];
  projects: string[];
  education: string[];
  keywords: string[];
  summary: string | null;
}

export interface ATSAnalysis {
  overall_score: number;
  contact_score: number;
  skills_score: number;
  experience_score: number;
  education_score: number;
  keywords_score: number;
  formatting_score: number;
  issues: string[];
  recommendations: string[];
}

export interface ResumeRecord {
  id: string;
  created_at: string;
  updated_at: string;
  filename: string;
  file_path: string;
  file_type: string;
  raw_text: string;
  parsed_data: ResumeParsedData;
  summary: string | null;
  ats_score: number | null;
  ats_analysis: ATSAnalysis | null;
}

export interface ResumeUploadResponse {
  resume: ResumeRecord;
}

export interface ApplicationRecord {
  id: string;
  created_at: string;
  updated_at: string;
  job_id: string | null;
  company: string;
  role: string;
  status: string;
  applied_at: string | null;
  resume_version: string | null;
  notes: string | null;
  screenshots: string[];
}

export interface JobRecord {
  id: string;
  created_at: string;
  updated_at: string;
  source_id: string | null;
  company: string;
  title: string;
  location: string | null;
  salary_text: string | null;
  apply_url: string;
  ats_type: string;
  source: string;
  description: string;
  posted_at: string | null;
  discovered_at: string;
  relevance_score: number | null;
  ai_analysis: {
    missing_skills?: string[];
    reasoning?: string;
    source?: string;
  };
}

export interface JobsQueryParams {
  company?: string;
  location?: string;
  ats_type?: string;
  source?: string;
  min_relevance_score?: number;
  page?: number;
  page_size?: number;
}

export interface JobsPage {
  items: JobRecord[];
  total: number;
  page: number;
  page_size: number;
  total_pages: number;
}

export interface JobDiscoveryRequest {
  keywords: string[];
  locations: string[];
  experience_levels: string[];
  sources: Array<"linkedin" | "google" | "wellfound">;
  resume_id: string | null;
  limit_per_source: number;
  remote_only: boolean;
}

export interface JobDiscoveryResponse {
  jobs: JobRecord[];
  source_counts: Record<string, number>;
  used_resume_id: string | null;
}

export interface JobScoreResponse {
  relevance_score: number;
  missing_skills: string[];
  reasoning: string;
}

export interface TailoredResumeResponse {
  tailored_resume: string;
  key_changes: string[];
  matched_keywords: string[];
}
