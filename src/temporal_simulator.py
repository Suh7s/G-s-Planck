
import numpy as np
import pandas as pd
import random
import argparse

def simulate_temporal_experiment(num_trials=1000, noise_level=0.0):
    """
    Simulates a Temporal Correlation Experiment (Leggett-Garg).
    
    System: Single binary system measured at two times (ta, tb).
    Hypothesis to falsify: "The system has a definite value v(t) at all times."
    
    Hidden Physics (NOT visible to Planck):
    - System is a qubit rotating with frequency omega.
    - Correlation C(dt) = cos(omega * dt).
    - We choose times t1=0, t2=delta, t3=2*delta.
    - Ideal Violation: delta corresponding to 60 degrees (pi/3).
    - C(1,2) = 0.5, C(2,3) = 0.5, C(1,3) = -0.5.
    - K = 0.5 + 0.5 - (-0.5) = 1.5 > 1.
    """
    
    data = []
    
    # Time points (abstract indices for Planck)
    # 0 -> t1, 1 -> t2, 2 -> t3
    available_indices = [0, 1, 2]
    
    # Simulation Parameters
    # Angle step = pi/3 for max violation
    angle_step = np.pi / 3 
    
    for i in range(num_trials):
        # 1. Select a pair of times to measure
        # We must choose two distinct times ta < tb
        # Options: (0,1), (1,2), (0,2)
        
        pair_choice = random.choice([(0,1), (1,2), (0,2)])
        t_a_idx, t_b_idx = pair_choice
        
        # 2. Simulate Outcomes
        # In a real invasive experiment, measurement at ta collapses the state.
        # But we only output the pair (ya, yb).
        
        # Outcome at ta (y_a)
        # Random +/- 1 (since it's a qubit starting in mixed state or we just track relative)
        # Actually, let's assume P(+)=0.5.
        y_a = 1 if random.random() < 0.5 else -1
        
        # Outcome at tb (y_b) depends on y_a and the time difference
        dt_idx = t_b_idx - t_a_idx
        theta = dt_idx * angle_step
        
        # Correlation C = P(same) - P(diff) = cos(theta)
        # P(same) = (1 + C)/2 = (1 + cos(theta))/2
        
        if random.random() < noise_level:
            # Complete noise: correlation is 0
            p_same = 0.5
        else:
            p_same = (1 + np.cos(theta)) / 2
        
        is_same = random.random() < p_same
        y_b = y_a if is_same else -y_a
        
        data.append({
            "trial_id": i,
            "t_first": t_a_idx,
            "t_second": t_b_idx,
            "outcome_first": y_a,
            "outcome_second": y_b
        })
        
    return pd.DataFrame(data)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--trials", type=int, default=3000)
    parser.add_argument("--noise", type=float, default=0.0)
    parser.add_argument("--output", type=str, default="data/temporal_experiment.csv")
    args = parser.parse_args()
    
    df = simulate_temporal_experiment(args.trials, args.noise)
    df.to_csv(args.output, index=False)
    print(f"Saved {len(df)} temporal trials to {args.output}")
