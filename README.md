# HONSigtest

**HONSigtest** is a Python project for significant dependencies with variable orders mining (**SDVOM**) method, which could capture significant dependencies with variable orders in sequential datasets. 
It provides a complete pipeline—from trajectory simulation and rule extraction to statistical significance testing — applicable to domains such as transportation flows, communication networks, and web clickstreams.

---

## 📁 Project Structure

HONSigtest/
│
├── main.py # Main entry script for running significance test workflows
│
├── dependencies/ # Core modules for variable-order rules extraction and preprocessing
│ ├── different_orders_rules_count.py # Categorizes and counts variable-order rules
│ ├── ExtractVariableOrderRules.py # Core algorithm for extracting variable-order rules
│ ├── find_real_second_dependencies.py # Identifies and validates second-order dependencies
│ ├── input_output_file.py # Reads and preprocesses sequential dataset
│ ├── rules_related_functions.py # Helper functions for rule extraction and manipulation
│ └── variables_to_pickleFile.py # Utility functions for variable serialization (pickle)
│
├── significancetest/ # Statistical significance testing modules
│ └── ExtractElementsDistributions.py # Performs distribution analysis and confidence interval testing
│
├── simulation_test/ # Simulation and synthetic trajectory generation
│ ├── build-simulation_grid100.py # Builds higher-order simulation datasets
│ ├── CalculateRulesDistributionOfSimulationData-grid100.py # Computes real rule distributions from simulated data
│ └── webclickstream_tools_grid100.py # Simulates multi-order clickstream trajectories based on transition matrices
│
└── .idea/ # PyCharm IDE configuration files (not required for execution)


---

## 🧩 Key Components

### 1. **Trajectory Simulation (`simulation_test/`)**
Simulates clickstream or trajectory data using multi-order Markov chains.  
- Supports orders from 1st to 4th.  
- Generates synthetic trajectories for validation of dependencies with variable orders.  
- Based on transition probability matrices stored as `.npy` or `.pickle` files.

### 2. **Variable-Order Rule Extraction (`dependencies/`)**
Implements recursive algorithms for mining  with variable-order rules.  
- Counts co-occurrence frequencies and builds transition probability distributions.  
- Automatically extends lower-order nodes to higher orders.  
- Supports minimum support threshold (`MinSupport`) for rule pruning.

### 3. **Significance Testing (`significancetest/`)**
Performs statistical significant tests for variable-order rules.
- Computes means, variances, Z-scores, and confidence intervals (99%).  
- Identifies statistically significant dependencies beyond random fluctuations.  
- Export of results as `.csv`.

---

## ⚙️ Environment Requirements

```bash
Python >= 3.7
numpy
pandas
scipy
statistics
matplotlib

## 🚀 Usage

### 1️⃣ Run the main workflow

Execute the complete multi-order significance test process:

```bash
python main.py

By default, the script performs 2nd–4th order significance tests and generates result files:

2nd_order_SignificantRules_mo4_99%CI.csv
3rd_order_SignificantRules_mo4_99%CI.csv
4th_order_SignificantRules_mo4_99%CI.csv

### 2️⃣ Optional Environment Variables

You can adjust the number of iterations, trajectory count, and minimum support threshold when running the main script:

```bash
SIGTEST_ITER=30 TRAJ_NUM=1000 MIN_SUPPORT=5 N_PROCESSES=8 python main.py














