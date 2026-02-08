
import numpy as np
import pandas as pd
import random
import argparse

def simulate_ghz_experiment_v2(num_trials=1000, noise_level=0.0):
    """
    Simulates the Three-Body Experiment (GHZ) with STRICTLY OPERATIONAL LABELS.
    
    Inputs: "Settings" 0 or 1 for each of 3 detectors.
    Outputs: "Outcomes" +1 or -1.
    
    Hidden Physics (NOT visible to Planck):
    - Setting 0 corresponds to X basis.
    - Setting 1 corresponds to Y basis.
    - State is |GHZ> = |000> + |111>.
    
    Strict Rules (Hidden):
    - (0, 1, 1) -> XYY -> Product +1
    - (1, 0, 1) -> YXY -> Product +1
    - (1, 1, 0) -> YYX -> Product +1
    - (0, 0, 0) -> XXX -> Product -1
    """
    
    data = []
    
    possible_settings = [0, 1]
    
    for i in range(num_trials):
        # 1. Randomly choose settings (0 or 1)
        s_A = random.choice(possible_settings)
        s_B = random.choice(possible_settings)
        s_C = random.choice(possible_settings)
        
        # 2. Simulate Outcomes based on Hidden Physics
        # Count number of 1s (Ys)
        num_ones = s_A + s_B + s_C
        
        # Determine Target Product
        # If 2 ones (XYY type) -> Product +1
        # If 0 ones (XXX type) -> Product -1
        # Else (1 or 3 ones) -> Random product (unentangled context for this state)
        
        if num_ones == 2:
            target_product = 1
        elif num_ones == 0:
            target_product = -1
        else:
            target_product = 0 # Random
            
        # Apply noise
        if random.random() < noise_level:
            target_product = 0 # Randomize
            
        # Generate individual outcomes
        a = 1 if random.random() < 0.5 else -1
        b = 1 if random.random() < 0.5 else -1
        
        if target_product != 0:
            # c is determined constraint
            # a*b*c = target => c = target * a * b
            c = target_product * a * b
        else:
            # Random c
            c = 1 if random.random() < 0.5 else -1
            
        data.append({
            "trial_id": i,
            "setting_A": s_A,
            "setting_B": s_B,
            "setting_C": s_C,
            "outcome_A": a,
            "outcome_B": b,
            "outcome_C": c
        })
        
    return pd.DataFrame(data)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--trials", type=int, default=5000)
    parser.add_argument("--noise", type=float, default=0.0)
    parser.add_argument("--output", type=str, default="data/ghz_experiment_v2.csv")
    args = parser.parse_args()
    
    df = simulate_ghz_experiment_v2(args.trials, args.noise)
    df.to_csv(args.output, index=False)
    print(f"Saved {len(df)} GHZ trials to {args.output}")
