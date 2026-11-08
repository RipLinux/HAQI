# Git workflow

Use `main` as the protected integration branch. Feature branches are `feat/rag-pipeline`, `feat/data-ingestion`, `feat/arabic-nlp`, `feat/retrieval-infrastructure`, `feat/frontend-setup`, and `feat/backend-setup`. Work from an updated `main`, commit with `feat(module): description`, push the feature branch, and open a PR targeting `main`. Direct pushes to `main` are prohibited; an administrator must enable branch protection.
