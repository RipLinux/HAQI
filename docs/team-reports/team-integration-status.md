# Team integration status

| Member | Required delivery | Why Anas needs it | Status | Next action |
|---|---|---|---|---|
| Mohamed Hussein | Chunk/Document contracts and processed data | Index stable IDs, text, and citations | WAITING | Confirm canonical schema and export |
| Ahmed Rabie | NLP query contract | Select one canonical retrieval query | WAITING | Confirm normalized/re-written field and clarification behavior |
| Maha | ORM/session integration | Connect the adapter to production storage | WAITING | Agree model, session, dimension, metric, and index |
| Hassan | Retrieval-to-RAG contract | Pass ranked evidence and citations | WAITING | Confirm result fields, candidate pool, and empty-result behavior |
| Heba | Docker/API coordination | Integrate the application without direct DB access | WAITING | Confirm API base URL, port, and citation display |

Retrieval hardening is VERIFIED for isolated synthetic execution. Production
integration remains WAITING because Mohamed's canonical Chunk/Document mapping,
Ahmed's canonical processed-query field, Maha's ORM/session contract, Hassan's
retrieval-to-RAG fields, and Heba's API confirmation have not been confirmed
in this repository.

No teammate is marked READY or VERIFIED without explicit owner confirmation.
