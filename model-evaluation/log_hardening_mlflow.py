import json
import time
from pathlib import Path
from urllib.parse import urlencode
from urllib.request import Request, urlopen

ROOT = Path(__file__).parent
BASE = "http://localhost:5000"
EXPERIMENT = "HAQI-Retrieval-Hardening-v1"


def post(path: str, payload: dict[str, object]) -> dict[str, object]:
    request = Request(
        BASE + path,
        data=json.dumps(payload).encode(),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urlopen(request, timeout=30) as response:
        return json.loads(response.read())


def get_experiment() -> str:
    query = urlencode({"experiment_name": EXPERIMENT})
    try:
        with urlopen(f"{BASE}/api/2.0/mlflow/experiments/get-by-name?{query}", timeout=30) as response:
            return str(json.loads(response.read())["experiment"]["experiment_id"])
    except Exception:
        return str(post("/api/2.0/mlflow/experiments/create", {"name": EXPERIMENT})["experiment_id"])


def upload(run_id: str, path: Path) -> None:
    request = Request(
        f"{BASE}/api/2.0/mlflow-artifacts/artifacts/{run_id}/{path.name}",
        data=path.read_bytes(),
        method="PUT",
    )
    with urlopen(request, timeout=60):
        pass


def log_run(experiment_id: str, name: str, model_id: str, report: dict[str, object], method: str) -> str:
    run = post(
        "/api/2.0/mlflow/runs/create",
        {
            "experiment_id": experiment_id,
            "run_name": name,
            "start_time": int(time.time() * 1000),
            "tags": [
                {"key": "dataset_status", "value": "machine_generated_pending_human_review"},
                {"key": "method", "value": method},
            ],
        },
    )
    run_id = str(run["run"]["info"]["run_id"])
    params = {
        "model_id": model_id,
        "vector_dimension": "384" if model_id != "keyword" else "n/a",
        "similarity_metric": "cosine" if model_id != "keyword" else "n/a",
        "index_type": "HNSW" if model_id != "keyword" else "n/a",
        "keyword_configuration": "token_or + simple matrix",
        "rrf_constant": "60",
        "candidate_pool": "10",
        "reranker_id": "cross-encoder/mmarco-mMiniLMv2-L12-H384-v1" if "reranked" in method else "none",
        "dataset_version": "haqi-model-comparison-synthetic-v1",
        "review_status": "pending_human_review",
    }
    for key, value in params.items():
        post("/api/2.0/mlflow/runs/log-parameter", {"run_id": run_id, "key": key, "value": value})
    for language, metrics in report["methods"][method].items():
        for metric, value in metrics.items():
            if isinstance(value, (int, float)):
                post(
                    "/api/2.0/mlflow/runs/log-metric",
                    {
                        "run_id": run_id,
                        "key": f"{language}_{metric}",
                        "value": value,
                        "timestamp": int(time.time() * 1000),
                        "step": 0,
                    },
                )
    for artifact in [ROOT / "results" / "dataset_quality_report.json", ROOT / "results" / "keyword_matrix_report.json"]:
        if artifact.exists():
            upload(run_id, artifact)
    if "e5" in method:
        upload(run_id, ROOT / "results" / "benchmark_report_e5.json")
    if "minilm" in method:
        upload(run_id, ROOT / "results" / "benchmark_report_minilm.json")
    post(
        "/api/2.0/mlflow/runs/update",
        {"run_id": run_id, "status": "FINISHED", "end_time": int(time.time() * 1000)},
    )
    return run_id


def main() -> None:
    experiment_id = get_experiment()
    e5 = json.loads((ROOT / "results" / "benchmark_report_e5.json").read_text(encoding="utf-8"))
    minilm = json.loads((ROOT / "results" / "benchmark_report_minilm.json").read_text(encoding="utf-8"))
    keyword = json.loads((ROOT / "results" / "keyword_matrix_report.json").read_text(encoding="utf-8"))
    configurations = [
        ("e5-vector", "intfloat/multilingual-e5-small", e5, "vector"),
        ("minilm-vector", "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2", minilm, "vector"),
        ("keyword-token-or", "keyword", keyword, "token_or"),
        ("e5-hybrid", "intfloat/multilingual-e5-small", e5, "hybrid"),
        ("minilm-hybrid", "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2", minilm, "hybrid"),
        ("e5-hybrid-reranked", "intfloat/multilingual-e5-small", e5, "reranked"),
        ("minilm-hybrid-reranked", "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2", minilm, "reranked"),
    ]
    run_ids = {
        name: log_run(experiment_id, name, model_id, report, method)
        for name, model_id, report, method in configurations
    }
    print(json.dumps({"experiment": EXPERIMENT, "experiment_id": experiment_id, "run_ids": run_ids}, indent=2))


if __name__ == "__main__":
    main()
