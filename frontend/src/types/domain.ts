export interface GovernmentService {
  id: string;
  name: string;
  cat: string;
  desc: string;
  status: "متاح" | "قريبًا";
  intro?: string;
  steps?: [string, string][];
  docs?: string[];
  duration?: string;
  notes?: string[];
}

export interface ChatMessage {
  role: "user" | "bot";
  text: string;
}
