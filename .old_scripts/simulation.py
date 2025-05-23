import random
from collections import defaultdict
from itertools import combinations, combinations_with_replacement
from typing import Tuple
from statistics import mean, stdev

# === Setup ===

class Potion:
    def __init__(self, id, mox, aga, lye, weight):
        self.id = id
        self.mox = mox
        self.aga = aga
        self.lye = lye
        self.weight = weight

potions = [
    Potion("AAA", 0, 20, 0, 5),
    Potion("MMM", 20, 0, 0, 5),
    Potion("LLL", 0, 0, 20, 5),
    Potion("MMA", 20, 10, 0, 4),
    Potion("MML", 20, 0, 10, 4),
    Potion("AAM", 10, 20, 0, 4),
    Potion("ALA", 0, 20, 10, 4),
    Potion("MLL", 10, 0, 20, 4),
    Potion("ALL", 0, 10, 20, 4),
    Potion("MAL", 20, 20, 20, 3),
]

potion_map = {p.id: p for p in potions}
potion_ids = list(potion_map.keys())
potion_weights = [potion_map[pid].weight for pid in potion_ids]

target = {"mox": 61050, "aga": 52550, "lye": 70500}

def bonus_for_count(n):
    return {1: 1.0, 2: 1.2, 3: 1.4}[n]

def all_subsets(draw):
    unique = set()
    for i in range(1, 4):
        for comb in combinations(draw, i):
            unique.add(tuple(sorted(comb)))
    return list(unique)

def apply_gain(subset) -> dict:
    gain = {"mox": 0, "aga": 0, "lye": 0}
    bonus = bonus_for_count(len(subset))
    for pid in subset:
        p = potion_map[pid]
        gain["mox"] += p.mox
        gain["aga"] += p.aga
        gain["lye"] += p.lye
    for r in gain:
        gain[r] = int(gain[r] * bonus)
    return gain

def resin_score(current, added):
    score = 0
    weights = {"lye": 100, "mox": 10, "aga": 1}
    for r in ["mox", "aga", "lye"]:
        before = abs(target[r] - current[r])
        after = abs(target[r] - (current[r] + added[r]))
        score += (before - after) * weights[r]
    return score

def is_done(current):
    return all(current[r] >= target[r] for r in target)

def bin_state(current: dict) -> Tuple[int, int, int]:
    return tuple(current[r] // 5000 for r in ["mox", "aga", "lye"])

# === Q-Learning ===

Q = defaultdict(lambda: defaultdict(dict))
alpha = 0.1
gamma = 0.95
epsilon = 0.1

def choose_action(state_bin, draw):
    subsets = all_subsets(draw)
    if random.random() < epsilon:
        return random.choice(subsets)
    q_vals = Q[state_bin][draw]
    return max(subsets, key=lambda a: q_vals.get(a, 0))

def train_qlearning(episodes=10000):
    for ep in range(episodes):
        current = {"mox": 0, "aga": 0, "lye": 0}
        steps = 0
        while not is_done(current):
            draw = tuple(sorted(random.choices(potion_ids, weights=potion_weights, k=3)))
            state_bin = bin_state(current)
            action = choose_action(state_bin, draw)
            gain = apply_gain(action)

            next_state = {r: current[r] + gain[r] for r in current}
            next_bin = bin_state(next_state)

            reward = resin_score(current, gain) - 1  # -1 per step
            max_q_next = max(Q[next_bin][draw].values(), default=0)

            old_q = Q[state_bin][draw].get(action, 0)
            new_q = (1 - alpha) * old_q + alpha * (reward + gamma * max_q_next)
            Q[state_bin][draw][action] = new_q

            current = next_state
            steps += 1

        if ep % 500 == 0:
            print(f"Episode {ep}, steps: {steps}")

# === Run Training ===

if __name__ == "__main__":
    train_qlearning(episodes=10000)
    # Aggregate best actions per draw across all seen state bins
    draw_action_scores = defaultdict(lambda: defaultdict(list))

    # Collect Q-values per draw-action combo
    for state_bin in Q:
        for draw in Q[state_bin]:
            for action, q in Q[state_bin][draw].items():
                draw_action_scores[draw][action].append(q)

    # Compute average Q per action and find best per draw
    print("\n=== Best Generalized Actions Per Draw ===")
    for draw in sorted(draw_action_scores.keys()):
        actions = draw_action_scores[draw]
        avg_qs = {action: mean(qs) for action, qs in actions.items()}
        best_action = max(avg_qs.items(), key=lambda kv: kv[1])
        print(f"Draw {draw}: Best action {best_action[0]} (Avg Q={best_action[1]:.2f})")

