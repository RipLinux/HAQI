import type {
  ChatRequest,
  ChatResponse,
  ServicesListResponse,
  ServiceDetailsResponse,
} from "../types/api";

const API_URL = import.meta.env.VITE_API_URL ?? "http://localhost:8000/api/v1";

export async function sendChat(request: ChatRequest): Promise<ChatResponse> {
  const response = await fetch(`${API_URL}/chat`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(request),
  });

  if (!response.ok) {
    throw new Error(`Chat request failed with status ${response.status}`);
  }

  return response.json() as Promise<ChatResponse>;
}

export async function getServices(): Promise<ServicesListResponse> {
  const response = await fetch(`${API_URL}/services`);

  if (!response.ok) {
    throw new Error(`Services request failed with status ${response.status}`);
  }

  return response.json() as Promise<ServicesListResponse>;
}

export async function getServiceDetails(
  slug: string
): Promise<ServiceDetailsResponse> {
  const response = await fetch(
    `${API_URL}/services/${encodeURIComponent(slug)}`
  );

  if (!response.ok) {
    throw new Error(`Service details request failed with status ${response.status}`);
  }

  return response.json() as Promise<ServiceDetailsResponse>;
}
