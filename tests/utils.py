import unittest

from mosaic_subnet.validator.utils import normalize_score


class TestUtils(unittest.TestCase):
    def test_normalize_score(self):
        score_dict = {
            0: 18.6783,
            1: 14.7374,
            2: 19.3978,
            3: 34.5924,
            4: 36.6691,
            5: 35.6634,
            6: 33.9311,
            7: 37.4565,
            8: 27.6466
        }
        normalized_scores = normalize_score(score_dict, {1: 0.1, 6: 1})
        print("normalized_score:", normalized_scores)

        scores = sum(normalized_scores.values())

        weights: dict[int, int] = {}
        for uid, score in normalized_scores.items():
            weight = int(score * 1000 / scores)
            weights[uid] = weight

        print(list(zip(weights.keys(), weights.values())))

        # uid 6 should get the highest score as it response in 1 second
        self.assertEqual(max(weights.values()), weights[6])

        # the weight of uid 0,1,2 should be less than 5
        self.assertLess(weights[0], 5)
        self.assertLess(weights[1], 5)
        self.assertLess(weights[2], 5)


if __name__ == '__main__':
    unittest.main()
