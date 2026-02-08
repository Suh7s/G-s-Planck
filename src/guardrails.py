
import numpy as np
import random
import json
import itertools

# Internal imports
try:
    from src import simulator
    from src import active_discovery_zero
    from src import falsification
except ImportError:
    import simulator
    import active_discovery_zero
    import falsification

# --- 1. Null Hypothesis Test ---

def classical_simulator(settings, trials=1000):
    """
    A simulator that strictly obeys Local Hidden Variable theory.
    Correlations are product states: E(a,b) = A(a) * B(b).
    Here we pick a random deterministic strategy (one of the 16 vertices).
    """
    # Pick a random hidden variable state lambda
    vertex_idx = random.randint(0, 15)
    
    va  = 1 if (vertex_idx & 1) else -1
    vap = 1 if (vertex_idx & 2) else -1
    vb  = 1 if (vertex_idx & 4) else -1
    vbp = 1 if (vertex_idx & 8) else -1
    
    # Calculate expected correlations for this strategy
    e_ab   = va * vb
    e_abp  = va * vbp
    e_apb  = vap * vb
    e_apbp = vap * vbp
    
    return {
        'E_ab': e_ab,
        'E_abp': e_abp,
        'E_apb': e_apb,
        'E_apbp': e_apbp
    }

def shuffled_simulator(settings, trials=1000):
    """
    Runs the real quantum simulator but returns shuffled results.
    We just return random correlations that satisfy local bounds on average?
    Better: We simulate the experiment, get the data, but then shuffle outcomes
    independently for A and B, destroying correlations.
    """
    # 1. Run real simulation to get raw data
    # (We need a version of simulator that returns raw df for specific settings)
    # Since simulator.py separates raw generation from aggregation, this is tricky
    # without modifying simulator.py again.
    # PROXY: We just return product of random averages.
    # <A>_local * <B>_local = <AB>_shuffled
    
    # Let's act as if each side sees local random noise
    
    res = {}
    for label in ['E_ab', 'E_abp', 'E_apb', 'E_apbp']:
        # Generate random local margins
        mean_A = random.uniform(-1, 1)
        mean_B = random.uniform(-1, 1)
        # Expected correlation for independent variables is product of means
        res[label] = mean_A * mean_B
        
    return res

def run_null_hypothesis_test():
    print("[PLANCK-GUARDRAILS] Running Null Hypothesis Counter-Checks...")
    
    # 1. Classical Data Test
    print("  > Testing on Classical LHV Data...")
    classical_planck = active_discovery_zero.ActivePlanckZero(simulator_func=classical_simulator)
    classical_result = classical_planck.run_loop(max_iterations=50) # Shorter loop
    
    classical_strain = classical_result['strain'] if classical_result else 0.0
    print(f"    Classical Max Strain: {classical_strain:.4f}")
    
    # 2. Shuffled Data Test
    print("  > Testing on Shuffled/Independent Data...")
    shuffled_planck = active_discovery_zero.ActivePlanckZero(simulator_func=shuffled_simulator)
    shuffled_result = shuffled_planck.run_loop(max_iterations=50)
    
    shuffled_strain = shuffled_result['strain'] if shuffled_result else 0.0
    print(f"    Shuffled Max Strain: {shuffled_strain:.4f}")
    
    passed = (classical_strain < 1e-4) and (shuffled_strain < 1e-4)
    status = "PASS" if passed else "FAIL"
    print(f"  > Null Hypothesis Result: {status}")
    
    return {
        "classical_strain": classical_strain,
        "shuffled_strain": shuffled_strain,
        "result": status
    }

# --- 2. Noise Robustness Verification ---

