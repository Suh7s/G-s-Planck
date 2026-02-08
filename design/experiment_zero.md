# Experiment Zero: Bell-CHSH Test (Design Spec)

## 1. The Experiment
The simplest experiment that guarantees a non-classical discovery is the **Bell-CHSH Experiment** involving two entangled Qubits (spin-1/2 particles).

### Rationale
- A single Qubit can be modeled classically as a hidden variable (e.g., a "spin vector" with probability distributions). While complex, it doesn't *force* a quantum interpretation.
- A Bell Test violates **Local Realism** (Bell's Theorem). No classical hidden variable theory can reproduce the correlations of a Bell state without violating locality or statistical independence.
- **Discovery Goal**: Planck must discover that the correlation function $E(\theta_A, \theta_B)$ violates the CHSH inequality $|S| \le 2$.

### Setup
- **Source**: Emits pairs of entangled particles (e.g., singlet state $|\psi^-\rangle = \frac{1}{\sqrt{2}}(|\uparrow\downarrow\rangle - |\downarrow\uparrow\rangle)$).
- **Observer A (Alice)**: Has a detector with adaptable setting $\theta_A$ (angle).
- **Observer B (Bob)**: Has a detector with adaptable setting $\theta_B$ (angle).
- **Outcomes**: Each measurement yields a binary result $r \in \{+1, -1\}$.

---

## 2. The Data Schema (What Planck Sees)
Planck is **blind** to the physics. It only sees a log of experimental trials.

### Input Data
A table (or stream) of `N` independent trials. Each row `i` contains:
1.  `setting_A` ($\theta_A^{(i)}$): A floating-point angle in $[0, 2\pi)$.
2.  `setting_B` ($\theta_B^{(i)}$): A floating-point angle in $[0, 2\pi)$.
3.  `outcome_A` ($r_A^{(i)}$): An integer $\in \{+1, -1\}$.
4.  `outcome_B` ($r_B^{(i)}$): An integer $\in \{+1, -1\}$.

**Example Row:**
| Trial | $\theta_A$ | $\theta_B$ | $r_A$ | $r_B$ |
| :--- | :--- | :--- | :--- | :--- |
| 1 | 0.0 | 0.785 | +1 | -1 |
| 2 | 1.57 | 0.785 | -1 | -1 |

Planck does **not** see wavefunctions, matrices, or the concept of "entanglement".

---

## 3. The "Discovery" (What Counts as Success)
A genuine discovery consists of three stages:

### Stage 1: Correlation Modeling (Symbolic Regression)
Planck must derive a symbolic expression for the expectation value of the product of outcomes:
$$ E(\theta_A, \theta_B) = \langle r_A r_B \rangle \approx \frac{1}{N} \sum r_A r_B $$
- Classical target: $E \propto \theta_A \cdot \theta_B$ (linear) or similar.
- **Quantum Discovery**: $E(\theta_A, \theta_B) = -\cos(\theta_A - \theta_B)$.
- Finding the cosine relationship strictly from data is the first "law".

### Stage 2: Falsification of Local Realism (The "Nobel Prize" Step)
Planck must evaluate the **CHSH quantity** $S$ using its derived model (or raw data) across 4 specific setting pairs $(a, b), (a, b'), (a', b), (a', b')$:
$$ S = E(a, b) - E(a, b') + E(a', b) + E(a', b') $$
- **Discovery**: It must calculate $S$ and find that $|S| > 2$ (specifically $S \approx 2\sqrt{2} \approx 2.82$).
- It must then assert: *"The data violates the bound $S \le 2$, implying that no local hidden variable model exists."*

### Stage 3: Minimal Axiom Derivations
- It should identify the minimal set of assumptions needed to explain the data (e.g., "The state space is 2D and non-commutative").

---

## 4. Avoiding Cheating & Leakage
To ensure Planck infers physics rather than memorizing it:

1.  **No Trigonometry Bias**: Although `sin` and `cos` are allowed primitives, they should not be prioritized over polynomials or exponentials. The system must *select* them because they fit the data best (Occam's Razor).
2.  **Blind Variables**: The angles should be provided as abstract scalars $x, y \in \mathbb{R}$. The system must discover the periodicity ($2\pi$) on its own.
3.  **Counterfactual Testing**: We must verify the discovered model on *unseen* angles. If it overfits (e.g., uses a 10th-order polynomial instead of cosine), it fails.
4.  **Symbolic Validation**: The output must be an interpretable equation, not a neural network black box.

---

## Next Steps
1.  **Simulator**: Build a Python script to generate this synthetic data using `numpy`.
2.  **Inference Engine**: Design the symbolic regression pipeline (e.g., using `pysr` or a custom genetic algorithm) to find $E(\theta_A, \theta_B)$.
