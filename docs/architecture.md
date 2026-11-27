# Backend architecture

## FastAPI entry points

The repository currently has two FastAPI entry points:

- `backend/main.py` is the RAG-backed service entry point. The backend Dockerfile
  starts it as `main:app`, and the `/api/v1/chat` route delegates to
  `RAGOrchestratorService.process_citizen_query`.
- `backend/app/main.py` is the modular foundation API. Its chat route is still
  an explicit `501 Not Implemented` scaffold.

Use `main:app` when running or testing the active RAG chat flow. The Lovable
frontend prototype remains separate and uses simulated responses.

## Active chat flow

The active `/api/v1/chat` request follows this path:

1. The service resolves the conversation session and logs the user message.
2. `nlp_service.analyze_query` processes the question and session context.
3. `retrieval_service.retrieve_and_rerank` returns ranked legacy retrieval
   records (up to three candidates).
4. The legacy evidence validator checks source identity, relevance, freshness,
   and contradictions. It requests clarification or abstains when evidence is
   insufficient.
5. For verified evidence, the service builds structured guidance and a
   deterministic answer from the primary retrieved record.
6. Optional modular LLM generation may replace that answer. The provider is
   disabled by default. When enabled, the service builds context from the
   primary record, generates an answer, validates `[E#]` references against
   that context, and applies the legacy generated-answer grounding checks.
7. The API returns the existing `ChatResponse` schema and its legacy
   `SourceCitation` metadata for the primary record.

Provider errors, invalid evidence references, and failed grounding checks
return the deterministic answer. The modular citation validator verifies that
referenced IDs map to the supplied context. The legacy generated-answer check
uses token overlap and checks numeric claims labeled as fees or durations
against their corresponding source fields. These checks are heuristics; they
do not establish complete semantic support for every generated claim.

## Configuration

`HAQI_LLM_PROVIDER` defaults to `disabled`. Set it to `openai` to enable the
OpenAI provider, configure `OPENAI_API_KEY` through the process environment,
and optionally set `HAQI_LLM_MODEL` (default `gpt-4o-mini`). The provider uses
a 30-second request timeout. The current Docker Compose backend does not pass
these LLM variables into the container, so its default behavior remains the
deterministic path.
