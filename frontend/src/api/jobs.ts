import { api } from "./client";
import type {
  JobDiscoveryRequest,
  JobDiscoveryResponse,
  JobRecord,
  JobsQueryParams,
  JobScoreResponse
} from "../types/api";

export async function fetchJobs(params: JobsQueryParams): Promise<JobRecord[]> {
  const response = await api.get<JobRecord[]>("/jobs", { params });
  return response.data;
}

export async function discoverJobs(payload: JobDiscoveryRequest): Promise<JobDiscoveryResponse> {
  const response = await api.post<JobDiscoveryResponse>("/jobs/discover", payload);
  return response.data;
}

export async function rescoreJob(jobId: string, resumeId?: string): Promise<JobScoreResponse> {
  const response = await api.post<JobScoreResponse>(`/jobs/${jobId}/score`, null, {
    params: resumeId ? { resume_id: resumeId } : undefined
  });
  return response.data;
}
