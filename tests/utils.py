import unittest
from random import randint

from mosaic_subnet.validator.utils import normalize_score, weight_score


class TestUtils(unittest.TestCase):
    def test_normalize_score(self):
        score_dict = {}
        for i in range(300):
            score_dict[i] = randint(28, 35)

        score_dict[0] = 10
        score_dict[1] = 35
        normalized_scores = normalize_score(score_dict, {0: 0.1, 1: 1})
        print("normalized_score:", normalized_scores)

        weights = weight_score(normalized_scores)
        print("weights", weights)

        scores = list(weights.values())
        max_score = max(scores)

        self.assertEqual(weights[0], 0)
        self.assertEqual(weights[1], max_score)
        self.assertGreater(min(scores[1:]), 0)


if __name__ == '__main__':
    unittest.main()
