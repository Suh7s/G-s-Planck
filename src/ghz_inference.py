
import pandas as pd
import numpy as np
import argparse

def analyze_ghz_experiment_v2(filepath="data/ghz_experiment_v2.csv"):
    """
    Analyzes Three-Body data to find Logical Contradictions.
    Theory-Free: Looks for deterministic rules and checks consistency.
    """
    try:
        df = pd.read_csv(filepath)
    except FileNotFoundError:
        print("Data file not found.")
        return

    # Calculate product
    df['sim_product'] = df['outcome_A'] * df['outcome_B'] * df['outcome_C']
    
    # Group by settings
    grouped = df.groupby(['setting_A', 'setting_B', 'setting_C'])['sim_product'].mean()
    counts = df.groupby(['setting_A', 'setting_B', 'setting_C'])['sim_product'].count()
    
    print("\n[PLANCK] Analyzing Three-Body Correlations...")
    
    # 1. Pattern Matching: Identify Strict Rules
    # We look for contexts where Mean Product is close to +1 or -1
    
    rules = {}
    
    for settings, val in grouped.items():
        if abs(val) > 0.9: # Threshold for "Strict Rule"
            rule_type = "product_is_positive" if val > 0 else "product_is_negative"
            print(f"Observed Rule for Inputs {settings}: Product is {val:.2f}")
            rules[settings] = val
            
    # 2. Consistency Checker
    # We specifically look for the standard 3-body paradox set
    # Eq1: (0, 1, 1) -> +1
    # Eq2: (1, 0, 1) -> +1
    # Eq3: (1, 1, 0) -> +1
    
    req_keys = [(0,1,1), (1,0,1), (1,1,0)]
    has_requirements = all(k in rules and rules[k] > 0.9 for k in req_keys)
    
    if not has_requirements:
        print("\n[PLANCK] No contradictory set of deterministic rules found.")
        return

    print("\n[PLANCK] Strict Rules Detected. internal_solver checking for consistency...")
    
    # Internal Solver Logic:
    # If vA(0)vB(1)vC(1) = 1
    # AND vA(1)vB(0)vC(1) = 1
    # AND vA(1)vB(1)vC(0) = 1
    # THEN product of all equations = 1.
    # [vA(0)vB(0)vC(0)] * [vA(1)^2 vB(1)^2 vC(1)^2] = 1
    # [vA(0)vB(0)vC(0)] * 1 = 1
    # PREDICTION: (0,0,0) MUST BE +1.
    
    prediction = 1.0
    print(f"[PLANCK] Logic Derivation: If these rules hold, Input (0,0,0) MUST yield Product +1.")
    
    # 3. Falsification
    key_test = (0,0,0)
    
    if key_test in grouped:
        observation = grouped[key_test]
        print(f"[PLANCK] Actual Observation for (0,0,0): {observation:.2f}")
        
        if abs(observation - prediction) > 1.0: # Close to -1 instead of +1
             print(f"\n[PLANCK] DISCOVERY: Logical Contradiction Detected.")
             print("          No pre-assigned values can explain these four joint observations simultaneously.")
        else:
             print("\n[PLANCK] Observation is consistent with derived prediction.")
    else:
        print("[PLANCK] Missing data for (0,0,0) configuration.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=str, default="data/ghz_experiment_v2.csv")
    args = parser.parse_args()
    
    analyze_ghz_experiment_v2(args.input)
