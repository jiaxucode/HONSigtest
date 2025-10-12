# -*- coding: utf-8 -*-
"""

Run the full pipeline automatically for orders 2 -> 4:
- simulate trajectories with a Nth-order Markov generator,
- extract rules up to the given order,
- aggregate distributions over many iterations,
- compute statistics, z-scores, CI tests,
- dump significant dependencies with variable orders to CSV and pickle files.
"""

from typing import List, Tuple

# ==== External modules from the project ====
import os
os.chdir(os.path.join(os.path.dirname(__file__), "simulation_test"))
# Simulation (Markov generators & real transition tables)
from simulation_test.webclickstream_tools_grid100 import Webclickstream
# Rule extraction and counting
from dependencies.different_orders_rules_count import *
from multiprocessing import Pool
from dependencies.ExtractVariableOrderRules import *
# Stats & significance
from significancetest.ExtractElementsDistributions import *
# Dumpers & pickle utils
from dependencies.rules_related_functions import *
from dependencies.variables_to_pickleFile import *

# ===================== User-tunable parameters =====================
# Number of Monte-Carlo iterations per order
iterations = int(os.environ.get("SIGTEST_ITER", "100"))
# Number of simulated clickstream trajectories per iteration
trajectories_num = int(os.environ.get("TRAJ_NUM", "500"))
# Minimum support when extracting rules
MinSupport = int(os.environ.get("MIN_SUPPORT", "5"))
# Processes for simulation (reduce if memory constrained)
N_PROCESSES = int(os.environ.get("N_PROCESSES", "8"))

# Base folders (created on demand)
BASE_VAR_RULES = "./variable/rules/20231114" # p=0.1
BASE_DATA_RULES = "./data/rules/20231114" # p=0.1

# BASE_VAR_RULES = "./variable/rules/20231217" # p=0.2
# BASE_DATA_RULES = "./data/rules/20231217" # p=0.2

# BASE_VAR_RULES = "./variable/rules/20231229" # p=0.3
# BASE_DATA_RULES = "./data/rules/20231229" # p=0.3

# Output CSV filenames (requested naming)
OUT_CSV_FMT = {
    2: "2nd_order_SignificantRules_mo4_99%CI_1.csv",
    3: "3rd_order_SignificantRules_mo4_99%CI_1.csv",
    4: "4th_order_SignificantRules_mo4_99%CI_1.csv",
}

# Real rules pickles per order (default names used in your repo)
REAL_RULE_PICKLE = {
    2: os.path.join(BASE_VAR_RULES, "2nd-order", "real", "Rules_2nd_order_mo4.pickle"),
    3: os.path.join(BASE_VAR_RULES, "3rd-order", "real", "Rules_3rd_order_mo4.pickle"),
    4: os.path.join(BASE_VAR_RULES, "4th-order", "real", "Rules_4th_order_mo4.pickle"),
}

def _ensure_dir(path: str) -> str:
    os.makedirs(path, exist_ok=True)
    return path

def _ordinal(n: int) -> str:
    return {1:"1st",2:"2nd",3:"3rd"}.get(n, f"{n}th")

def _nettype_for_sim(order: int) -> str:
    """
    When validating order=k dependencies, we simulate with (k-1)-order generator
    to form the null distribution:
        k=2 -> simulate with '1st-order'
        k=3 -> '2nd-order'
        k=4 -> '3rd-order'
    """
    prev = order - 1
    return f"{_ordinal(prev)}-order"

def _save_rules_folder(order: int) -> str:
    return _ensure_dir(os.path.join(BASE_VAR_RULES, f"{_ordinal(order)}-order", "synthetic"))

def _out_csv_path(order: int) -> str:
    return _ensure_dir(BASE_DATA_RULES) + os.sep + OUT_CSV_FMT[order]

def _real_rules_pickle(order: int) -> str:
    return REAL_RULE_PICKLE[order]

