import math


def sigmoid(x: float):
    return 1 / (1 + math.exp(-x))


def normalize_score(score_dict: dict[int, float], duration_dict: dict[int, float]) -> dict[int, float]:
    mean_score = sum(score_dict.values()) / len(score_dict)
    threshold = mean_score * 0.95

    steepness = 0.5
    high_reward = 1.0
    low_reward = 0.01

    adjusted_scores: dict[int, float] = {}
    for uid, score in score_dict.items():
        normalized_score = (score - threshold) * steepness
        reward_ratio = sigmoid(normalized_score)
        adjusted_score = low_reward + (high_reward - low_reward) * reward_ratio

        if score > threshold:
            duration = duration_dict.get(uid, 5)
            bonus = 0.5 - duration * 0.1
            if bonus > 0:
                adjusted_score = adjusted_score * (1 + bonus)
        adjusted_scores[uid] = adjusted_score

    return adjusted_scores


def weight_score(score_dict: dict[int, float]) -> dict[int, float]:
    scores = sum(score_dict.values())

    weights: dict[int, int] = {}
    for uid, score in score_dict.items():
        weight = int(score * 3000 / scores)
        weights[uid] = weight
    return weights
