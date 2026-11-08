# Contributing

Use the feature branches documented in `docs/git-workflow.md`; all changes require a PR and review. Use focused commits such as `feat(api): add health route`, run backend tests/lint and frontend build, and update contracts/docs when interfaces change. Manage Python dependencies with uv and keep lock files in sync. Coordinate shared files (`contracts`, `main`, Compose, and CI) in a PR rather than editing them independently. New modules belong under their functional ownership directory, never under a person's name.
