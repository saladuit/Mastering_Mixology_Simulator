import random
from itertools import product
from collections import defaultdict
import csv
import argparse
import os
import shutil
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


# === Helper Functions ===

def is_done(current):
    return all(current[r] >= target[r] for r in target)

def bonus_for_count(n):
    return {1:1.0, 2:1.2, 3:1.4}[n]

def run_baseline_simulation(draw_to_choice_map, runs=100000):
    all_run_data = []
    aggregate_potion_counts = defaultdict(int)

    for _ in range(runs):
        # Progress bar
        if _ % (runs // 10) == 0:
            print(f"Progress: {(_ / runs) * 100:.2f}%")
        current = {"mox": 0, "aga": 0, "lye": 0}
        potion_counts = defaultdict(int)
        total_potions_used = 0

        while not is_done(current):
            draw = tuple(sorted(random.choices(potion_ids, weights=potion_weights, k=3)))
            chosen_potions = draw_to_choice_map.get(draw)

            if not chosen_potions:
                raise ValueError(f"No potion selection provided for draw: {draw}")

            count = len(chosen_potions)
            bonus = bonus_for_count(count)
            for pid in chosen_potions:
                potion = potion_map[pid]
                current["mox"] += potion.mox * bonus
                current["aga"] += potion.aga * bonus
                current["lye"] += potion.lye * bonus
                potion_counts[pid] += 1
                total_potions_used += 1

        # Record run data
        run_record = {
            "total_potions": total_potions_used,
            "mox": current["mox"],
            "aga": current["aga"],
            "lye": current["lye"],
            **{pid: potion_counts[pid] for pid in potion_ids}
        }
        all_run_data.append(run_record)

        for pid in potion_ids:
            aggregate_potion_counts[pid] += potion_counts[pid]

    # === Summary Statistics ===
    total_potions_list = [run["total_potions"] for run in all_run_data]
    mox_list = [run["mox"] for run in all_run_data]
    aga_list = [run["aga"] for run in all_run_data]
    lye_list = [run["lye"] for run in all_run_data]

    def min_run_by(key):
        return min(all_run_data, key=lambda x: x[key])

    def max_run_by(key):
        return max(all_run_data, key=lambda x: x[key])

    avg_potions_used = sum(total_potions_list) / runs
    avg_per_potion = {pid: aggregate_potion_counts[pid] / runs for pid in potion_ids}
    avg_targets = {
        "mox": sum(mox_list) / runs,
        "aga": sum(aga_list) / runs,
        "lye": sum(lye_list) / runs,
    }

    # === Prepare Output Directory ===
    strategy_basename = os.path.splitext(os.path.basename(args.strategy_file))[0]
    output_dir = os.path.join("strategies", strategy_basename)
    os.makedirs(output_dir, exist_ok=True)

    # Copy the strategy file into the output directory
    shutil.copy2(args.strategy_file, os.path.join(output_dir, os.path.basename(args.strategy_file)))

    # === Write Detailed Run Data ===
    run_data_path = os.path.join(output_dir, "run_data.csv")
    # === Write Detailed Run Data ===
    with open(run_data_path, "w", newline="") as csvfile:
        fieldnames = ["total_potions", "mox", "aga", "lye"] + potion_ids
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for run in all_run_data:
            writer.writerow(run)
        print(f"Run data saved to {run_data_path}")
    
    summary_path = os.path.join(output_dir, "summary.csv")
    # === Write Summary Statistics ===
    with open(summary_path, "w", newline="") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["Metric", "Value"])

        # Overall potions used
        writer.writerow(["Average Potions Used", f"{avg_potions_used:.2f}"])
        writer.writerow(["Minimum Potions Used", min(total_potions_list)])
        writer.writerow(["Maximum Potions Used", max(total_potions_list)])

        writer.writerow([])
        writer.writerow(["Potion Type", "Average", "Minimum", "Maximum"])
        for pid in potion_ids:
            per_run = [run[pid] for run in all_run_data]
            writer.writerow([pid, f"{avg_per_potion[pid]:.2f}", min(per_run), max(per_run)])

        writer.writerow([])
        writer.writerow(["Target Resource", "Average", "Minimum (MOX,AGA,LYE)", "Maximum (MOX,AGA,LYE)"])
        for key in ["mox", "aga", "lye"]:
            min_run = min_run_by(key)
            max_run = max_run_by(key)
            writer.writerow([
                key.upper(),
                f"{avg_targets[key]:.2f}",
                f"{min_run['mox']},{min_run['aga']},{min_run['lye']}",
                f"{max_run['mox']},{max_run['aga']},{max_run['lye']}"
            ])
        print(f"Summary statistics saved to {summary_path}")

    # === Console Report ===
    print(f"\n=== Simulation Summary for Strategy File: {args.strategy_file} ===")
    print(f"Runs: {runs}")
    print(f"Average Potions Used to Reach Target: {avg_potions_used:.2f}")
    print("Average Potion Usage per Type:")
    for pid in potion_ids:
        print(f"  {pid}: {avg_per_potion[pid]:.2f}")
    print("Average Reached:")
    for key in ["mox", "aga", "lye"]:
        print(f"  {key.upper()}: {avg_targets[key]:.2f}")

# === Example Usage ===
def load_draw_choices_from_csv(filepath):
    draw_to_choice_map = {}
    with open(filepath, newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            draw = tuple(sorted(row['draw'].split('-')))
            choice = row['choice'].split('-')
            draw_to_choice_map[draw] = choice
    return draw_to_choice_map

def generate_draw_template(filepath="draw_choices.csv"):
    all_draws = set(tuple(sorted(draw)) for draw in product(potion_ids, repeat=3))
    with open(filepath, "w", newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["draw", "choice"])
        for draw in sorted(all_draws):
            draw_key = "-".join(draw)
            writer.writerow([draw_key, "-".join(draw)])

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run the Mastering Mixology simulation.")
    parser.add_argument(
        "strategy_file",
        type=str,
        help="Path to your strategy CSV file (e.g., strategy.csv).\nAfter running it will create a folder in strategies and it will copy your current strategy to that folder and store the results."
    )
    parser.add_argument(
        "number_of_runs",
        type=int,
        nargs="?",
        default=100000,
        help="Number of simulation runs to perform (default: 100000)"
    )
    args = parser.parse_args()
    # generate_draw_template()
    # Print number of runs
    print(f"Using strategy file: {args.strategy_file}")
    print(f"Number of runs: {args.number_of_runs}")
    # draw_to_choice_map = load_draw_choices_from_csv(args.strategy_file_csv)
    # run_baseline_simulation(draw_to_choice_map, runs=args.number_of_runs)
