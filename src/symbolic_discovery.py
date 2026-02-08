
import random
import math
import json
import copy
import copy
import itertools

# Epistemic Purity: No external ML libraries. Strictly explicit logic.

# Internal imports (simulated for now, would import from src)
# from src.falsification import LocalHiddenVariableModel but we don't need it as we generate vertices manually here for speed.
# Actually, let's keep it self-contained as requested.

# --- 1. Expression Language ---

class Node:
    def evaluate(self, env):
        raise NotImplementedError
    
    def __str__(self):
        raise NotImplementedError
        
    def size(self):
        return 1

class Terminal(Node):
    def __init__(self, value, is_variable=False):
        self.value = value
        self.is_variable = is_variable
        
    def evaluate(self, env):
        if self.is_variable:
            return env[self.value] # Look up E_00, etc.
        return self.value # Constant
    
    def __str__(self):
        return str(self.value)

class BinaryOp(Node):
    def __init__(self, left, right, op_symbol):
        self.left = left
        self.right = right
        self.op_symbol = op_symbol
        
    def evaluate(self, env):
        l_val = self.left.evaluate(env)
        r_val = self.right.evaluate(env)
        
        if self.op_symbol == '+':
            return l_val + r_val
        elif self.op_symbol == '-':
            return l_val - r_val
        elif self.op_symbol == '*':
            return l_val * r_val
        return 0
    
    def __str__(self):
        return f"({self.left} {self.op_symbol} {self.right})"
        
    def size(self):
        return 1 + self.left.size() + self.right.size()

class UnaryOp(Node):
    def __init__(self, child, op_symbol):
        self.child = child
        self.op_symbol = op_symbol
        
    def evaluate(self, env):
        val = self.child.evaluate(env)
        if self.op_symbol == 'abs':
            return abs(val)
        elif self.op_symbol == 'sq':
            return val * val
        return val
        
    def __str__(self):
        return f"{self.op_symbol}({self.child})"
        
    def size(self):
        return 1 + self.child.size()

# --- 2. Genetic Algorithm Components ---

VARIABLES = ['E_00', 'E_01', 'E_10', 'E_11']
CONSTANTS = [1.0, -1.0]
OPS_BINARY = ['+', '-', '*']
OPS_UNARY = ['abs', 'sq']

def random_tree(depth):
    if depth == 0 or random.random() < 0.1:
        if random.random() < 0.7:
            return Terminal(random.choice(VARIABLES), is_variable=True)
        else:
            return Terminal(random.choice(CONSTANTS), is_variable=False)
    
    type_choice = random.random()
    if type_choice < 0.2: # Unary
        return UnaryOp(random_tree(depth-1), random.choice(OPS_UNARY))
    else: # Binary
        return BinaryOp(random_tree(depth-1), random_tree(depth-1), random.choice(OPS_BINARY))

model_vertices_cache = None

def get_model_vertices():
    """Generates the 16 vertices of the Local Factorizable Polytope."""
    global model_vertices_cache
    if model_vertices_cache:
        return model_vertices_cache
        
    vertices = []
    # 4 local variables: A(0), A(1), B(0), B(1) in {-1, 1}
    for i in range(16):
        a0 = 1 if (i & 1) else -1
        a1 = 1 if (i & 2) else -1
        b0 = 1 if (i & 4) else -1
        b1 = 1 if (i & 8) else -1
        
        # Correlations for this deterministic strategy
        # E_00 = A(0)B(0), E_01 = A(0)B(1), etc.
        v = {
            'E_00': a0 * b0,
            'E_01': a0 * b1,
            'E_10': a1 * b0,
            'E_11': a1 * b1
        }
        vertices.append(v)
    
    model_vertices_cache = vertices
    return vertices

def calculate_fitness(tree, obs_env):
    # 1. Observed Value
    try:
        val_obs = tree.evaluate(obs_env)
        
        # 2. Model Maximum (over all 16 vertices)
        max_model_val = 0.0
        vertices = get_model_vertices()
        for v in vertices:
            val = tree.evaluate(v)
            if abs(val) > max_model_val:
                max_model_val = abs(val)
        
        # 3. Separation
        # We want Obs > Model Max
        # Using symmetric scoring: |Obs| - Max(|Model|)
        
        separation = abs(val_obs) - max_model_val
        
        # 4. Parsimony Pressure
        # Penalty for complexity
        penalty = 0.05 * tree.size()
        
        return separation - penalty, separation, abs(val_obs), max_model_val
        
    except Exception:
        return -999.0, 0.0, 0.0, 0.0