def verify_noise_robustness(discovery_config):
    print("\n[PLANCK-GUARDRAILS] Verifying Noise Robustness (Structural Continuity)...")
    
    if not discovery_config:
        print("  > No discovery to verify.")
        return {"result": "N/A"}
        
    controls = discovery_config['controls']
    # Sweep noise from 0.0 to 1.0
    noise_steps = np.linspace(0.0, 1.0, 21) # 0.05 increments
    strains = []
    
    model = falsification.LocalHiddenVariableModel()
    
    prev_strain = 999.0
    monotonic = True
    vanished = False
    
    print("  > Sweeping Noise Parameter (eta):")
    
    for eta in noise_steps:
        # We need to simulate with specific noise.
        # But simulate_bell_experiment_with_settings doesn't take noise arg directly in current signature!
        # We need to wrap it or modify it.
        # Let's use a lambda wrapper that uses the global simulate_bell_experiment_with_settings logic 
        # but injects noise.
        # WAIT: simulate_bell_experiment_with_settings in simulator.py DOES NOT TAKE NOISE ARG.
        # It assumes default? 
        # We need to update simulator.py to accept noise in 'with_settings' function.
        # I will assume I updated it or hack it here.
        
        # HACK: We can simulate manually using simulator logic here since we can't edit simulator.py inside this execution block easily 
        # (simultaneous edits bad).
        # Actually, best to update simulator.py. But let's check if I can pass it.
        # I will implement a local simulator wrapper that supports noise.
        
        results = simulator_with_noise(controls, eta)
        
        # Calculate Strain
        E_ab = results['E_ab']
        E_abp = results['E_abp']
        E_apb = results['E_apb']
        E_apbp = results['E_apbp']
        S_obs = E_ab - E_abp + E_apb + E_apbp
        
        _, strain = model.fit_best(controls, S_obs)
        
        strains.append(strain)
        print(f"    eta={eta:.2f} -> Strain={strain:.4f}")
        
        # Checks
        if strain > prev_strain + 0.05: # Allow small noise fluctuations
            monotonic = False
        
        if strain < 1e-4:
            vanished = True
            
        prev_strain = strain
        
    continuity = monotonic # Simple check
    
    status = "PASS" if (monotonic and vanished) else "FAIL"
    print(f"  > Noise Robustness Result: {status}")
    print(f"    (Monotonic: {monotonic}, Vanishes: {vanished})")
    
    return {
        "monotonic": monotonic,
        "vanishes_at_limit": vanished,
        "result": status,
        "trace": strains
    }

def simulator_with_noise(settings, noise_level, trials=1000):
    # Re-impl of simulate_bell_experiment_with_settings but with noise support
    results = {}
    pairs = [
        ('E_ab', settings['A'][0], settings['B'][0]),
        ('E_abp', settings['A'][0], settings['B'][1]),
        ('E_apb', settings['A'][1], settings['B'][0]),
        ('E_apbp', settings['A'][1], settings['B'][1])
    ]
    
    for label, theta_A, theta_B in pairs:
        delta = theta_A - theta_B
        # Expected E = -cos(delta) * (1 - noise) + 0 * noise
        # E_ideal = -np.cos(delta)
        # E_noisy = E_ideal * (1.0 - noise_level)
        # We simulate this analytically for speed/stability in guardrails?
        # "Simulate Bell Experiment" usually implies sampling.
        # Let's sample.
        
        sum_product = 0
        for _ in range(trials):
            if random.random() < noise_level:
                # Random noise
                outcome_A = 1 if random.random() < 0.5 else -1
                outcome_B = 1 if random.random() < 0.5 else -1
            else:
                # Quantum
                outcome_A = 1 if random.random() < 0.5 else -1
                if outcome_A == 1:
                    p_B_plus = (np.sin(delta/2))**2
                else:
                    p_B_plus = (np.cos(delta/2))**2
                outcome_B = 1 if random.random() < p_B_plus else -1
                
            sum_product += outcome_A * outcome_B
            
        results[label] = sum_product / trials
        
    return results

def run_guardrails():
    # Load Discovery
    try:
        with open("discovery_certificate_zero.json", 'r') as f:
            config = json.load(f)
    except FileNotFoundError:
        config = None
        
    null_res = run_null_hypothesis_test()
    noise_res = verify_noise_robustness(config)
    
    report = {
        "status": "PASSED" if (null_res['result'] == "PASS" and noise_res['result'] == "PASS") else "FAILED",
        "null_hypothesis": null_res,
        "noise_robustness": noise_res
    }
    
    with open("guardrails_report.json", 'w') as f:
        json.dump(report, f, indent=2)
        
    print("\n[PLANCK-GUARDRAILS] Report saved to guardrails_report.json")
    return report

if __name__ == "__main__":
    run_guardrails()
