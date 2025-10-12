# HONSigtest

**HONSigtest** is a Python project for significant dependencies with variable orders mining (**SDVOM**) method, which could capture significant dependencies with variable orders in sequential datasets. 
It provides a complete pipeline—from trajectory simulation and rule extraction to statistical significance testing — applicable to domains such as transportation flows, communication networks, and web clickstreams.

---

## 📁 Project Structure

```
HONSigtest/
│
├── main.py                             # Main entry script for running significance test workflows
│
├── dependencies/                       # Core modules for dependency rule extraction and preprocessing
│   ├── different_orders_rules_count.py      # Categorizes and counts rules of different orders
│   ├── ExtractVariableOrderRules.py         # Core algorithm for extracting variable-order dependency rules
│   ├── find_real_second_dependencies.py     # Identifies and validates second-order dependencies
│   ├── input_output_file.py                 # Reads and preprocesses sequential trajectory data
│   ├── rules_related_functions.py           # Helper functions for rule extraction and manipulation
│   └── variables_to_pickleFile.py           # Utility functions for variable serialization (pickle)
│
├── significancetest/                   # Statistical significance testing modules
│   └── ExtractElementsDistributions.py     # Performs distribution analysis and confidence interval testing
│
├── simulation_test/                    # Simulation and synthetic trajectory generation
│   ├── build-simulation_grid100.py         # Builds higher-order simulation datasets
│   ├── CalculateRulesDistributionOfSimulationData-grid100.py  # Computes rule distributions from simulated data
│   └── webclickstream_tools_grid100.py    # Simulates multi-order clickstream trajectories based on transition matrices
│
└── .idea/                              # PyCharm IDE configuration files (not required for execution)
```


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
```
---

## 🚀 Usage

### 1️⃣ Run the Main Workflow

Execute the complete multi-order significance test process:

```bash
python main.py
```

By default, the script performs 2nd–4th order significance tests and generates result files:

```
2nd_order_SignificantRules_mo4_99%CI.csv
3rd_order_SignificantRules_mo4_99%CI.csv
4th_order_SignificantRules_mo4_99%CI.csv
```

---

### 2️⃣ Optional Environment Variables

You can customize the number of iterations, trajectory count, and minimum support threshold when running the main script:

```bash
SIGTEST_ITER=30 TRAJ_NUM=1000 MIN_SUPPORT=5 N_PROCESSES=8 python main.py
```

| Environment Variable | Description | Default |
|----------------------|-------------|----------|
| **`SIGTEST_ITER`** | Number of Monte Carlo iterations for significance testing | `30` |
| **`TRAJ_NUM`** | Number of simulated trajectories generated per order | `1000` |
| **`MIN_SUPPORT`** | Minimum frequency threshold for rule extraction | `5` |
| **`N_PROCESSES`** | Number of parallel processes for computation | `8` |

💡 *Tip:* Increasing `SIGTEST_ITER` improves statistical robustness, while higher `TRAJ_NUM` increases accuracy but also computation time.

---

### 3️⃣ Output Files

After running `main.py`, all results of significant dependencies with variable order are automatically saved in:

```
simulation_test/data/rules/20231114/
```

Each file contains the statistically significant dependencies identified at the corresponding order:

| File Name | Description |
|------------|-------------|
| `2nd_order_SignificantRules_mo4_99%CI.csv` | Significant second-order dependencies at the 99% confidence interval |
| `3rd_order_SignificantRules_mo4_99%CI.csv` | Significant third-order dependencies at the 99% confidence interval |
| `4th_order_SignificantRules_mo4_99%CI.csv` | Significant fourth-order dependencies at the 99% confidence interval |

#### 📂 Example Directory Structure

```
simulation_test/
└── data/
    └── rules/
        └── 20231114/
            ├── 2nd_order_SignificantRules_mo4_99%CI.csv
            ├── 3rd_order_SignificantRules_mo4_99%CI.csv
            └── 4th_order_SignificantRules_mo4_99%CI.csv
```

#### 📊 CSV File Structure

Each result file (`*_SignificantRules_mo4_99%CI.csv`) contains the following columns:

| Column Name | Meaning |
|--------------|----------|
| **`Rule`** | The identified dependency pattern (e.g., `A → B → C`) |
| **`Observed_Probability`** | Empirical transition probability of the dependency |

---

### 4️⃣ Example Workflow Summary

1. Load transition probability matrices (`1st-order`–`4th-order`).  
2. Generate synthetic trajectories using `webclickstream_tools_grid100.py`.  
3. Extract variable-order dependency rules via `ExtractVariableOrderRules.py`.  
4. Perform statistical significance testing with `ExtractElementsDistributions.py`.  
5. Export confidence-based CSV files.

---

## 🧠 Theoretical Background

HONSigtest is built upon the **Significant Dependencies with Variable Orders Mining (**SDVOM**)** method, designed to enhance the **representability** and **interpretability** of higher-order network (HON) models.

---

## 📰 Publication

This research has been **accepted for publication** in *Chaos, Solitons & Fractals* (Elsevier),  

> **Li, Jiaxu**, Yuan, Xiaoqian, Fu, Yude, Li, Jichao, Tan, Wenhui, and Lu, Xin.  
> *Representing Significant Dependencies with Variable Orders in Networks.*  
> *Chaos, Solitons & Fractals* (2025), in press.  
> DOI — forthcoming.

---

## 📚 BibTeX Citation (pre-publication)

---

## 📄 License

This project is released under the **MIT License**.

---

## 🧱 Suggested Repository Additions

To keep your GitHub repository clean, include a `.gitignore` file:

```
__pycache__/
*.pyc
*.pyo
*.pkl
*.pickle
*.npy
*.csv
.idea/
data/
variable/
```

---

### ✨ Author

Jiaxu Li, a Ph.D. candidate in Complex Network Science.
Focus: *Higher-Order Network Modeling, and Dependencies with Variable Orders Mining*









