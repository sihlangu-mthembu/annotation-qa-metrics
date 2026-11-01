# Annotation QA report

Batch `labels.csv`: 120 items, 2 annotators, 28 items adjudicated in a spot check. Generated 2026-11-01 19:34.

## Headline

- **Cohen's kappa:** 0.62 (substantial agreement), raw agreement 75%.
- **Disagreements sent to adjudication:** 30 items (25%).
- **Weakest label:** `hallucination`, where the annotators agreed on only 38% of items either of them gave that label.
- **Accuracy on the spot check:** annotator A 86%, annotator B 82% (n = 28).

## KPIs by annotator

| Annotator | Spot-check accuracy | Median seconds/item | Throughput (items/hour) | Accuracy when rushed | Accuracy otherwise |
| --- | --- | --- | --- | --- | --- |
| A | 86% | 46 | 77 | 100% (n=1) | 85% (n=27) |
| B | 82% | 30 | 120 | 67% (n=9) | 89% (n=19) |

"Rushed" means under 25 seconds on an item.

## Agreement by label

| Label | Items either annotator chose it | Both agreed |
| --- | --- | --- |
| helpful | 69 | 67% |
| unhelpful | 46 | 52% |
| hallucination | 21 | 38% |
| unsafe | 14 | 86% |

## Where they disagree (rows: A, columns: B)

| A \ B | helpful | unhelpful | hallucination | unsafe |
| --- | --- | --- | --- | --- |
| helpful | **46** | 8 | 2 | 0 |
| unhelpful | 7 | **24** | 2 | 1 |
| hallucination | 6 | 3 | **8** | 0 |
| unsafe | 0 | 1 | 0 | **12** |

## Recommendations

1. **Clarify the guideline between `helpful` and `unhelpful`**, the most frequent disagreement pair (15 items). Add two or three worked examples of borderline cases.
2. **Address rushing for annotator B:** accuracy drops from 89% to 67% on items completed in under 25 seconds. Consider a minimum review time or targeted feedback.
3. **Adjudicate the 30 disagreements** in `adjudication_queue.csv`, then re-measure kappa on the next batch to check whether the guideline change worked.

## Caveats

- The spot check covers 28 items, so the accuracy figures have wide error margins.
- Kappa can look low when one label is rare, even if annotators rarely disagree on it.
- With the bundled sample data, all of this is from a synthetic batch; see the README.