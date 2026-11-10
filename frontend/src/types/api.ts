export type ChatRequest = {
  question: string;
  user_id?: string;
  session_id?: string | null;
  service_category?: string | null;
};

export type Citation = {
  doc_code: string;
  title: string;
  authority: string;
  original_url: string;
  last_updated?: string;
  verification_date?: string;
  version?: string;
  verification_status?: string;
  relevance_score?: number;
};

export type StructuredGuidance = {
  specific_service?: string;
  procedural_steps?: string[];
  required_documents?: string[];
  responsible_authority?: string;
  fees_and_duration?: string;
  reference_and_verification?: string;
  methodological_note?: string;
};

export type ChatResponse = {
  status: string;
  session_id: string;
  user_id: string;
  received_question: string;
  decision_type: "answered" | "clarification_needed" | "safe_abstention";
  answer: string;
  structured_guidance?: StructuredGuidance | null;
  clarification_question?: string | null;
  clarification_options?: string[];
  sources?: string[];
  citations?: Citation[];
  evidence_validation?: {
    is_sufficient?: boolean;
    abstention_reason?: string | null;
  };
};

export type ApiService = {
  chunk_id: string;
  service_slug: string;
  service_name_ar: string;
  sub_type: string;
  service_category: string;
  authority: string;
  steps: string[];
  required_documents: string[];
  eligibility_criteria: string[];
  fees_text: string;
  processing_time: string;
  source_url: string;
  last_updated: string;
  verification_date: string;
};

export type ServicesListResponse = {
  status: string;
  count: number;
  services: ApiService[];
};

export type ApiProcedure = {
  id: number;
  chunk_id: string;
  document_id: number;
  service_slug: string;
  service_name_ar: string;
  sub_type: string;
  intent_tag: string;
  chunk_text: string;
  steps_json: string;
  required_documents_json: string;
  eligibility_criteria_json: string;
  fees_text: string;
  processing_time: string;
  keywords_ar: string;
  created_at: string;
  doc_code: string;
  doc_title: string;
  authority: string;
  original_url: string;
  publication_date: string;
  last_updated: string;
  service_category: string;
  verification_date: string;
  version: string;
  is_official_verified: boolean;
  doc_status: string;
  steps: string[];
  required_documents: string[];
  eligibility_criteria: string[];
};

export type ServiceDetailsResponse = {
  status: string;
  service_slug: string;
  procedures: ApiProcedure[];
};
