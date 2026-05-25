import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";

import { discoverJobs, fetchJobs, rescoreJob } from "../api/jobs";
import type { JobDiscoveryRequest, JobsQueryParams } from "../types/api";

export function useJobs(filters: JobsQueryParams) {
  return useQuery({
    queryKey: ["jobs", filters],
    queryFn: () => fetchJobs(filters)
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
