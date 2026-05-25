import { api } from "./client";
import type { ResumeRecord, ResumeUploadResponse } from "../types/api";

export async function fetchResumes(): Promise<ResumeRecord[]> {
  const response = await api.get<ResumeRecord[]>("/resumes");
  return response.data;
}

export async function uploadResume(file: File): Promise<ResumeUploadResponse> {
  const formData = new FormData();
  formData.append("file", file);
  const response = await api.post<ResumeUploadResponse>("/resumes/upload", formData, {
    headers: {
      "Content-Type": "multipart/form-data"
    }
  });
  return response.data;
}
