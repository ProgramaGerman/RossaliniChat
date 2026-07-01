import type { ModeInfo, AnalyzeResponse } from "./types";

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export async function fetchModes(): Promise<ModeInfo[]> {
  const res = await fetch(`${API_BASE}/api/modes`);
  if (!res.ok) throw new Error("Failed to fetch modes");
  return res.json();
}

export async function analyzeImage(file: File): Promise<AnalyzeResponse> {
  const formData = new FormData();
  formData.append("file", file);
  const res = await fetch(`${API_BASE}/api/analyze`, {
    method: "POST",
    body: formData,
  });
  if (!res.ok) throw new Error("Failed to analyze image");
  return res.json();
}

export async function analyzeText(context: string): Promise<AnalyzeResponse> {
  const res = await fetch(`${API_BASE}/api/analyze/text`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ context }),
  });
  if (!res.ok) throw new Error("Failed to analyze text");
  return res.json();
}
