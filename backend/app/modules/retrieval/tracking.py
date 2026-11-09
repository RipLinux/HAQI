"""Optional MLflow tracking for retrieval experiments.

MLflow is deliberately not a required import for normal unit tests. Callers must
provide an explicit tracking URI and may use a local-only no-op tracker instead.
"""

import importlib
from collections.abc import Mapping
from typing import Any


class RetrievalExperimentTracker:
    def __init__(self, tracking_uri: str | None = None, experiment_name: str = "haqi-retrieval"):
        self.tracking_uri = tracking_uri
        self.experiment_name = experiment_name

    def log_run(
        self,
        *,
        run_name: str,
        parameters: Mapping[str, Any],
        metrics: Mapping[str, float],
    ) -> str | None:
        if not self.tracking_uri:
            return None
        try:
            mlflow = importlib.import_module("mlflow")
        except ImportError as exc:
            raise RuntimeError(
                "Install the optional mlflow dependency to track experiments"
            ) from exc
        mlflow.set_tracking_uri(self.tracking_uri)
        mlflow.set_experiment(self.experiment_name)
        with mlflow.start_run(run_name=run_name) as run:
            mlflow.log_params({key: str(value) for key, value in parameters.items()})
            mlflow.log_metrics({key: float(value) for key, value in metrics.items()})
            return run.info.run_id
