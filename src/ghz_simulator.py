
import numpy as np
import pandas as pd
import random
import argparse

def simulate_ghz_experiment(num_trials=1000, noise_level=0.0, reliability=1.0):
    """
    Simulates a GHZ Experiment (Greenberger-Horne-Zeilinger).
    State: |Psi> = 1/sqrt(2) (|000> + |111>)
    
    Observables:
    - X measurements on all 3 (XXX) -> Expectation -1
    - X on one, Y on two (XYY, YXY, YYX) -> Expectation +1
    
    Outcomes are +/- 1.
    """
    
    data = []
    
    # Settings: 'X' or 'Y'
    possible_settings = ['X', 'Y']
    
    for i in range(num_trials):
        # 0. Detector Inefficiency
        if random.random() > reliability:
            continue

        # 1. Choose Settings Randomly
        # For GHZ, we need specific combinations to see the contradiction:
        # XXX, XYY, YXY, YYX.
        # But a real experiment would choose randomly.
        s_A = random.choice(possible_settings)
        s_B = random.choice(possible_settings)
        s_C = random.choice(possible_settings)
        
        # 2. GHZ Logic (Hidden from Planck, but used for simulation)
        # We can simulate outcomes directly based on quantum predictions for GHZ state.
        # |GHZ> = (|000> + |111>)/sqrt(2)
        
        # Rules for perfect GHZ correlations:
        # Product(XXX) = -1
        # Product(XYY) = +1
        # Product(YXY) = +1
        # Product(YYX) = +1
        
        # Other combinations (like XXY) are random/zero correlation in standard basis?
        # Actually for GHZ:
        # X eigenstates |+>, |->. Y eigenstates |+i>, |-i>.
        # We only really care about the 4 Mermin contexts for the paradox.
        # But we must generate valid outcomes for ALL settings to be a "real" experiment.
        
        # Let's implementation a generalized simulation:
        # 1. Generate state |000> + |111>
        # 2. Apply Rotations based on settings (X or Y basis)
        # 3. Measure in Z basis
        
        # Simplified simulation for the 4 critical contexts + noise:
        
        # Determine Parity constraint
        # Parity = a * b * c
        
        is_noisy = random.random() < noise_level
        
        if is_noisy:
            # Random outcomes
            a = 1 if random.random() < 0.5 else -1
            b = 1 if random.random() < 0.5 else -1
            c = 1 if random.random() < 0.5 else -1
        else:
            # Quantum Outcomes
            # We construct outcomes to satisfy the product rules.
            # We can pick 2 outcomes randomly, and fix the 3rd to satisfy the constraint.
            
            # Count number of Ys
            num_Y = 0
            if s_A == 'Y': num_Y += 1
            if s_B == 'Y': num_Y += 1
            if s_C == 'Y': num_Y += 1
            
            # Constraint:
            # If 0 Ys (XXX): Product = -1
            # If 2 Ys (XYY, YXY, YYX): Product = +1
            # If 1 or 3 Ys: These are not eigenstates of the Mermin operators for this GHZ state?
            # Actually, for standard GHZ, odd number of Ys -> correlations are zero?
            # Let's check: Y Y Y on |000>+|111>
            # Y = sigma_y = [[0, -i], [i, 0]]
            # YYY |000> = i*i*i |111> = -i |111>
            # YYY |111> = (-i)*(-i)*(-i) |000> = i |000>
            # <Psi|YYY|Psi> = 0.
            # So for 1 or 3 Ys, the product is random (+1 or -1 with 50%).
            
            if num_Y == 0: # XXX
                target_product = -1
            elif num_Y == 2: # XYY, etc.
                target_product = 1
            else:
                target_product = 0 # Random
            
            # Generate A and B randomly
            a = 1 if random.random() < 0.5 else -1
            b = 1 if random.random() < 0.5 else -1
            
            if target_product != 0:
                # c is determined by a*b*c = target
                # c = target / (a*b) = target * a * b
                c = target_product * a * b
            else:
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
    parser.add_argument("--trials", type=int, default=1000)
    parser.add_argument("--noise", type=float, default=0.0)
    parser.add_argument("--reliability", type=float, default=1.0)
    parser.add_argument("--output", type=str, default="data/ghz_experiment.csv")
    args = parser.parse_args()
    
    df = simulate_ghz_experiment(args.trials, args.noise, args.reliability)
    df.to_csv(args.output, index=False)
    print(f"Saved {len(df)} GHZ trials to {args.output}")
