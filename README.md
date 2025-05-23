# 🧪 Mastering Mixology Simulator
Mixing Mixology is a minigame in Old School RuneScape (OSRS). This repository aims to simulate and optimize strategies for green logging the minigame (i.e., unlocking all unique rewards) using as few potions as possible.
# 🎯 Goal
For every 3-potion draw, decide which 1–3 potions to create such that the total number of potions needed to hit the green log targets is minimized.
## Resource Targets:
```python
target = {"mox": 61050, "aga": 52550, "lye": 70500}
```
## Available Potions:
```python
# (combination, Mox, Aga, Lye, Weight)
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
```
## Bonus multiplier
Bonuses apply based on how many potions you submit at once:

1 potion → ×1.0
2 potions → ×1.2
3 potions → ×1.4

# 🛠️ How to Use
1. Clone and Run the Simulation
```bash
python3 mastering_mixology_simulation.py <path_to_strategy>.csv [num_runs]
```
* <path_to_strategy>.csv: CSV file mapping each draw (e.g. AAA-AAM-MAL) to a choice (e.g. AAM-MAL)

* `[num_runs]` (optional): Number of simulation runs to perform. Defaults to 100,000. You can use a smaller number for quick testing, but at least 100,000 runs are required for a strategy to be considered valid.
Example:
```bash
python mastering_mixology_simulation.py strategy_template.csv 10.000
```
The file `strategy_template.csv` contains the `completing_full_orders` strategy, which creates every single potion for each draw.

## The simulation will:
* Run the chosen strategy
* Print progress to the console
* Create a folder in csv_archive/<strategy_name>/
    * run_data.csv: detailed run-by-run breakdown
    * <strategy_name>.csv: the strategy you used as input
    * summary.csv: aggregated results

# ⚠️ Limitations
The following aspects are not simulated:

* ⏳ Potion crafting time
All potions are treated equally in time cost; workstation mechanics and their impact are not factored in.

* 🌿 Digweed usage
Currently excluded — players often only apply it to MAL potions, its impact on shouldn't really matter.

# ✏️ How to Create or Edit Strategies
Strategies are CSV files located in ./strategies. Each line looks like this:
```
AAA-AAM-MAL,AAM-MAL
```

This means:
For the draw AAA-AAM-MAL, create the potions AAM and MAL (in one turn for the bonus).

## 💡 You can:
* Use any potion subset of size 1–3 from the draw
* Preserve full orders (e.g. AAA-AAM-MAL,AAA-AAM-MAL) for testing base cases
## 🚫 You must NEVER: 
* Omit a choice (e.g. AAA-AAA-AAA,) I think it will just crash and you can restart the run.


# 📊 Output & Analysis
## After running a simulation:
* A new folder will be created in csv_archive/<strategy_name>/
* This contains:
    * run_data.csv: one line per simulation
    * summary.csv: key statistics (averages, min/max per potion type, and resin totals)
Example summary:
```
Metric,Value
Average Potions Used,5289.53
Minimum Potions Used,5013
Maximum Potions Used,5571

Potion Type,Average,Minimum,Maximum
AAA,629.92,515,761
MMM,629.67,513,754
LLL,629.62,530,732
MMA,503.72,393,610
MML,503.69,413,602
AAM,503.83,399,615
ALA,503.73,415,614
MLL,503.78,423,606
ALL,503.79,415,589
MAL,377.77,303,455

Target Resource,Average,"Minimum (MOX,AGA,LYE)","Maximum (MOX,AGA,LYE)"
MOX,70522.22,"64512.0,66584.0,70532.0","77686.0,74914.0,70532.0"
AGA,70532.06,"67662.0,64064.0,70504.0","73570.0,77154.0,70560.0"
LYE,70522.93,"68838.0,70504.0,70504.0","71008.0,71540.0,70574.0"

```
Example metrics:
* Average Potions Used: mean of all simulation runs
* Minimum Potions Used: best possible run
* Per-potion breakdown: see which potions are used the most
* Resource overshoot: check how efficiently you meet (not exceed) each resin target

Let me know if you want to see more data in a PR!

# ✅ Recommendations
## If you're iterating on a strategy:
* Name your files like 4.1_my_new_hypothesis.csv
* This keeps versions sorted and traceable for comparison
## Want to test faster?
```bash
python mastering_mixology_simulation.py my_strategy.csv 1000
```
# Current Strategies Overview

Below are descriptions and results for each strategy tested so far. Each strategy attempts to minimize the average number of potions brewed to achieve all green log targets.

---

## 1. Complete Full Orders (`1_complete_full_orders`)
**Approach:**  
Always create every potion in each draw, regardless of the combination.

**Result:**  
`Average Potions Used: 5289.53`

---

## 2. Skip Triples Unless MAL (`2_skip_triples_unless_MAL`)
**Approach:**  
Only create triple potions ("AAA", "MMM", "LLL") if the draw also contains "MAL".  
- If "MAL" is present, create all potions in the draw.
- If not, skip the triple potions.

**Example:**
```
AAA-MAL-MMM,AAA-MAL-MMM   # Full order, since MAL is present.
AAA-MLL-MLL,MLL-MLL       # Skip AAA, since MAL is absent.
```

**Result:**  
`Average Potions Used: 5060.33`

---

## 3. Skip Double Aga Unless MAL (`3_skip_double_aga_for_less_aga_points`)
**Approach:**  
Builds on Strategy 2. Additionally, skip any double-aga potions (e.g., "AAM", "ALA") unless "MAL" is present in the draw.  
- Aims to reduce excess AGA resource production.

**Example:**
```
AAM-MLL-MMM,MLL   # Skip AAM, as it's not part of a MAL order.
```

**Result:**  
`Average Potions Used: 4851.29`

---

## 4. Full Order If Lye ≥ 4 (`4_full_order_if_lye_4plus`)
**Approach:**  
Builds on Strategies 2 and 3.  
- If the total number of 'L's in the draw is at least 4, create the full order.
- Note: "LLL" counts as 2 L's (since it adds 20 Lye, not 30).

**Example:**
```
ALL-MML-MML,ALL-MML-MML   # Full order, since there are at least 4 L's.
```

**Result:**  
`Average Potions Used: 4678.46`

---

## 5. Lye-over-Mox-over-Aga Ratio (`5_lye_over_mox_over_aga_ratio`)
**Approach:**  
Builds on Strategies 2–4.  
- Prioritizes creating orders where the ratio of Lye to Mox to Aga is balanced or favors Lye.
- For example, if a draw like "AAA-LLL-MML" results in more Lye than Mox or Aga, create all three.

**Note:**  
This strategy may not be fully optimized, as its average is slightly higher than Strategy 4.

**Result:**  
`Average Potions Used: 4719.60`

---

*If you have ideas for new strategies or improvements, contributions are welcome!*

# 🙋 Help Wanted
I've tried five unique strategies so far, with the best averaging ~4,678 potions brewed.
If you have:

* Ideas on how to optimize better

* Knowledge about station bonuses or Digweed mechanics

* Thoughts on evaluating potion combinations more intelligently

Please contribute!

🧵 I’ll be posting this project to the OSRS subreddit.
Feedback, testing, and new strategy ideas are welcome. Feel free to fork or open PRs.