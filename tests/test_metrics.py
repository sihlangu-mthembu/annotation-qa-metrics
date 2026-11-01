import pathlib
import sys
import unittest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))

from metrics import (accuracy_vs_gold, cohens_kappa, interpret_kappa, percent_agreement,  # noqa: E402
                     per_label_agreement)


class KappaTests(unittest.TestCase):
    def test_textbook_example(self):
        # Classic 50-item yes/no example: 20 yes-yes, 5 yes-no, 10 no-yes, 15 no-no.
        # Observed 0.70, expected 0.50, so kappa = 0.40.
        a = ["yes"] * 25 + ["no"] * 25
        b = ["yes"] * 20 + ["no"] * 5 + ["yes"] * 10 + ["no"] * 15
        self.assertAlmostEqual(percent_agreement(a, b), 0.70)
        self.assertAlmostEqual(cohens_kappa(a, b), 0.40)

    def test_perfect_agreement(self):
        labels = ["x", "y", "x", "z"]
        self.assertAlmostEqual(cohens_kappa(labels, labels), 1.0)

    def test_interpretation_bands(self):
        self.assertEqual(interpret_kappa(0.40), "fair")
        self.assertEqual(interpret_kappa(0.75), "substantial")
        self.assertEqual(interpret_kappa(0.9), "almost perfect")


class OtherMetricTests(unittest.TestCase):
    def test_accuracy_only_uses_gold_items(self):
        acc, n = accuracy_vs_gold(["a", "b", "c"], ["a", "", "x"])
        self.assertEqual(n, 2)
        self.assertAlmostEqual(acc, 0.5)

    def test_per_label_agreement(self):
        share, either = per_label_agreement(["a", "a", "b"], ["a", "b", "b"], ["a", "b"])["a"]
        self.assertEqual(either, 2)
        self.assertAlmostEqual(share, 0.5)


if __name__ == "__main__":
    unittest.main()
