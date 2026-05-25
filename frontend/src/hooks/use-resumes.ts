import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";

import { fetchResumes, uploadResume } from "../api/resumes";

export function useResumes() {
  return useQuery({
    queryKey: ["resumes"],
    queryFn: fetchResumes
  });
}

export function useUploadResume() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: uploadResume,
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: ["resumes"] });
      void queryClient.invalidateQueries({ queryKey: ["dashboard-stats"] });
    }
  });
}
