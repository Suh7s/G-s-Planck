
import pandas as pd
import numpy as np
import argparse

def analyze_temporal_experiment(filepath="data/temporal_experiment.csv"):
    """
    Analyzes temporal data to test the "Pre-existing Trajectory" hypothesis.
    Hypothesis implies: K = C12 + C23 - C13 <= 1.
    """
    try:
        df = pd.read_csv(filepath)
    except FileNotFoundError:
        print("Data file not found.")
        return

    # Calculate product for each trial
    df['sim_product'] = df['outcome_first'] * df['outcome_second']
    
    # Group by time pair (t_first, t_second)
    grouped = df.groupby(['t_first', 't_second'])['sim_product'].mean()
    counts = df.groupby(['t_first', 't_second'])['sim_product'].count()
    
    print("\n[PLANCK] Analyzing Temporal Correlations...")
    
    # We expect pairs (0,1), (1,2), (0,2)
    pairs = [(0,1), (1,2), (0,2)]
    correlations = {}
    
    for p in pairs:
        if p in grouped.index:
            val = grouped[p]
            cnt = counts[p]
            print(f"Time Pair {p}: Correlation C = {val:.4f} (N={cnt})")
            correlations[p] = val
        else:
            print(f"Time Pair {p}: No Data")
            correlations[p] = 0.0
            
    # Check Consistency Condition (Leggett-Garg Inequality)
    # K = C12 + C23 - C13
    
    C12 = correlations.get((0,1), 0)
    C23 = correlations.get((1,2), 0)
    C13 = correlations.get((0,2), 0)
    
    K = C12 + C23 - C13
    
    print(f"\n[PLANCK] Consistency Metric K = C(0,1) + C(1,2) - C(0,2)")
    print(f"[PLANCK] K = {C12:.4f} + {C23:.4f} - {C13:.4f} = {K:.4f}")
    
    # 2. Empirical Bound Discovery
    # Planck checks: "What is the maximum K possible for a system with definite history?"
    # It enumerates all 2^3 = 8 possible history vectors (v1, v2, v3) in {-1, 1}^3
    
    max_k_model = -999.0
    
    # 8 combinations of +/- 1
    # Simple explicit iteration
    for v1 in [-1, 1]:
        for v2 in [-1, 1]:
            for v3 in [-1, 1]:
                # K = v1*v2 + v2*v3 - v1*v3
                current_k = (v1 * v2) + (v2 * v3) - (v1 * v3)
                if current_k > max_k_model:
                    max_k_model = current_k
    
    print(f"\n[PLANCK] Enumerated all definite histories. Maximum possible K = {max_k_model:.4f}")
    
    # 3. Comparison
    stat_margin = 0.05
    
    if K > (max_k_model + stat_margin):
        print(f"\n[PLANCK] DISCOVERY: History Logic Violated.")
        print(f"          Observed K ({K:.4f}) exceeds the maximum possible for any definite history ({max_k_model:.4f}).")
        print(f"          Conclusion: The system does not possess pre-existing values independent of measurement.")
    else:
        print(f"\n[PLANCK] RESULT: Data is consistent with Definite History models (K <= {max_k_model:.4f}).")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=str, default="data/temporal_experiment.csv")
    args = parser.parse_args()
    
    analyze_temporal_experiment(args.input)
