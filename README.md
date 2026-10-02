<div align="center">

# AlphaZero-Style Chess AI
### Self-Play Reinforcement Learning • Monte Carlo Tree Search • Policy-Value Networks

---

<!-- =========================
     CORE STATUS
========================= -->
<p>
<img src="https://img.shields.io/badge/Status-Active%20Development-020617?style=for-the-badge&logo=github&logoColor=8ef1e5" />
<img src="https://img.shields.io/badge/Architecture-Modular-020617?style=for-the-badge&logo=databricks&logoColor=8ef1e5" />
<img src="https://img.shields.io/badge/AI-Reinforcement%20Learning-020617?style=for-the-badge&logo=pytorch&logoColor=8ef1e5" />
<img src="https://img.shields.io/badge/Chess-Self--Play-020617?style=for-the-badge&logo=chess.com&logoColor=8ef1e5" />
</p>

<!-- =========================
     TECH STACK
========================= -->
<p>
<img src="https://img.shields.io/badge/Python-3.12+-0f172a?style=for-the-badge&logo=python&logoColor=7c9cff" />
<img src="https://img.shields.io/badge/PyTorch-Deep%20Learning-0f172a?style=for-the-badge&logo=pytorch&logoColor=7c9cff" />
<img src="https://img.shields.io/badge/MCTS-Search%20Engine-0f172a?style=for-the-badge&logo=target&logoColor=8ef1e5" />
<img src="https://img.shields.io/badge/Self--Play-Reinforcement%20Learning-0f172a?style=for-the-badge&logo=python&logoColor=8ef1e5" />
<img src="https://img.shields.io/badge/Policy--Value-Neural%20Network-0f172a?style=for-the-badge&logo=pytorch&logoColor=7c9cff" />
</p>

<p>
<img src="https://img.shields.io/badge/Replay%20Buffer-Experience%20Learning-1e293b?style=for-the-badge&logo=databricks&logoColor=8ef1e5" />
<img src="https://img.shields.io/badge/Monte%20Carlo%20Tree%20Search-MCTS-1e293b?style=for-the-badge&logo=googlecloud&logoColor=7c9cff" />
<img src="https://img.shields.io/badge/Neural%20Network-Policy%20%2B%20Value-1e293b?style=for-the-badge&logo=pytorch&logoColor=8ef1e5" />
<img src="https://img.shields.io/badge/Automated-Evaluation-1e293b?style=for-the-badge&logo=githubactions&logoColor=7c9cff" />
</p>

<!-- =========================
     GITHUB META
========================= -->
<p>
<img src="https://img.shields.io/github/stars/Nomusa990822/AlphaZero-Style-Chess-AI-Self-Play-Reinforcement-Learning-with-MCTS-and-Policy-Value-Networks?style=for-the-badge&color=020617" />
<img src="https://img.shields.io/github/forks/Nomusa990822/AlphaZero-Style-Chess-AI-Self-Play-Reinforcement-Learning-with-MCTS-and-Policy-Value-Networks?style=for-the-badge&color=020617" />
<img src="https://img.shields.io/github/issues/Nomusa990822/AlphaZero-Style-Chess-AI-Self-Play-Reinforcement-Learning-with-MCTS-and-Policy-Value-Networks?style=for-the-badge&color=020617" />
<img src="https://img.shields.io/github/last-commit/Nomusa990822/AlphaZero-Style-Chess-AI-Self-Play-Reinforcement-Learning-with-MCTS-and-Policy-Value-Networks?style=for-the-badge&color=020617" />
</p>

---

**A chess engine that learns through experience rather than a fixed opening book.**  
*Play. Learn. Evaluate. Improve.*

</div>

---

# Overview

This project is an **AlphaZero-inspired chess reinforcement-learning system** built around three core ideas:

- **Self-play**
- **Monte Carlo Tree Search (MCTS)**
- **Policy-value neural networks**

Instead of relying primarily on a handcrafted evaluation function or a database of predefined games, the system generates its own chess positions through self-play and uses those experiences to continuously train a neural network.

The trained network learns two complementary tasks:

1. **Policy prediction**  
   → Which moves are promising from the current position?

2. **Value prediction**  
   → How favourable is the current position?

MCTS then combines neural-network guidance with tree search to select moves.

The result is a learning system in which the chess engine repeatedly:

```text
SELF-PLAY
    ↓
GENERATE POSITIONS
    ↓
MCTS SEARCH
    ↓
STORE TRAINING EXPERIENCE
    ↓
TRAIN CANDIDATE MODEL
    ↓
EVALUATE CANDIDATE
    ↓
PROMOTE OR REJECT
    ↓
REPEAT
```
