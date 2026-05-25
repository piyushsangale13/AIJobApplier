import { api } from "./client";
import type { DashboardStats } from "../types/api";

export async function fetchDashboardStats(): Promise<DashboardStats> {
  const response = await api.get<DashboardStats>("/dashboard/stats");
  return response.data;
}
