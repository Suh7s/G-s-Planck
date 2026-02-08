
import numpy as np
import random
import argparse
import json
import time

# Internal imports
try:
    from src import simulator
    from src import falsification
except ImportError:
    import simulator
    import falsification

# Use the full module path
simulate_bell_experiment_with_settings = simulator.simulate_bell_experiment_with_settings
LocalHiddenVariableModel = falsification.LocalHiddenVariableModel

class ActivePlanckZero:
    def __init__(self, simulator_func=None):
        self.model_class = LocalHiddenVariableModel()
        self.best_strain = -1.0
        self.best_config = None
        self.history = []
        # Dependency Injection for Guardrails/Testing
        self.simulator_func = simulator_func if simulator_func else simulate_bell_experiment_with_settings

    def propose_initial_controls(self):
        # Random angles in [0, 2pi]
        return {
            'A': [random.uniform(0, 2*np.pi), random.uniform(0, 2*np.pi)],
            'B': [random.uniform(0, 2*np.pi), random.uniform(0, 2*np.pi)]
        }
        
    def measure_strain(self, controls, trials=1000):
        # 1. Run Experiment
        # We need simulator to return observed S-like statistic or raw data
        # Let's assume simulator returns the 4 correlations: E(a,b), E(a, b'), E(a', b), E(a', b')
        # for the specific settings provided.
        
        # We need to adapt simulator.py to take specific settings and return data for those settings only.
        # Current simulator generates random settings.
        # We will modify simulator.py to accept 'fixed_settings' mode.
        
        results = self.simulator_func(controls, trials)
        
        # 2. Identify Observed Correlations
        # results = {'E_ab': ..., 'E_abp': ..., 'E_apb': ..., 'E_apbp': ...}
        
        E_ab = results['E_ab']
        E_abp = results['E_abp']
        E_apb = results['E_apb']
        E_apbp = results['E_apbp']
        
        # 3. Compute S-statistic (The Proxy for Model Failure)
        # S = E(a,b) - E(a, b') + E(a', b) + E(a', b')
        # There are actually 8 symmetries of S, we just maximize the absolute value of the best one
        # For active discovery, we can try to maximize S.
        
        S_obs = E_ab - E_abp + E_apb + E_apbp
        
        # 4. Compute Strain (Dynamic Model Query)
        # We ask the model: "What is the max S you can support?"
        # The model searches its parameter space and returns the limit.
        # We do NOT assume the limit is 2.0.
        
        limit, strain = self.model_class.fit_best(controls, S_obs)
        
        return strain, results, S_obs

    def perturb_controls(self, current_controls, perturbation_scale=0.1):
        # Add random noise
        new_controls = {}
        for key in current_controls:
            new_controls[key] = [
                angle + random.gauss(0, perturbation_scale) 
                for angle in current_controls[key]
            ]
        return new_controls

    def run_loop(self, max_iterations=50):
        print(f"[PLANCK-ACTIVE] Starting Active Discovery Loop (Max Iterations: {max_iterations})...")
        
        current_controls = self.propose_initial_controls()
        
        for i in range(max_iterations):
            # 1. Measure Strain
            strain, results, S_obs = self.measure_strain(current_controls)
            
            # 2. Record
            # We recover the limit from strain to show we found it
            limit_found = abs(S_obs) - strain if strain > 0 else 2.0 # Approximation for logging
            print(f"Iter {i+1}: S={S_obs:.4f} (Model Max: {limit_found:.4f}) -> Strain={strain:.4f}")
            
            if strain > self.best_strain:
                self.best_strain = strain
                self.best_config = {
                    'controls': current_controls,
                    'results': results,
                    'S_obs': S_obs,
                    'strain': strain,
                    'model_limit': limit_found
                }
                print(f"  [NEW BEST] Found configuration with Strain {strain:.4f}")
                
            # 3. Terminate?
            if strain > 0.8: # Close to theoretical max 2.82 - 2.0 = 0.82
                print(f"[PLANCK-ACTIVE] Saturation Reached. Stopping.")
                break
                
            # 4. Update (Hill Climbing)
            # Try a candidate
            candidate_controls = self.perturb_controls(current_controls)
            cand_strain, _, _ = self.measure_strain(candidate_controls)
            
            if cand_strain >= strain:
                current_controls = candidate_controls
            # Else stay
            
        return self.best_config

    def save_artifact(self, filename="discovery_certificate_zero.json"):
        if self.best_config:
            with open(filename, 'w') as f:
                json.dump(self.best_config, f, indent=2)
            print(f"[PLANCK-ACTIVE] Discovery Certificate saved to {filename}")
        else:
            print("[PLANCK-ACTIVE] No discovery made.")

if __name__ == "__main__":
    planck = ActivePlanckZero()
    best_result = planck.run_loop(max_iterations=100)
    
    if best_result:
        planck.save_artifact()
        print(f"\n[PLANCK] Discovery Complete.")
        print(f"         Max Strain: {best_result['strain']:.4f}")
        print(f"         Controls: {best_result['controls']}")
