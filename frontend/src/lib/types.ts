export interface ModeInfo {
  key: string;
  icon: string;
  label: string;
  description: string;
}

export interface AnalyzeResponse {
  modes: Record<string, string>;
  conversation?: Record<string, unknown> | null;
  context?: string | null;
}
