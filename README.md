# annotation-qa-metrics

A small Python tool that answers the questions a human-data or QA lead asks after every labelling batch: **Do our annotators agree? Who needs feedback? Which guideline is unclear? What needs adjudication?**

It takes a CSV of labels from two annotators and produces a QA report with inter-annotator agreement (Cohen's kappa), per-label agreement, a disagreement matrix, accuracy on a spot-check sample, speed and throughput KPIs, and concrete recommendations. It also writes an adjudication queue of every item the annotators disagreed on.

## Quick start

Needs Python 3.10 or newer. No packages to install.

```bash
python run.py                      # writes reports/qa_report.md and reports/adjudication_queue.csv
python -m unittest discover tests  # run the tests
```

## Sample result

The bundled batch is **synthetic** (see below): two annotators rating 120 AI-generated responses as `helpful`, `unhelpful`, `hallucination` or `unsafe`.

- **Cohen's kappa 0.62** (substantial), raw agreement 75%; 30 items go to adjudication.
- **`hallucination` is the weakest label:** the annotators agreed on only 38% of the items either of them flagged.
- **Annotator B is faster** (120 vs 77 items an hour), but their spot-check accuracy falls from 89% to 67% on items done in under 25 seconds.
- **Recommendation:** clarify the `helpful`/`unhelpful` boundary with worked examples, address rushing, adjudicate, then re-measure kappa on the next batch.

See [`reports/qa_report.md`](reports/qa_report.md) for the full report.

## How it works

| Metric | What it tells you |
| --- | --- |
| Raw agreement | Share of items both annotators labelled the same way |
| Cohen's kappa | Agreement corrected for chance: 1 is perfect, 0 is no better than guessing. Interpreted with the Landis & Koch (1977) bands |
| Agreement by label | Which categories are ambiguous. A low score usually means the **guideline** is unclear, not that the annotators are careless |
| Disagreement matrix | Which pairs of labels get confused, so you know which boundary to clarify |
| Spot-check accuracy | Each annotator against adjudicated gold labels on a sample |
| Speed and "rushed" accuracy | Whether speed is costing quality |

## Using your own batch

Provide a CSV with these columns (see `data/labels.csv`):

```
item_id, topic, annotator_a, annotator_b, seconds_a, seconds_b, gold
```

Leave `gold` blank for items that weren't spot-checked. Change the label set in `run.py` if your project uses different categories.

```bash
python run.py --data my_batch.csv --rushed-seconds 20
```

## About the sample data

`data/labels.csv` is **generated, not real**. `generate_sample_data.py` creates it with a fixed random seed and deliberately builds in two problems for the report to find: `hallucination` and `unhelpful` are easy to confuse, and annotator B makes more mistakes when rushing. Run `python generate_sample_data.py` to recreate it.

## Limitations

- Supports exactly two annotators. For three or more you would use Fleiss' kappa or Krippendorff's alpha.
- The spot check is small (28 items), so the accuracy figures have wide error margins.
- Kappa is sensitive to how common each label is; read it alongside per-label agreement.

## Project structure

```
annotation-qa-metrics/
├── run.py                    # builds the report and adjudication queue
├── metrics.py                # kappa, agreement, accuracy, throughput
├── generate_sample_data.py   # creates the synthetic sample batch
├── data/labels.csv
├── reports/                  # qa_report.md, adjudication_queue.csv
└── tests/test_metrics.py
```

## Author

Sihlangu Mthembu, AI evaluation and data analysis. Economics & Politics, University of Cape Town.
