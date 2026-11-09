# Infrastructure setup

`compose.yaml` runs PostgreSQL with pgvector, MLflow, the backend, and the
frontend on the default Compose network. Containers use `postgres` and `mlflow`
as internal hostnames; host applications use `localhost`.

PostgreSQL persists to the named `postgres_data` volume and enables `vector`
from `docker/postgres/init/001-enable-pgvector.sql`. Initialization scripts run
only when the data directory is first created. To reset local development data,
stop the stack and explicitly run `docker compose down -v`; never do this
against shared or production data.

MLflow 2.17.2 uses a local SQLite backend and `/mlflow` named volume for
artifacts. Its image pins SQLAlchemy to the 2.0 line because MLflow 2.17.2
imports a pool symbol removed by SQLAlchemy 2.1.
The host tracking URL is `http://localhost:5000`; the backend container uses
`http://mlflow:5000`. Credentials are supplied through `.env`, which must not
be committed.

Start and inspect the stack:

```bash
docker compose up --build -d
docker compose ps
docker compose logs postgres
docker compose logs mlflow
```
