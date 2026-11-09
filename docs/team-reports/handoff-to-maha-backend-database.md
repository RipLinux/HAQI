# Handoff to Maha: backend and database

The retrieval adapter must use Maha's shared SQLAlchemy session and canonical
Chunk/Document ORM models; it must not create a competing engine or schema.
Please confirm table/column names, embedding storage, migrations, vector
dimension, similarity metric, index strategy, and repository/session
interfaces.

The embedding dimension is provisional until real model evaluation completes.
If 384 dimensions are selected, record which model produced them (for example,
E5-small) and keep other models in isolated indexes. Production dependencies
must remain separate from optional experiment-only model packages.

Acceptance means a shared session can index and query canonical chunks while
preserving IDs, text, metadata, and source references.
