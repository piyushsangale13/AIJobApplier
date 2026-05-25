import { useQuery } from "@tanstack/react-query";

import { fetchApplications } from "../api/applications";

export function useApplications() {
  return useQuery({
    queryKey: ["applications"],
    queryFn: fetchApplications
  });
}
