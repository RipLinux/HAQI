import json
import shutil
import sys
import time
from pathlib import Path

from sentence_transformers import CrossEncoder


def main() -> None:
    model_id = sys.argv[1]
    start = time.perf_counter()
    model = CrossEncoder(model_id, device="cpu")
    initialization_s = time.perf_counter() - start
    pairs = [
        ["ما هي خطوات تجديد الخدمة التجريبية؟", "خطوات تجديد الخدمة التجريبية موضحة هنا."],
        ["عايز أعرف إزاي أتابع حالة الطلب التجريبي", "متابعة حالة الطلب التجريبي متاحة من صفحة الحالة."],
        ["How do I check the fictional service application status?", "The fictional service status can be checked here."],
    ]
    score_start = time.perf_counter()
    scores = model.predict(pairs, batch_size=3, show_progress_bar=False)
    score_latency_s = time.perf_counter() - score_start
    batch = pairs * 8
    batch_start = time.perf_counter()
    model.predict(batch, batch_size=8, show_progress_bar=False)
    batch_latency_s = time.perf_counter() - batch_start
    usage = shutil.disk_usage(Path.cwd())
    print(
        json.dumps(
            {
                "model_id": model_id,
                "python": sys.version,
                "scores": [float(score) for score in scores],
                "initialization_s": initialization_s,
                "score_latency_s": score_latency_s,
                "batch_count": len(batch),
                "batch_latency_s": batch_latency_s,
                "batch_pairs_per_s": len(batch) / batch_latency_s,
                "free_gb_after": round(usage.free / 1024**3, 3),
            },
            ensure_ascii=False,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
