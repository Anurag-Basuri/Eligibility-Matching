import random

def balance_pairs(texts, labels, seed=42):
    random.seed(seed)

    positives = [(t, y) for t, y in zip(texts, labels) if y == 1]
    negatives = [(t, y) for t, y in zip(texts, labels) if y == 0]

    if not positives:
        raise ValueError("No positive samples found to balance.")

    k = len(positives)
    sampled_negatives = random.sample(negatives, min(k, len(negatives)))

    balanced = positives + sampled_negatives
    random.shuffle(balanced)

    X_balanced = [x for x, _ in balanced]
    y_balanced = [y for _, y in balanced]

    return X_balanced, y_balanced
