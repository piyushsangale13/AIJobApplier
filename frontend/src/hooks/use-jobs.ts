import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";

import { discoverJobs, fetchJobs, rescoreJob, tailorResume } from "../api/jobs";
import type { JobDiscoveryRequest, JobsQueryParams } from "../types/api";

export function useJobs(filters: JobsQueryParams, page: number = 1, pageSize: number = 20) {
  const params: JobsQueryParams = { ...filters, page, page_size: pageSize };
  return useQuery({
    queryKey: ["jobs", params],
    queryFn: () => fetchJobs(params),
    placeholderData: (prev) => prev
  });
}

export function useDiscoverJobs() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (payload: JobDiscoveryRequest) => discoverJobs(payload),
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: ["jobs"] });
      void queryClient.invalidateQueries({ queryKey: ["dashboard-stats"] });
    }
  });
}

export function useRescoreJob() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ jobId, resumeId }: { jobId: string; resumeId?: string }) =>
      rescoreJob(jobId, resumeId),
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: ["jobs"] });
    }
  });
}

export function useTailorResume() {
  return useMutation({
    mutationFn: ({ jobId, resumeId }: { jobId: string; resumeId?: string }) =>
      tailorResume(jobId, resumeId)
  });
}
