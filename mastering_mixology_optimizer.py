from itertools import combinations_with_replacement, combinations
from collections import Counter, defaultdict
from typing import NamedTuple
import pulp

class Potion(NamedTuple):
    id: str
    mox: int
    aga: int
    lye: int
    weight: int  # 5 (single resin), 4 (dual), 3 (triple)

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

target_mox, target_aga, target_lye = 61050, 52550, 70500

def bonus_for_count(n):
    return {1:1.0, 2:1.2, 3:1.4}[n]

# Generate all multisets of 3 potions (unordered with repetition)
multisets = list(combinations_with_replacement(potion_map.keys(), 3))

def subsets_all_same(potions):
    # potions = (A,A,A)
    # valid subsets: 1xA, 2xA, 3xA
    return [(potions[0],) * n for n in range(1, 4)]

def subsets_two_same(potions):
    # potions like (A,A,B) or (A,B,B)
    # Generate all non-empty multisets from potions with duplicates
    c = Counter(potions)
    pot_ids = list(c.elements())  # e.g. ['A', 'A', 'B']
    # Generate unique multisets of sizes 1,2,3 considering duplicates
    result = set()
    for size in range(1,4):
        for comb in combinations(pot_ids, size):
            # To avoid duplicates, sort tuple
            result.add(tuple(sorted(comb)))
    return sorted(result)

def subsets_all_different(potions):
    # potions like (A,B,C), all distinct
    # all non-empty subsets of size 1,2,3
    result = []
    for size in range(1,4):
        for comb in combinations(potions, size):
            result.append(comb)
    return result

results = []
subset_data = []
for mset in multisets:
    c = Counter(mset)
    distinct = len(c)
    # Classify multiset type
    if distinct == 1:
        # all same
        valid_subsets = [ (mset[0],)*n for n in range(1,4) ]
    elif distinct == 2:
        # two same
        valid_subsets = subsets_two_same(mset)
    else:
        # all distinct
        valid_subsets = subsets_all_different(mset)

    for subset in valid_subsets:
        count = len(subset)
        bonus = bonus_for_count(count)
        total_mox = sum(potion_map[p].mox for p in subset) * bonus
        total_aga = sum(potion_map[p].aga for p in subset) * bonus
        total_lye = sum(potion_map[p].lye for p in subset) * bonus
        total_weight = sum(potion_map[p].weight for p in subset)
        results.append({
            "combo": mset,
            "chosen": subset,
            "distinct": distinct,
            "bonus": bonus,
            "adjusted_mox": round(total_mox, 2),
            "adjusted_aga": round(total_aga, 2),
            "adjusted_lye": round(total_lye, 2),
            "total_weight": total_weight,
        })
        subset_data.append((subset, total_mox, total_aga, total_lye))


# Optimization model
prob = pulp.LpProblem("Minimize_Total_Potions", pulp.LpMinimize)
x_vars = [pulp.LpVariable(f"x_{i}", lowBound=0, cat='Integer') for i in range(len(subset_data))]

# 🧠 Objective: minimize total number of potions used
prob += pulp.lpSum(x_vars[i] * len(subset_data[i][0]) for i in range(len(subset_data)))

# Constraints to meet resin targets
prob += pulp.lpSum(x_vars[i] * subset_data[i][1] for i in range(len(subset_data))) >= target_mox
prob += pulp.lpSum(x_vars[i] * subset_data[i][2] for i in range(len(subset_data))) >= target_aga
prob += pulp.lpSum(x_vars[i] * subset_data[i][3] for i in range(len(subset_data))) >= target_lye

prob.solve()

# Collect solution
solution = [(subset_data[i][0], int(x_vars[i].varValue)) for i in range(len(subset_data)) if x_vars[i].varValue and x_vars[i].varValue > 0]

# Helper to compute stats
def get_stats(subset):
    count = len(subset)
    bonus = bonus_for_count(count)
    mox = sum(potion_map[p].mox for p in subset) * bonus
    aga = sum(potion_map[p].aga for p in subset) * bonus
    lye = sum(potion_map[p].lye for p in subset) * bonus
    total = mox + aga + lye
    weight = sum(potion_map[p].weight for p in subset)
    efficiency = total / weight if weight else 0
    return int(mox), int(aga), int(lye), int(total), weight, efficiency

# Print readable table
print(f"\n{'Subset':<20} {'Qty':<5} {'Mox':<5} {'Aga':<5} {'Lye':<5} {'Total':<6} {'Weight':<6} {'Eff.':<6}")
print("=" * 70)
for subset, qty in sorted(solution, key=lambda x: -x[1]):
    mox, aga, lye, total, weight, eff = get_stats(subset)
    potions = ",".join(subset)
    print(f"{potions:<20} {qty:<5} {mox:<5} {aga:<5} {lye:<5} {total:<6} {weight:<6} {eff:.2f}")

# print(f"Total combinations (multisets × subsets): {len(results)}")
# # Should print 1320

# # Example output: print first 5 results
# for r in results:
#     print(r)