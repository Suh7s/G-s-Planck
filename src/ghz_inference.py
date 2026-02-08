
import pandas as pd
import numpy as np
import argparse
import ghz_falsification

def analyze_ghz_experiment(filepath="data/ghz_experiment.csv"):
    """
    Analyzes GHZ data to check for Triangle Violation.
    """
    try:
        df = pd.read_csv(filepath)
    except FileNotFoundError:
        print("Data file not found.")
        return

    # Calculate product of outcomes for each trial
    df['sim_product'] = df['outcome_A'] * df['outcome_B'] * df['outcome_C']
    
    # Group by settings
    grouped = df.groupby(['setting_A', 'setting_B', 'setting_C'])['sim_product'].mean()
    counts = df.groupby(['setting_A', 'setting_B', 'setting_C'])['sim_product'].count()
    
    print("\n[PLANCK] Analyzing GHZ State Correlations...")
    print(f"Total Trials: {len(df)}")
    
    # We are interested in 4 contexts:
    contexts = [
        ('X', 'X', 'X'),
        ('X', 'Y', 'Y'),
        ('Y', 'X', 'Y'),
        ('Y', 'Y', 'X')
    ]
    
    results = {}
    
    for ctx in contexts:
        if ctx in grouped.index:
            val = grouped[ctx]
            cnt = counts[ctx]
            print(f"Context {ctx}: Mean Product = {val:.4f} (N={cnt})")
            results[ctx] = val
        else:
            print(f"Context {ctx}: No Data")
            results[ctx] = 0.0

    # 1. Check if we have the prerequisites (XYY, etc approx +1)
    # We allow some noise, so threshold is not strictly 1.0
    pre_reqs = [results[('X','Y','Y')], results[('Y','X','Y')], results[('Y','Y','X')]]
    avg_pre_req = np.mean(pre_reqs)
    
    print(f"\n[PLANCK] Average of supporting correlations (XYY, YXY, YYX): {avg_pre_req:.4f}")
    
    if avg_pre_req < 0.5:
        print("[PLANCK] WARNING: Supporting correlations are too weak. Data may be just noise.")
        return

    # 2. Get Classical Prediction
    classical_pred = ghz_falsification.verify_ghz_constraints()
    
    # 3. Compare with XXX observation
    obs_xxx = results[('X','X','X')]
    
    print(f"\n[PLANCK] Target Observable XXX: {obs_xxx:.4f}")
    print(f"[PLANCK] Classical Deterministic Prediction: {classical_pred:.4f}")
    
    # Check for Contradiction
    # The contradiction is huge: -1 vs +1. Distance = 2.
    
    diff = abs(obs_xxx - classical_pred)
    
    if diff > 1.0:
        print(f"\n[PLANCK] DISCOVERY: 'Triangle' Contradiction Detected!")
        print(f"          Observation ({obs_xxx:.2f}) is the OPPOSITE of the Deterministic Prediction ({classical_pred:.2f}).")
        print(f"          This falsifies Non-contextual Determinism.")
    else:
        print(f"\n[PLANCK] RESULT: Consistent with Determinism.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=str, default="data/ghz_experiment.csv")
    args = parser.parse_args()
    
    analyze_ghz_experiment(args.input)
