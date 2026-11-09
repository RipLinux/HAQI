import json
import shutil
import sys
import time
from pathlib import Path

import numpy as np
import torch
from sentence_transformers import SentenceTransformer


def main() -> None:
    model_id = sys.argv[1]
    start = time.perf_counter()
    model = SentenceTransformer(model_id, device="cpu")
    initialization_s = time.perf_counter() - start
    queries = [
        "ما هي خطوات تجديد الخدمة التجريبية؟",
        "عايز أعرف إزاي أتابع حالة الطلب التجريبي",
        "How do I check the fictional service application status?",
    ]
    passages = [
        "خطوات تجديد الخدمة التجريبية موضحة هنا.",
        "متابعة حالة الطلب التجريبي متاحة من صفحة الحالة.",
        "The fictional service status can be checked here.",
    ]
    query_start = time.perf_counter()
    query_embeddings = model.encode(
        queries, normalize_embeddings=True, convert_to_numpy=True, batch_size=3
    )
    query_latency_s = time.perf_counter() - query_start
    passage_start = time.perf_counter()
    passage_embeddings = model.encode(
        passages, normalize_embeddings=True, convert_to_numpy=True, batch_size=3
    )
    passage_latency_s = time.perf_counter() - passage_start
    batch = passages * 8
    batch_start = time.perf_counter()
    model.encode(batch, normalize_embeddings=True, convert_to_numpy=True, batch_size=8)
    batch_latency_s = time.perf_counter() - batch_start
    usage = shutil.disk_usage(Path.cwd())
    print(
        json.dumps(
            {
                "model_id": model_id,
                "python": sys.version,
                "torch": torch.__version__,
                "dimensions": int(query_embeddings.shape[1]),
                "initialization_s": initialization_s,
                "query_latency_s": query_latency_s,
                "passage_latency_s": passage_latency_s,
                "batch_count": len(batch),
                "batch_latency_s": batch_latency_s,
                "batch_items_per_s": len(batch) / batch_latency_s,
                "query_norms": np.linalg.norm(query_embeddings, axis=1).round(6).tolist(),
                "passage_norms": np.linalg.norm(passage_embeddings, axis=1).round(6).tolist(),
                "free_gb_after": round(usage.free / 1024**3, 3),
            },
            ensure_ascii=False,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
