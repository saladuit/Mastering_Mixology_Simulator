import random
from collections import defaultdict, Counter
from itertools import combinations, product
from typing import Tuple
from statistics import mean
import csv

# === Setup ===
def load_combo_scores(filename="final_combo_scores.csv"):
    combo_scores = {}
    try:
        with open(filename, newline="") as csvfile:
            reader = csv.reader(csvfile)
            next(reader)  # skip header
            for row in reader:
                combo = tuple(row[0].split("-"))
                score = float(row[1])
                combo_scores[combo] = score
    except FileNotFoundError:
        print(f"File '{filename}' not found, starting fresh.")
    return combo_scores
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

def is_done(current):
    return all(current[r] >= target[r] for r in target)

# === Learning with Combo Scores ===

def run_episode(combo_scores, alpha=0.1, epsilon=0.1, baseline=0.0):
    current = {"mox": 0, "aga": 0, "lye": 0}
    total_potions_used = 0
    chosen_combos = []

    while not is_done(current):
        draw = tuple(sorted(random.choices(potion_ids, weights=potion_weights, k=3)))
        subsets = all_subsets(draw)

        scores = [combo_scores.get(subset, 0.0) for subset in subsets]

        if random.random() < epsilon:
            chosen_subset = random.choice(subsets)
        else:
            total_score = sum(scores)
            if total_score == 0:
                probs = [1 / len(subsets)] * len(subsets)
            else:
                # Shift scores to positive for probabilities
                min_score = min(scores)
                if min_score < 0:
                    shifted_scores = [s - min_score + 1e-3 for s in scores]
                else:
                    shifted_scores = scores
                total_shifted = sum(shifted_scores)
                probs = [s / total_shifted for s in shifted_scores]
            chosen_subset = random.choices(subsets, weights=probs, k=1)[0]

        gain = apply_gain(chosen_subset)
        for r in current:
            current[r] += gain[r]

        total_potions_used += len(chosen_subset)
        chosen_combos.append(chosen_subset)

    episode_score = 1 / total_potions_used

    counts = Counter(chosen_combos)
    for combo, count in counts.items():
        old_score = combo_scores.get(combo, 0.0)
        # Update with baseline subtraction to provide negative feedback
        combo_scores[combo] = old_score + alpha * (episode_score - baseline) * count

    return total_potions_used, len(counts), current

def train(episodes=500000, alpha=0.1, epsilon=0.1, print_interval=100):
    combo_scores = dict()
    # combo_scores = load_combo_scores()
    stats = []
    window_size = 50
    recent_scores = []
    recent_potions = []
    min_potions_ever = float('inf')
    baseline = 0.0

    for ep in range(1, episodes + 1):
        potions_used, unique_combos, final_resources = run_episode(combo_scores, alpha=alpha, epsilon=epsilon, baseline=baseline)

        episode_score = 1 / potions_used
        recent_scores.append(episode_score)
        if len(recent_scores) > 100:
            recent_scores.pop(0)
        baseline = mean(recent_scores)

        recent_potions.append(potions_used)
        if len(recent_potions) > window_size:
            recent_potions.pop(0)
        moving_avg = mean(recent_potions)

        if potions_used < min_potions_ever:
            min_potions_ever = potions_used

        stats.append({
            "episode": ep,
            "potions_used": potions_used,
            "moving_avg_potions_used": moving_avg,
            "min_potions_used_so_far": min_potions_ever,
            "unique_combos_used": unique_combos,
            "total_mox": final_resources["mox"],
            "total_aga": final_resources["aga"],
            "total_lye": final_resources["lye"],
        })

        if ep % print_interval == 0:
            print(
        f"Episode {ep}: potions used = {potions_used}, moving avg = {moving_avg:.2f}, "
        f"min so far = {min_potions_ever}, unique combos = {unique_combos}, "
        f"total mox = {final_resources['mox']}, "
        f"aga = {final_resources['aga']}, "
        f"lye = {final_resources['lye']}"
    )    # Save stats to CSV
    with open("training_stats.csv", "w", newline="") as csvfile:
        fieldnames = [
            "episode", "potions_used", "moving_avg_potions_used",
            "min_potions_used_so_far", "unique_combos_used",
            "total_mox", "total_aga", "total_lye"
        ]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for row in stats:
            writer.writerow(row)

    return combo_scores, stats

# === Run Training ===

if __name__ == "__main__":
    combo_scores, stats = train(episodes=500000, alpha=0.1, epsilon=0.1, print_interval=100)

    print("\n=== Best combos by average efficiency ===")
    sorted_combos = sorted(combo_scores.items(), key=lambda kv: kv[1], reverse=True)
    for combo, score in sorted_combos:
        print(f"{combo}: score={score:.5f}")
    # === Evaluate Best Generalized Action Per Draw ===

    print("\n=== Best Generalized Action Per Draw ===")
    all_draws = set()
    for draw in product(potion_ids, repeat=3):
        all_draws.add(tuple(sorted(draw)))
    all_draws = sorted(all_draws)

    best_action_map = {}

    for draw in all_draws:
        subsets = all_subsets(draw)
        best_subset = max(subsets, key=lambda s: combo_scores.get(s, 0.0))
        best_action_map[draw] = best_subset

    for draw in list(best_action_map):  # Show top 20
        action = best_action_map[draw]
        score = combo_scores.get(action, 0.0)
        print(f"Draw: {draw} -> Best subset: {action}, Score: {score:.4f}")

    # === Save to CSV ===
    with open("best_actions_per_draw.csv", "w", newline="") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["Draw", "Best Subset", "Score"])
        for draw, subset in best_action_map.items():
            writer.writerow(["-".join(draw), "-".join(subset), combo_scores.get(subset, 0.0)])

    # === Save Final Combo Scores ===
    with open("final_combo_scores.csv", "w", newline="") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["Combo", "Score"])
        for combo, score in sorted(combo_scores.items(), key=lambda kv: kv[1], reverse=True):
            writer.writerow(["-".join(combo), score])