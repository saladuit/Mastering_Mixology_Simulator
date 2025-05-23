# Mastering_Mixology_Simulator
Mixing Mixology is a mini game of OSRS. I've made this repository to find the approximation to the most efficient route to green log the mini game.
# How this works

## The goal
We want to find an action set per draw which results in the least amount of potions used.

There are 10 different kind of potions.
```python
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

All of the 220 unique orders this can generate are stored in ./draw_strategies/full_order.csv

That is an csv file which can be used as input to the simulation. This stategy just makes all the potions and the results are store in csv_archive/full_order/summary.csv. There is also a 'run_data.csv' file if you want to look more closely at the data of each run.

## The simulation
### Included in the simulation
- When 1, 2 or 3 potions are turned in, the bonus multipliers are applied, 1.0, 1.2 and 1.4 respectively.
- The green log goal is `target = {"mox": 61050, "aga": 52550, "lye": 70500}`
- It takes the weight of each potion into account
- It reads from a csv file which action to take for a given order
- It will produce a summary in the following format
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

### Not included in the simulation
- I didn't take into account how long it takes to create a potion at a certain station
- I didn't include digweed. (I don't think it really matters, as one will only use it on MAL potions anyway)
- I didn't take into account the various mixing stations.

### How to use the simulation
After cloning the repository
```python
python mastering_mixology_simulation.py <action_per_draw>.csv [number_of_runs]
# `action_per_draw.csv`: Path to your strategy CSV file.
# `number_of_runs` (optional): Number of simulation runs to perform (default is 100,000).
```
I've added a progress bar to show you how far it is in the simulation.
For testing purposes you can test a few runs. But for a new strategy to be submitted, 100.000 runs are needed

### How to edit the actions
All the strategies are stored in ./draw_strategies. You could start with a clean slate. ./draw_strategies/full_order.csv just creates each single potion for each draw. It is the worst strategy listed on the wiki and results in an average of 5289 potions.
It is order like this:
`AAA-AAM-MAL,AAA-AAM-MAL`
Left side of the comma is the draw/order. Right side of the comma is the action that should be taken. Shoul it create one, two or three of the given potions and in what combination.
In the following example I'd only want to create a single potions so I put this into the file:
`AAA-AAA-LLL,LLL`
Currently my best result is: Average Potions Used,4678.46

### Output
The simulation will automatically create a new folder in csv_archive with the name you've given to the file. In that folder you will find two files. `run_data.csv` and `summary.csv`. I think that most people just want to look at the latter one. There you can find usefull stats about the run. Let me know if you want to see more statistics.

### Recommendation
If you try to improve an existing strategy. Create a file name called: 1.1_complete_full_orders. In that way you can still compare the data from previous versions.

# Current Strategies Descriptions
## 1_complete_full_orders
Just create every single potion for every given order.
Result: `Average Potions Used,5289.53`
## 2_skip_triples_unless_MAL
When either "AAA", "MMM", "LLL" are in the order. only create them when they are part of an MAL order.
Example
```
AAA-MAL-MMM,AAA-MAL-MMM # We create the full order, because MAL is in the recipe.
AAA-MLL-MLL,MLL-MLL # We skip it because there is no MAL in the order
```
Result: `Average Potions Used,5060.33`
## 3_skip_double_aga_less_points
I used strategy 2 and added that I'd skip every double aga potion when it wasn't part of a MAL potion.
(When writing this I see that I wasn't very consistent sticking to this strategy).
Example
```
AAM-MLL-MMM,MLL # we skip AAM, because we over produce aga in the previous test result. I is also not part of a MAL order.
```
Result: `Average Potions Used,4851.29`
## 4_triple_order_if_lye_4plus
I used strategy 2 and 3 and the also applied the strategy which creates a triple order if the letter L is at least four times in the order. I do have to state that "LLL" counts as only 2, as it only adds 20 lye to the order.
(While creating this strategy I still counted "LLL" as 3, instead of 2 -> it only adds twenty lye and not thirty.)
```
# We create the full order as there are at least 4 L's
ALL-MML-MML,ALL-MML-MML
```

Result: `Average Potions Used,4678.46`
## 5_lye_over_mox_over_aga_ratio
This last strategy I'm working on builds on top of strategies 2 to 4. In this strategy I also try to add orders which have a equal or favourable ratio between mox, aga and lye. For example, if the draw is "AAA-LLL-MML" it would add 24 aga, 38 L's and 24 M's, I will create all three, due to L's being more prevalentand there are not more A's, than M's.

Result: `Average Potions Used,4719.60`
I'm quite sure I've not created this strategy perfectly, as the average potions made are higher than strategy 4.