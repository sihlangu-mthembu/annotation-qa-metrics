"""Generate the SYNTHETIC sample dataset in data/labels.csv.

Two annotators label 120 AI-generated responses into four quality categories.
The "true" label is known for every item so we can simulate a QA spot-check,
where a reviewer adjudicates a random sample.

Error behaviour is deliberately built in so the QA report has something to find:
- 'hallucination' and 'unhelpful' are easy to confuse with each other;
- annotator_b is faster and makes more mistakes when rushing (< 25 seconds).

Run:  python generate_sample_data.py   (deterministic: seed 42)
"""

import csv
import pathlib
import random

LABELS = ["helpful", "unhelpful", "hallucination", "unsafe"]
CONFUSABLE = {
    "helpful": ["unhelpful"],
    "unhelpful": ["hallucination", "helpful"],
    "hallucination": ["unhelpful", "helpful"],
    "unsafe": ["unhelpful"],
}
TOPICS = ["billing", "travel", "health info", "coding", "history", "recipes"]
BASE_ACCURACY = {"helpful": 0.93, "unhelpful": 0.80, "hallucination": 0.74, "unsafe": 0.95}


def annotate(rng, true_label, accuracy, rushed_penalty, seconds):
    p = accuracy - (rushed_penalty if seconds < 25 else 0)
    return true_label if rng.random() < p else rng.choice(CONFUSABLE[true_label])


def main():
    rng = random.Random(42)
    rows = []
    for i in range(1, 121):
        true_label = rng.choices(LABELS, weights=[45, 30, 18, 7])[0]
        time_a = max(15, int(rng.gauss(48, 12)))
        time_b = max(8, int(rng.gauss(30, 10)))
        rows.append({
            "item_id": f"r{i:03d}",
            "topic": rng.choice(TOPICS),
            "annotator_a": annotate(rng, true_label, BASE_ACCURACY[true_label], 0.0, time_a),
            "annotator_b": annotate(rng, true_label, BASE_ACCURACY[true_label] - 0.03, 0.20, time_b),
            "seconds_a": time_a,
            "seconds_b": time_b,
            "gold": true_label if rng.random() < 0.25 else "",  # 25% spot-check sample
        })
    out = pathlib.Path(__file__).resolve().parent / "data" / "labels.csv"
    with open(out, "w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    print(f"wrote {len(rows)} synthetic items to {out.name}")


if __name__ == "__main__":
    main()
