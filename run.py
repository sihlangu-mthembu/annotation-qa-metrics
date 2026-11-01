"""annotation-qa-metrics: quality report for a two-annotator labelling batch.

Usage:
    python run.py                        # uses data/labels.csv
    python run.py --data my_batch.csv    # your own batch (same columns)
    python run.py --rushed-seconds 20    # change the "rushed" threshold

Writes reports/qa_report.md and reports/adjudication_queue.csv.
"""

import argparse
import csv
import datetime
import pathlib

from metrics import (accuracy_vs_gold, cohens_kappa, confusion_matrix, interpret_kappa, median,
                     per_label_agreement, percent_agreement, throughput_per_hour)

ROOT = pathlib.Path(__file__).resolve().parent
LABELS = ["helpful", "unhelpful", "hallucination", "unsafe"]


def load(path):
    with open(path, newline="", encoding="utf-8") as fh:
        rows = list(csv.DictReader(fh))
    for r in rows:
        r["seconds_a"], r["seconds_b"] = int(r["seconds_a"]), int(r["seconds_b"])
    return rows


def pct(x):
    return "n/a" if x is None else f"{x:.0%}"


def rushed_split(rows, who, threshold):
    """Accuracy against gold for rushed vs normal items, for one annotator."""
    out = {}
    for name, test in [("rushed", lambda s: s < threshold), ("normal", lambda s: s >= threshold)]:
        sample = [r for r in rows if r["gold"] and test(r[f"seconds_{who}"])]
        correct = sum(r[f"annotator_{who}"] == r["gold"] for r in sample)
        out[name] = (correct / len(sample) if sample else None, len(sample))
    return out


def build_report(rows, threshold, data_name):
    a = [r["annotator_a"] for r in rows]
    b = [r["annotator_b"] for r in rows]
    gold = [r["gold"] for r in rows]
    kappa = cohens_kappa(a, b)
    agree = percent_agreement(a, b)
    per_label = per_label_agreement(a, b, LABELS)
    acc_a, n_gold = accuracy_vs_gold(a, gold)
    acc_b, _ = accuracy_vs_gold(b, gold)
    rushed = {w: rushed_split(rows, w, threshold) for w in ("a", "b")}
    disagreements = sum(x != y for x, y in zip(a, b))

    weakest = min((v for v in per_label.items() if v[1][0] is not None), key=lambda kv: kv[1][0])
    lines = [
        "# Annotation QA report",
        "",
        f"Batch `{data_name}`: {len(rows)} items, 2 annotators, {n_gold} items adjudicated in a spot check. "
        f"Generated {datetime.datetime.now():%Y-%m-%d %H:%M}.",
        "",
        "## Headline",
        "",
        f"- **Cohen's kappa:** {kappa:.2f} ({interpret_kappa(kappa)} agreement), raw agreement {agree:.0%}.",
        f"- **Disagreements sent to adjudication:** {disagreements} items ({disagreements / len(rows):.0%}).",
        f"- **Weakest label:** `{weakest[0]}`, where the annotators agreed on only {pct(weakest[1][0])} of items either of them gave that label.",
        f"- **Accuracy on the spot check:** annotator A {pct(acc_a)}, annotator B {pct(acc_b)} (n = {n_gold}).",
        "",
        "## KPIs by annotator",
        "",
        "| Annotator | Spot-check accuracy | Median seconds/item | Throughput (items/hour) | Accuracy when rushed | Accuracy otherwise |",
        "| --- | --- | --- | --- | --- | --- |",
    ]
    for who in ("a", "b"):
        secs = [r[f"seconds_{who}"] for r in rows]
        acc = acc_a if who == "a" else acc_b
        r_acc, r_n = rushed[who]["rushed"]
        n_acc, n_n = rushed[who]["normal"]
        lines.append(f"| {who.upper()} | {pct(acc)} | {median(secs):.0f} | {throughput_per_hour(secs):.0f} | "
                     f"{pct(r_acc)} (n={r_n}) | {pct(n_acc)} (n={n_n}) |")
    lines += [f"", f"\"Rushed\" means under {threshold} seconds on an item.", "",
              "## Agreement by label", "",
              "| Label | Items either annotator chose it | Both agreed |", "| --- | --- | --- |"]
    for label, (share, either) in per_label.items():
        lines.append(f"| {label} | {either} | {pct(share)} |")

    matrix = confusion_matrix(a, b, LABELS)
    lines += ["", "## Where they disagree (rows: A, columns: B)", "",
              "| A \\ B | " + " | ".join(LABELS) + " |", "| --- | " + " | ".join("---" for _ in LABELS) + " |"]
    for row in LABELS:
        cells = [f"**{matrix[row][col]}**" if row == col else str(matrix[row][col]) for col in LABELS]
        lines.append(f"| {row} | " + " | ".join(cells) + " |")

    top_pairs = sorted(((matrix[r][c] + matrix[c][r], r, c) for i, r in enumerate(LABELS)
                        for c in LABELS[i + 1:]), reverse=True)[:2]
    lines += ["", "## Recommendations", ""]
    lines.append(f"1. **Clarify the guideline between `{top_pairs[0][1]}` and `{top_pairs[0][2]}`**, the most frequent "
                 f"disagreement pair ({top_pairs[0][0]} items). Add two or three worked examples of borderline cases.")
    worse = "B" if (acc_b or 0) < (acc_a or 0) else "A"
    wr = rushed[worse.lower()]["rushed"]
    wn = rushed[worse.lower()]["normal"]
    if wr[0] is not None and wn[0] is not None and wr[0] < wn[0]:
        lines.append(f"2. **Address rushing for annotator {worse}:** accuracy drops from {pct(wn[0])} to {pct(wr[0])} on items "
                     f"completed in under {threshold} seconds. Consider a minimum review time or targeted feedback.")
    else:
        lines.append(f"2. **Give annotator {worse} targeted feedback** using their disagreements in the adjudication queue.")
    lines.append(f"3. **Adjudicate the {disagreements} disagreements** in `adjudication_queue.csv`, then re-measure kappa "
                 f"on the next batch to check whether the guideline change worked.")
    lines += ["", "## Caveats", "",
              f"- The spot check covers {n_gold} items, so the accuracy figures have wide error margins.",
              "- Kappa can look low when one label is rare, even if annotators rarely disagree on it.",
              "- With the bundled sample data, all of this is from a synthetic batch; see the README."]
    return "\n".join(lines)


def write_queue(rows, path):
    with open(path, "w", newline="", encoding="utf-8") as fh:
        writer = csv.writer(fh)
        writer.writerow(["item_id", "topic", "annotator_a", "annotator_b", "gold_if_known"])
        for r in rows:
            if r["annotator_a"] != r["annotator_b"]:
                writer.writerow([r["item_id"], r["topic"], r["annotator_a"], r["annotator_b"], r["gold"]])


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--data", default=ROOT / "data" / "labels.csv")
    parser.add_argument("--rushed-seconds", type=int, default=25)
    parser.add_argument("--out", default=ROOT / "reports")
    args = parser.parse_args()

    rows = load(args.data)
    out = pathlib.Path(args.out)
    out.mkdir(exist_ok=True)
    report = build_report(rows, args.rushed_seconds, pathlib.Path(args.data).name)
    (out / "qa_report.md").write_text(report, encoding="utf-8")
    write_queue(rows, out / "adjudication_queue.csv")
    print(report.split("## KPIs")[0].strip())
    print(f"\nFull report: {out / 'qa_report.md'}")


if __name__ == "__main__":
    main()