# ===================== Trajectory simulation =====================
def Simulate_Webclickstream_Trajectories(nettype: str) -> Tuple[object, List[List[int]]]:
    """
    Generate a DataFrame-like stub (kept for compatibility) and a list of trajectories.
    The Webclickstream class internally fixes steps=100 and uses the correct
    order-specific generator based on `nettype` ('1st-order' / '2nd-order' / ...).
    """
    trajectories: List[List[int]] = []
    # We don't rely on the DataFrame structure elsewhere in the pipeline;
    # return None as placeholder to keep the original function signature.
    df_stub = None
    for i in range(1, trajectories_num + 1):
        stream = Webclickstream(clickstream_id=i, NetType=nettype)
        # Exhaust the generator to populate history
        _ = list(stream.gen)
        trajectories.append(stream.history)
    return df_stub, trajectories

# ===================== Per-iteration job =====================
def _generate_trajectories(iter_idx: int, order: int, nettype: str, save_rules_folder: str):
    """
    - Simulate trajectories using the (order-1)-th generator (nettype)
    - Extract rules up to 'order'
    - Keep only current order dictionary via RuleStats()
    - Save a pickle for later aggregation
    """
    _, trajectories = Simulate_Webclickstream_Trajectories(nettype)
    dist = ExtractRules(trajectories, order, MinSupport)   # returns Distribution (probabilities)
    rules_by_order = RuleStats(dist)                       # split by order
    pick_idx = {1:0, 2:1, 3:2, 4:3, 5:4}.get(order, order-1)
    rules_current = rules_by_order[pick_idx]

    SaveVariablestoPickleFile(
        rules_current,
        os.path.join(save_rules_folder, f'iter_{iter_idx}_{order}th_rules.pickle')
    )

# ===================== Pipeline for one order =====================
def run_pipeline_for_order(order: int):
    assert order in (2,3,4), "Only orders 2–4 are automated in this script."
    nettype = _nettype_for_sim(order)
    save_rules_folder = _save_rules_folder(order)
    real_rules_path = _real_rules_pickle(order)
    out_csv = _out_csv_path(order)

    print(f"[order={order}] start | simulate={nettype} | iters={iterations} | traj/iter={trajectories_num}")
    _ensure_dir(os.path.join(save_rules_folder, "mo4"))

    # 1) Simulation + extraction (per-iteration pickle)
    try:
        with Pool(processes=N_PROCESSES) as pool:
            pool.starmap(
                _generate_trajectories,
                [(i, order, nettype, save_rules_folder) for i in range(iterations)]
            )
    except Exception as e:
        print(f"[order={order}] multiprocessing failed ({e}), falling back to single process.")
        for i in range(iterations):
            _generate_trajectories(i, order, nettype, save_rules_folder)

    # 2) Merge per-iteration distributions into value lists
    Distributions_differentElements = read_all_defaultdictPickleFile(save_rules_folder)

    # 3) Compute stats (mean, std, CI)
    statisticsindex = CalculateStatisticsOfDifferentDistribution(Distributions_differentElements)

    # 4) Load real rules for current order
    Rules_x_order = LoadVariablestoPickleFile(real_rules_path)

    # 5) Z-score & p-value
    statisticsindex, zscore_outliers, pval_outliers = CalculateZscoreofRealElements(statisticsindex, Rules_x_order)
    SaveVariablestoPickleFile(zscore_outliers, os.path.join(save_rules_folder, 'mo4', 'zscore_outliers.pickle'))
    SaveVariablestoPickleFile(pval_outliers, os.path.join(save_rules_folder, 'mo4', 'pval_outliers.pickle'))
    SaveVariablestoPickleFile(statisticsindex, os.path.join(save_rules_folder, 'mo4', 'statisticsindex_of_dependencies.pickle'))

    # 6) CI test
    CI_outliers = ConfidenceIntervalTest(statisticsindex, Rules_x_order)
    SaveVariablestoPickleFile(CI_outliers, os.path.join(save_rules_folder, 'mo4', 'CI_outliers.pickle'))

    # 7) Dump significant rules (CSV + pickles)
    DumpSignificantRules(statisticsindex, CI_outliers, Rules_x_order, save_rules_folder, out_csv)

    print(f"[order={order}] done -> {out_csv}")

# ===================== Main =====================
if __name__ == "__main__":
    for k in (2, 3, 4):
        run_pipeline_for_order(k)
    print("All orders (2–4) finished.")
