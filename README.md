# Planck: Automated Scientific Discovery for Quantum Physics

**Planck** is an AI-driven scientific co-designer that infers physical laws purely from experimental data, without prior knowledge of quantum mechanics.

This repository contains the implementation of **Experiment Zero** (Bell-CHSH) and **Experiment One** (GHZ State), where Planck successfully "discovers" that local factorizable models (classical intuition) fail to explain observed correlations.

## Project Structure

- `src/`: Core logic for simulation, falsification, and inference.
  - `simulator.py`: Simulates Bell-CHSH experiment.
  - `inference.py`: Infers correlation laws and checks CHSH violation.
  - `falsification.py`: Proves bounds for Local Hidden Variable models.
  - `ghz_simulator.py`: Simulates 3-particle GHZ state.
  - `ghz_inference.py`: Detects "All-vs-Nothing" violation of determinism.
  - `ghz_falsification.py`: Proves bounds for Local Deterministic models.
- `design/`: Design documents and experimental plans.
- `data/`: Generated experimental data (gitignored).

## Experiments

### 1. Experiment Zero: Bell-CHSH Violation
Planck observes correlations between two entangled particles and discovers that they violate the CHSH inequality ($|S| \le 2$), a bound it independently derives for local factorizable models.

**Run the Experiment:**
```bash
# 1. Generate Data (Simulate Experiment)
python3 src/simulator.py --trials 5000 --noise 0.0

# 2. Run Planck's Analysis
python3 src/inference.py
```

### 2. Experiment One: GHZ "Triangle" Violation
Planck observes three particles in a GHZ state. It derives that any local deterministic model must predict $XXX = +1$ given $XYY = YXY = YYX = +1$. It then observes $XXX = -1$, a perfect contradiction.

**Run the Experiment:**
```bash
# 1. Generate Data
python3 src/ghz_simulator.py --trials 5000 --noise 0.0 --output data/ghz_clean.csv

# 2. Run Planck's Analysis
python3 src/ghz_inference.py --input data/ghz_clean.csv
```

## Methodology
Planck operates under strict constraints:
1.  **Operational Purity**: It only sees settings and outcomes.
2.  **No Physics Priors**: It does not know about Hilbert spaces, wavefunctions, or operators.
3.  **Falsification First**: It defines classical model classes and proves they fail, rather than just curve-fitting.

## Requirements
- Python 3.8+
- `numpy`
- `pandas`
- `gplearn` (for symbolic regression)
- `scikit-learn`
- `matplotlib`
