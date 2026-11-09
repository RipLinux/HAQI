import json
import mimetypes
import uuid
from pathlib import Path
from urllib.parse import urlencode
from urllib.request import Request, urlopen


ROOT = Path(__file__).parent
BASE = "http://localhost:5000"
EXPERIMENT = "HAQI-Retrieval-Model-Comparison-v1"


def request(path: str, payload: dict[str, object]) -> dict[str, object]:
    data = json.dumps(payload).encode()
    request = Request(
        BASE + path,
        data=data,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urlopen(request, timeout=30) as response:
        return json.loads(response.read())


def experiment_id() -> str:
    query = urlencode({"experiment_name": EXPERIMENT})
    try:
        with urlopen(f"{BASE}/api/2.0/mlflow/experiments/get-by-name?{query}", timeout=30) as response:
            return str(json.loads(response.read())["experiment"]["experiment_id"])
    except Exception:
        return str(request("/api/2.0/mlflow/experiments/create", {"name": EXPERIMENT})["experiment_id"])


def upload_artifact(run_id: str, path: Path) -> None:
    boundary = "----HAQI" + uuid.uuid4().hex
    content = path.read_bytes()
    filename = path.name
    content_type = mimetypes.guess_type(filename)[0] or "application/octet-stream"
    body = (
        f"--{boundary}\r\n"
        f'Content-Disposition: form-data; name="file"; filename="{filename}"\r\n'
        f"Content-Type: {content_type}\r\n\r\n"
    ).encode() + content + f"\r\n--{boundary}--\r\n".encode()
    query = urlencode({"run_id": run_id, "path": filename})
    request = Request(
        f"{BASE}/api/2.0/mlflow/artifacts/upload?{query}",
        data=body,
        headers={"Content-Type": f"multipart/form-data; boundary={boundary}"},
        method="POST",
    )
    with urlopen(request, timeout=60):
        pass


def main() -> None:
    report = json.loads((ROOT / "results" / "benchmark_report.json").read_text(encoding="utf-8"))
    exp_id = experiment_id()
    run_ids: dict[str, str] = {}
    for method, languages in report["methods"].items():
        run = request(
            "/api/2.0/mlflow/runs/create",
            {
                "experiment_id": exp_id,
                "run_name": f"e5-small-{method}",
                "start_time": 0,
                "tags": [
                    {"key": "dataset_status", "value": "machine_generated_pending_human_review"},
                    {"key": "embedding_model", "value": "intfloat/multilingual-e5-small"},
                    {"key": "reranker", "value": "cross-encoder/mmarco-mMiniLMv2-L12-H384-v1" if method == "reranked" else "none"},
                ],
            },
        )
        run_id = str(run["run"]["info"]["run_id"])
        run_ids[method] = run_id
        params = {
            "embedding_model_id": "intfloat/multilingual-e5-small",
            "embedding_dimensions": "384",
            "query_prefix": "query: ",
            "passage_prefix": "passage: ",
            "similarity_metric": "cosine",
            "vector_index": "HNSW",
            "keyword_configuration": "simple",
            "rrf_constant": "60",
            "top_k": "5",
            "candidate_pool": "10",
            "evaluation_dataset": "haqi-model-comparison-synthetic-v1",
        }
        for key, value in params.items():
            request("/api/2.0/mlflow/runs/log-parameter", {"run_id": run_id, "key": key, "value": value})
        for language, metrics in languages.items():
            for metric in ("recall", "precision", "mrr", "ndcg", "latency_average_ms", "latency_p50_ms", "latency_p95_ms"):
                request(
                    "/api/2.0/mlflow/runs/log-metric",
                    {"run_id": run_id, "key": f"{language}_{metric}", "value": metrics[metric], "timestamp": 0, "step": 0},
                )
        for artifact in [ROOT / "results" / "benchmark_report.json", ROOT / "results" / "benchmark_comparison.csv"]:
            try:
                upload_artifact(run_id, artifact)
            except Exception as error:
                print(f"artifact upload failed for {method}/{artifact.name}: {error}")
    print(json.dumps({"experiment": EXPERIMENT, "experiment_id": exp_id, "run_ids": run_ids}, indent=2))


if __name__ == "__main__":
    main()
