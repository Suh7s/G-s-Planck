
import json
import itertools
try:
    from src.falsification import LocalHiddenVariableModel
except ImportError:
    from falsification import LocalHiddenVariableModel

def run_constraint_discovery(certificate_path="discovery_certificate_zero.json"):
    print("[PLANCK-DISCOVERY] Starting Primitive Constraint Discovery...")
    
    # 1. Load Certificate
    with open(certificate_path, 'r') as f:
        cert = json.load(f)
        
    results = cert['results']
    # These are correlations E_ab, E_abp, E_apb, E_apbp
    # We map them to an ordered list for coefficients
    E_obs = [
        results['E_ab'],
        results['E_abp'],
        results['E_apb'],
        results['E_apbp']
    ]
    labels = ["E(a,b)", "E(a,b')", "E(a',b)", "E(a',b')"]
    
    print(f"Loaded Observation: {E_obs}")
    
    # 2. Initialize Model
    model = LocalHiddenVariableModel()
    
    # 3. Generate Candidates (Coeffs in {-1, 0, 1})
    coeffs = [-1, 0, 1]
    candidates = list(itertools.product(coeffs, repeat=4))
    
    discoveries = []
    
    print(f"Evaluating {len(candidates)} candidate expressions...")
    
    for c in candidates:
        # Check if trivial (all zero)
        if all(x == 0 for x in c):
            continue
            
        # 4. Score Candidate
        # A. Observed Magnitude
        # Use simple algebraic sum first, then take ABS
        # F = c0*E0 + ...
        val_obs_alg = sum(c[i] * E_obs[i] for i in range(4))
        val_obs_mag = abs(val_obs_alg)
        
        # B. Model Maximum (Optimization)
        # Use the symmetric maximizer we added to falsification.py
        val_model_max = model.maximize_absolute_linear_combination(c)
        
        # C. Separation (Gap)
        # Score(F) = |Obs| - Max(|Model|)
        gap = val_obs_mag - val_model_max
        
        if gap > 0.1: # Noise threshold
            # Format the expression string
            terms = []
            for i in range(4):
                if c[i] == 1:
                    terms.append(f"+{labels[i]}")
                elif c[i] == -1:
                    terms.append(f"-{labels[i]}")
            expr_str = " ".join(terms)
            if expr_str.startswith("+"):
                expr_str = expr_str[1:]
                
            discoveries.append({
                "expression": expr_str,
                "coefficients": c,
                "observed_magnitude": val_obs_mag,
                "model_maximum": val_model_max,
                "violation_margin": gap
            })
            
    # 5. Selection & Ranking
    # Sort by violation margin (descending)
    discoveries.sort(key=lambda x: x['violation_margin'], reverse=True)
    
    if discoveries:
        best = discoveries[0]
        print(f"\n[PLANCK-DISCOVERY] SUCCESS! Found a violating constraint.")
        print(f"Expression: {best['expression']}")
        print(f"Observed Mag: {best['observed_magnitude']:.4f}")
        print(f"Model Max:    {best['model_maximum']:.4f}")
        print(f"Violation:    {best['violation_margin']:.4f}")
        
        # Save Artifact
        output_path = "primitive_constraint_discovery.json"
        with open(output_path, 'w') as f:
            json.dump({
                "status": "DISCOVERY",
                "top_constraints": discoveries[:5] # Top 5
            }, f, indent=2)
        print(f"Saved top constraints to {output_path}")
        return True
    else:
        print("\n[PLANCK-DISCOVERY] No violating constraints found (linear combinations).")
        return False

if __name__ == "__main__":
    run_constraint_discovery()
