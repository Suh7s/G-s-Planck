
import numpy as np
from scipy.optimize import minimize

class LocalHiddenVariableModel:
    """
    Represents a class of models where correlations differ from:
    E(a, b) = sum_lambda P(lambda) * A(a, lambda) * B(b, lambda)
    
    Outcomes A and B are strictly local (depend only on local setting and lambda).
    """
    
    def __init__(self, num_lambdas=16):
        self.num_lambdas = num_lambdas
        # We model discrete hidden variables which can approximate continuous ones.
    
    def maximize_chsh(self):
        """
        Attempts to find the configuration of local variables that maximizes S.
        S = E(a, b) - E(a, b') + E(a', b) + E(a', b')
        
        Returns the maximum S found.
        """
        # We want to maximize S.
        # S <= 2 is the bound we expect Planck to "discover" empiricially.
        
        # To make this "optimization" easy, notice that for a fixed lambda:
        # S_lambda = A(a)B(b) - A(a)B(b') + A(a')B(b) + A(a')B(b')
        # S = sum P(lambda) S_lambda
        # So max S is achieved by finding a single optimal lambda configuration (P=1 for that lambda).
        
        # Max S_lambda = A(a)[B(b) - B(b')] + A(a')[B(b) + B(b')]
        # A, B are in {-1, 1}.
        # B(b), B(b') can be (1,1), (1,-1), (-1,1), (-1,-1).
        # Cases:
        # 1. B, B' = 1, 1 -> [0] + A(a')[2]. Max if A(a')=1 -> 2.
        # 2. B, B' = 1, -1 -> A(a)[2] + [0]. Max if A(a)=1 -> 2.
        # ...
        # Planck can "search" this via brute force or sampling for small N.
        
        # Let's simulate a "search" process.
        max_s = 0.0
        
        # Brute force check of all 16 combinations of values for A(a), A(a'), B(b), B(b')
        # This is the simplest proof Planck can perform.
        # There are 4 variables: va = A(a), vap = A(a'), vb = B(b), vbp = B(b')
        # Each can be +/- 1. Total 2^4 = 16 states.
        
        for i in range(16):
            va  = 1 if (i & 1) else -1
            vap = 1 if (i & 2) else -1
            vb  = 1 if (i & 4) else -1
            vbp = 1 if (i & 8) else -1
            
            # Calculate S contribution for this "deterministic strategy"
            # E(x,y) is just the product of outcomes for this single event
            s_val = (va * vb) - (va * vbp) + (vap * vb) + (vap * vbp)
            
            if s_val > max_s:
                max_s = s_val
                
        return max_s

    def maximize_linear_combination(self, coefficients):
        """
        Finds the maximum value of a linear combination of correlations:
        F = c0*E(a,b) + c1*E(a,b') + c2*E(a',b) + c3*E(a',b')
        that can be produced by any Local Deterministic Strategy.
        
        Args:
            coefficients: List/Tuple of 4 floats [c0, c1, c2, c3]
            
        Returns:
            max_val: The maximum achievable value.
        """
        max_val = -999.0
        
        # Iterate over all 16 deterministic strategies (vertices of the local polytope)
        # Each vertex defines values for A(a), A(a'), B(b), B(b') in {-1, 1}
        for i in range(16):
            va  = 1 if (i & 1) else -1
            vap = 1 if (i & 2) else -1
            vb  = 1 if (i & 4) else -1
            vbp = 1 if (i & 8) else -1
            
            # The correlation E(x,y) for a deterministic strategy is just the product of outcomes
            e_ab   = va * vb
            e_abp  = va * vbp
            e_apb  = vap * vb
            e_apbp = vap * vbp
            
            # Compute the linear combination value for this strategy
            val = (coefficients[0] * e_ab) + \
                  (coefficients[1] * e_abp) + \
                  (coefficients[2] * e_apb) + \
                  (coefficients[3] * e_apbp)
                  
            if val > max_val:
                max_val = val
                
        return max_val

    def maximize_absolute_linear_combination(self, coefficients):
        """
        Finds the maximum absolute value of a linear combination of correlations:
        F = c0*E(a,b) + c1*E(a,b') + c2*E(a',b) + c3*E(a',b')
        that can be produced by any Local Deterministic Strategy.
        
        Symmetric evaluation: returns max(|F|).
        
        Args:
            coefficients: List/Tuple of 4 floats [c0, c1, c2, c3]
            
        Returns:
            max_abs_val: The maximum achievable magnitude.
        """
        max_abs_val = -999.0
        
        for i in range(16):
            va  = 1 if (i & 1) else -1
            vap = 1 if (i & 2) else -1
            vb  = 1 if (i & 4) else -1
            vbp = 1 if (i & 8) else -1
            
            e_ab   = va * vb
            e_abp  = va * vbp
            e_apb  = vap * vb
            e_apbp = vap * vbp
            
            val = (coefficients[0] * e_ab) + \
                  (coefficients[1] * e_abp) + \
                  (coefficients[2] * e_apb) + \
                  (coefficients[3] * e_apbp)
                  
            abs_val = abs(val)
            if abs_val > max_abs_val:
                max_abs_val = abs_val
                
        return max_abs_val
        
    def fit(self, X, y):
        """
        Attempts to fit the LHV model to observed correlations.
        X: [[theta_A, theta_B], ...]
        y: [E_obs, ...]
        
        Since general LHV is hard to fit, we check if the S-statistic matches.
        Or we can try to fit specific factorizable models.
        
        For Step 1, proving |S| <= 2 is sufficient falsification for Bell.
        Falsification logic:
        1. Calculate observed S.
        2. Compare with max_chsh() of the model class.
        3. If S_obs > Max_Model_S, then Model is Falsified.
        """
        return self.maximize_chsh()
        
    def fit_best(self, settings, observation):
        """
        Returns the best possible prediction of the model class for a given observation.
        The model searches its own parameter space to find the maximum possible statistic.
        
        Args:
            settings: The experimental settings (unused for CHSH as bound is universal, but kept for API).
            observation: The specific observed S-statistic.
            
        Returns:
            model_prediction: The maximum S-statistic the model can produce (found by search).
            fitting_error: Gap between obs and limit (strain).
        """
        # Ask the model: "What is the max S you can produce?"
        # The model performs a brute-force search over its hidden logical states.
        limit = self.maximize_chsh()
        
        # Strain is the excess of observation over this limit
        return limit, max(0, abs(observation) - limit)

def verify_model_constraints():
    print("PL: Exploring constraints of Local Factorizable Models...")
    
    # Planck does not know the bound is 2.
    # It must find it by exploring the model space.
    model = LocalHiddenVariableModel()
    
    print("PL: Running optimization over local hidden variable space...")
    max_s = model.maximize_chsh()
    
    print(f"PL: Optimization complete. Empirical maximum S-statistic for this model class: {max_s}")
    return max_s

if __name__ == "__main__":
    verify_model_constraints()
