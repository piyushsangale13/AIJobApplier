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
}

export interface ResumeUploadResponse {
  resume: ResumeRecord;
}

export interface ApplicationRecord {
  id: string;
  created_at: string;
  updated_at: string;
  company: string;
  role: string;
  status: string;
  applied_at: string | null;
  resume_version: string | null;
  notes: string | null;
  screenshots: string[];
}
