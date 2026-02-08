# Inference Architecture: specific for Experiment Zero

## Goal
To discover the **Correlation Function** $E(\theta_A, \theta_B)$ purely from raw experimental data, without using neural networks or assuming quantum mechanics.

---

## 1. The Inference Pipeline

Planck's inference engine consists of three distinct stages: **Aggregation**, **Symbolic Search**, and **Verification**.

### Stage 1: Data Aggregation (From Trials to Statistics)
Raw quantum data is probabilistic (binary outcomes +1/-1). Physical laws usually describe *expectations* or *probabilities*, not individual events.
Planck must first convert the raw event log into a statistical summary.

**Input**: Trial Log (N rows)
**Process**:
1.  Group trials by unique setting pairs $(\theta_A, \theta_B)$. 
    *   *Note*: In a real experiment with continuous variables, Planck would need to bin data. For Experiment Zero, we assume discrete setting pairs are repeated many times.
2.  Calculate the **Empirical Correlation** for each group:
    $$ E_{obs}(\theta_A, \theta_B) = \frac{1}{N_{group}} \sum (r_A \cdot r_B) $$
    where $r_A, r_B \in \{+1, -1\}$.
**Output**: A dataset of $( \theta_A, \theta_B, E_{obs} )$.

### Stage 2: Symbolic Search (Genetic Programming)
This is the core "AI" component. Instead of training weights, we **evolve equations**.

**Search Space (Primitives)**:
-   **Variables**: $x$ (for $\theta_A$), $y$ (for $\theta_B$)
-   **Operators**: $+$, $-$, $*$, $/$
-   **Functions**: $\sin$, $\cos$, $\exp$
-   **Constants**: Real numbers $c$

**Algorithm**:
We use **Genetic Programming (GP)** (e.g., via `PySR` or a custom implementation):
1.  **Initialize**: Generate a population of random mathematical expressions (trees).
2.  **Evaluate**: Calculate the fitness of each expression against the aggregated data.
    -   **Loss Function**: $MSE = \frac{1}{M} \sum (f(x_i, y_i) - E_{obs, i})^2$
    -   **Complexity Penalty**: Penalize the number of nodes in the expression tree (Occam's Razor).
3.  **Evolve**:
    -   **Selection**: Keep the best equations.
    -   **Crossover**: Combine parts of two equations (e.g., take $f(x)$ from one and $g(y)$ from another).
    -   **Mutation**: Randomly change an operator or variable.
4.  **Repeat**: Iterate until convergence or max generations.

**Why this is valid scientifically**:
-   It searches the space of *functional forms*, not black-box mappings.
-   It prioritizes simplicity, aligning with the scientific method (simplest explanation is best).
-   It yields an interpretable equation, not a matrix of weights.

### Stage 3: Verification & Falsification
The search will produce a set of candidate equations (Pareto Frontier of Accuracy vs. Complexity).
Planck must select the *best* candidate and verify it.

**Selection Criteria**:
-   **Pareto Optimal**: The equation that gives the biggest drop in error for the smallest increase in complexity.
-   **Robustness**: If the equation $f(x, y)$ relies on a "magic number" like $5.12391$ that doesn't correspond to $\pi$ or $e$, it is suspicious (though allowed if it fits perfectly).

**Falsification Test**:
-   Planck must predict the correlation for a **held-out** set of angles (e.g., test on $\theta = 0.5$ if trained on $0.0, 1.0$).
-   If the candidate equation fails to predict the unseen data, it is rejected.
-   *Strict Rule*: If no equation fits the data with low complexity, Planck reports "No simple law found" rather than overfitting.

---

## 2. Expected Outcome for Experiment Zero
If successful, Planck should output:
1.  **Candidate 1 (Linear)**: $0.0$ (Error: High)
2.  **Candidate 2 (Linear)**: $0.5 * (x - y)$ (Error: Medium)
3.  **Candidate 3 (Trigonometric)**: $-\cos(x - y)$ (Error: Near Zero, Complexity: Low)

Planck selects **Candidate 3** as the discovered law.

---

## 3. Implementation Strategy
We will use Python for the implementation.
-   **Library**: `PySR` (Python Symbolic Regression) is excellent for this. It uses a high-performance Julia backend but provides a friendly Python API.
-   **Fallback**: `gplearn` (pure Python, simpler but less powerful).
-   **Recommendation**: Start with `PySR` for robustness.