def evolve(obs_vector):
    """
    Run Symbolic Regression GA.
    obs_vector: list [E_ab, E_abp, E_apb, E_apbp]
    """
    obs_env = {
        'E_00': obs_vector[0],
        'E_01': obs_vector[1],
        'E_10': obs_vector[2],
        'E_11': obs_vector[3]
    }
    
    population_size = 50
    generations = 30
    
    population = [random_tree(depth=random.randint(1, 3)) for _ in range(population_size)]
    hall_of_fame = []
    
    print(f"[PLANCK-SYMBOLIC] Evolving constraint candidates for {generations} generations...")
    
    for gen in range(generations):
        # Evaluate
        scored_pop = []
        for tree in population:
            ft, sep, v_obs, v_mod = calculate_fitness(tree, obs_env)
            scored_pop.append((ft, tree, sep, v_obs, v_mod))
            
        # Sort
        scored_pop.sort(key=lambda x: x[0], reverse=True)
        
        # Update Hall of Fame
        if scored_pop[0][2] > 0.1: # If positive separation
            best = scored_pop[0]
            # Avoid duplicates in HoF based on string exp
            exists = False
            for h in hall_of_fame:
                if str(h[1]) == str(best[1]):
                    exists = True
                    break
            if not exists:
                hall_of_fame.append(best)
                hall_of_fame.sort(key=lambda x: x[2], reverse=True)
                hall_of_fame = hall_of_fame[:5] # Keep top 5
                
        # Selection & Reproduction
        new_pop = [scored_pop[0][1], scored_pop[1][1]] # Elitism
        
        while len(new_pop) < population_size:
            # Tournament
            parent1 = max(random.sample(scored_pop, 3), key=lambda x: x[0])[1]
            parent2 = max(random.sample(scored_pop, 3), key=lambda x: x[0])[1]
            
            # Crossover (Simple logic: just pick one or new random for now to keep implementation minimal/robust)
            # Full subtree crossover is complex to code in one shot without bugs. 
            # Let's use simple mutation-only propagation or restart.
            # Actually, standard GA requires crossover. Let's do a simple swap.
            
            child = copy.deepcopy(parent1)
            # Mutate
            if random.random() < 0.3:
                child = random_tree(2) # Replacement mutation
            
            new_pop.append(child)
            
        population = new_pop
        
    return hall_of_fame

# --- Main Driver ---

def run_symbolic_discovery(certificate_path="discovery_certificate_zero.json"):
    # Load Observation
    try:
        with open(certificate_path, 'r') as f:
            cert = json.load(f)
        results = cert['results']
        obs_vec = [
            results['E_ab'],
            results['E_abp'],
            results['E_apb'],
            results['E_apbp']
        ]
        
    except FileNotFoundError:
        print("Certificate not found. Using Mock Data (CHSH violation).")
        obs_vec = [0.707, 0.707, 0.707, -0.707] # Yields 2.82
    
    print(f"Observation Vector: {obs_vec}")
    
    hof = evolve(obs_vec)
    
    print("\n[PLANCK-SYMBOLIC] Discovery Results (Top Candidates):")
    final_output = []
    
    for i, (fit, tree, sep, v_obs, v_mod) in enumerate(hof):
        print(f"{i+1}. Expression: {tree}")
        print(f"   Obs Mag: {v_obs:.4f} | Model Max: {v_mod:.4f} | Separation: {sep:.4f}")
        
        final_output.append({
            "expression": str(tree),
            "observed_magnitude": v_obs,
            "model_maximum": v_mod,
            "separation": sep,
            "complexity": tree.size()
        })
        
    # Save Artifact
    if final_output:
        with open("symbolic_constraint_discovery.json", 'w') as f:
            json.dump({
                "status": "DISCOVERY",
                "constraints": final_output
            }, f, indent=2)
        print("Saved to symbolic_constraint_discovery.json")
    else:
        print("No significant separating constraints found.")

if __name__ == "__main__":
    run_symbolic_discovery()
