# Randomness Policy

To ensure reproducibility, the following rules apply:
1. **Fixed Seeds**: All stochastic processes (e.g., train/test splits, noise injection) must use a fixed seed (Default: 42).
2. **Library Versions**: Exact versions of NumPy and Pandas must be recorded (see environment.lock.yml).
3. **Hardware Determinism**: Where possible, avoid non-deterministic GPU operations.
