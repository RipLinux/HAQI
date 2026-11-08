export type UserQuery = {
  text: string;
  language?: string;
  conversation_id?: string;
};

export type ChatRequest = { query: UserQuery };
export type Citation = { chunk_id: string; source_url?: string; label?: string };
export type Answer = {
  text: string;
  citations: Citation[];
  abstained: boolean;
  abstention_reason?: string;
};
export type ChatResponse = { answer: Answer };
