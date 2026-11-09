from pathlib import Path
from urllib.request import Request, urlopen


ROOT = Path(__file__).parent
RUNS = {
    "vector": "fa41a73e23974b85bb71114771145e5a",
    "keyword": "4c3f7de3f68e4e58847300f9bd27268b",
    "hybrid": "aed19f046ccf4a20a049b3257120f0f3",
    "reranked": "66a66069c1334171a7d2edce2ed72974",
}


def main() -> None:
    uploaded = []
    for run_id in RUNS.values():
        for path in [ROOT / "results" / "benchmark_report.json", ROOT / "results" / "benchmark_comparison.csv"]:
            url = f"http://localhost:5000/api/2.0/mlflow-artifacts/artifacts/{run_id}/{path.name}"
            request = Request(url, data=path.read_bytes(), method="PUT")
            with urlopen(request, timeout=60):
                uploaded.append((run_id, path.name))
    print({"uploaded": uploaded})


if __name__ == "__main__":
    main()
