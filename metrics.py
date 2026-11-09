"""Annotation quality metrics. Pure Python, no dependencies."""

from collections import Counter


def percent_agreement(a: list[str], b: list[str]) -> float:
    """Share of items where both annotators chose the same label."""
    return sum(x == y for x, y in zip(a, b)) / len(a)


def cohens_kappa(a: list[str], b: list[str]) -> float:
    """Agreement between two annotators, corrected for chance.

    kappa = (observed - expected) / (1 - expected)
    1 = perfect agreement, 0 = no better than chance.
    """
    n = len(a)
    observed = percent_agreement(a, b)
    count_a, count_b = Counter(a), Counter(b)
    expected = sum(count_a[label] * count_b[label] for label in set(a) | set(b)) / (n * n)
    if expected == 1:
        return 1.0
    return (observed - expected) / (1 - expected)


def interpret_kappa(kappa: float) -> str:
    """Landis & Koch (1977) bands, the most commonly cited scale."""
    for limit, name in [(0.0, "poor"), (0.20, "slight"), (0.40, "fair"),
                        (0.60, "moderate"), (0.80, "substantial")]:
        if kappa <= limit:
            return name
    return "almost perfect"


def confusion_matrix(a: list[str], b: list[str], labels: list[str]) -> dict[str, dict[str, int]]:
    """Rows: annotator A's label. Columns: annotator B's label."""
    matrix = {row: {col: 0 for col in labels} for row in labels}
    for x, y in zip(a, b):
        matrix[x][y] += 1
    return matrix


def per_label_agreement(a: list[str], b: list[str], labels: list[str]) -> dict[str, tuple[float | None, int]]:
    """For each label: of the items either annotator gave that label, how many did both give it?"""
    result = {}
    for label in labels:
        either = sum(x == label or y == label for x, y in zip(a, b))
        both = sum(x == label and y == label for x, y in zip(a, b))
        result[label] = (both / either if either else None, either)
    return result


def accuracy_vs_gold(labels: list[str], gold: list[str]) -> tuple[float | None, int]:
    """Accuracy on the adjudicated spot-check sample only (items with a gold label)."""
    pairs = [(x, g) for x, g in zip(labels, gold) if g]
    if not pairs:
        return None, 0
    return sum(x == g for x, g in pairs) / len(pairs), len(pairs)


def throughput_per_hour(seconds: list[float]) -> float:
    return 3600 / (sum(seconds) / len(seconds))


def median(values: list[float]) -> float:
    ordered = sorted(values)
    mid = len(ordered) // 2
    return ordered[mid] if len(ordered) % 2 else (ordered[mid - 1] + ordered[mid]) / 2
