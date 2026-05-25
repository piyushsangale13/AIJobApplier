import { api } from "./client";
import type { ApplicationRecord } from "../types/api";

export async function fetchApplications(): Promise<ApplicationRecord[]> {
  const response = await api.get<ApplicationRecord[]>("/applications");
  return response.data;
}
