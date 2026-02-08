import numpy as np
import pandas as pd
import random
import argparse

def simulate_bell_experiment(num_trials=1000, noise_level=0.0, reliability=1.0):
    """
    Simulates a Bell Test (CHSH setup) with entangled spin-1/2 particles (Singlet State).
    Returns a DataFrame with trial data.
    
    Args:
        num_trials: Number of attempted trials to generate
        noise_level: Probability (0.0 to 1.0) of a completely random outcome (white noise)
        reliability: Probability (0.0 to 1.0) of successful detection (detector efficiency)
    
    Quantum Mechanics (Hidden from Planck):
    - State: |psi-> = 1/sqrt(2) (|up,down> - |down,up>)
    - Correlation: E(theta_A, theta_B) = -cos(theta_A - theta_B)
    """
    
    # print(f"Generating trials... (Target: {num_trials}, Noise: {noise_level}, Eff: {reliability})")
    
    data = []
    
    possible_angles_A = [0.0, np.pi/2, np.pi/4, np.pi] 
    possible_angles_B = [np.pi/4, 3*np.pi/4, 0.0, np.pi/2]

    # We might need to attempt more than num_trials if reliability < 1.0 to get fixed size, 
    # OR we just simulate num_trials events and some are lost. 
    # "Total trials are reduced" in the prompt suggests the latter.
    
    for i in range(num_trials):
        # 0. Detector Inefficiency Check
        # If either detector fails, we don't get a coincidence pair in this simplified model.
        # We assume independent efficiency for A and B?
        # Let's say reliability is system reliability (P_coincidence).
        if random.random() > reliability:
            continue # Data lost

        # 1. Randomly choose settings for Alice and Bob
        if random.random() < 0.8:
            theta_A = random.choice(possible_angles_A)
            theta_B = random.choice(possible_angles_B)
        else:
            theta_A = random.uniform(0, 2*np.pi)
            theta_B = random.uniform(0, 2*np.pi)
            
        # 2. Calculate Quantum Probabilities
        delta = theta_A - theta_B
        
        # 3. Determine Outcomes
        # Pure QM probabilities for Singlet:
        # P(outcome_A = +1) = 0.5
        # P(outcome_B = -outcome_A) = cos^2(delta/2)
        
        # Decide if this trial is 'noisy' (unentangled / random) or 'quantum'
        if random.random() < noise_level:
            # Completely random outcomes (uncorrelated)
            outcome_A = 1 if random.random() < 0.5 else -1
            outcome_B = 1 if random.random() < 0.5 else -1
        else:
            # Quantum Behavior
            outcome_A = 1 if random.random() < 0.5 else -1
            
            # B depends on A and delta
            if outcome_A == 1:
                p_B_plus = (np.sin(delta/2))**2
            else: # outcome_A == -1
                p_B_plus = (np.cos(delta/2))**2
                
            outcome_B = 1 if random.random() < p_B_plus else -1
        
        data.append({
            "trial_id": i,
            "setting_A": round(theta_A, 5),
            "setting_B": round(theta_B, 5),
            "outcome_A": outcome_A,
            "outcome_B": outcome_B
        })
        
    return pd.DataFrame(data)

def simulate_bell_experiment_with_settings(settings, trials=1000):
    """
    Runs a Bell experiment with explicit settings provided by the Active Discovery Engine.
    
    Args:
        settings: Dict {'A': [theta_A1, theta_A2], 'B': [theta_B1, theta_B2]}
        trials: Number of trials per setting pair.
        
    Returns:
        Dict of results: {'E_ab': float, 'E_abp': float, 'E_apb': float, 'E_apbp': float}
    """
    results = {}
    
    # We need to measure 4 combinations: (A1, B1), (A1, B2), (A2, B1), (A2, B2)
    # Corresponding to E(a,b), E(a,b'), E(a',b), E(a',b')
    
    pairs = [
        ('E_ab', settings['A'][0], settings['B'][0]),
        ('E_abp', settings['A'][0], settings['B'][1]),
        ('E_apb', settings['A'][1], settings['B'][0]),
        ('E_apbp', settings['A'][1], settings['B'][1])
    ]
    
    for label, theta_A, theta_B in pairs:
        # Simulate 'trials' events for this specific pair
        # Hidden Quantum Physics: E = -cos(theta_A - theta_B)
        # We simulate the finite statistics
        
        delta = theta_A - theta_B
        
        # P(outcome_A = +1) = 0.5
        # P(outcome_B = -outcome_A) = cos^2(delta/2)
        # P(outcome_B = outcome_A) = sin^2(delta/2)
        
        # Expected Correlation E = P(same) - P(diff)
        # E = sin^2 - cos^2 = -cos(delta)
        # We can just simulate the E directly with binomial noise for speed?
        # Or simulate individual events. Let's simulate events to be honest.
        
        sum_product = 0
        for _ in range(trials):
            # A is random
            outcome_A = 1 if random.random() < 0.5 else -1
            
            # B depends on A and delta
            # Prob B = +1 given A
            if outcome_A == 1:
                p_B_plus = (np.sin(delta/2))**2
            else:
                p_B_plus = (np.cos(delta/2))**2
                
            outcome_B = 1 if random.random() < p_B_plus else -1
            
            sum_product += outcome_A * outcome_B
            
        results[label] = sum_product / trials
        
    return results

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--trials", type=int, default=10000)
    parser.add_argument("--noise", type=float, default=0.0, help="Noise level (0.0 to 1.0)")
    parser.add_argument("--reliability", type=float, default=1.0, help="Detector reliability/efficiency (0.0 to 1.0)")
    parser.add_argument("--output", type=str, default="data/bell_experiment.csv")
    args = parser.parse_args()
    
    df = simulate_bell_experiment(args.trials, args.noise, args.reliability)
    df.to_csv(args.output, index=False)
    print(f"Saved {len(df)} trials to {args.output} (Noise: {args.noise}, Reliability: {args.reliability})")
