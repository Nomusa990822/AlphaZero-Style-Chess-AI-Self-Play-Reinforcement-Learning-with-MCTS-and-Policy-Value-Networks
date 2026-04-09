<div align="center">

# ♟️ AlphaZero-Style Chess AI  
### Self-Play Reinforcement Learning with MCTS & Deep Neural Networks

![Python](https://img.shields.io/badge/Python-3.12-blue)
![PyTorch](https://img.shields.io/badge/PyTorch-DeepLearning-red)
![Status](https://img.shields.io/badge/Status-AlphaZero--Style-success)
![RL](https://img.shields.io/badge/Reinforcement-Learning-purple)
![MCTS](https://img.shields.io/badge/MCTS-Enabled-orange)

</div>

---

## Overview

This project implements an **AlphaZero-style chess engine from scratch**, combining:

- Deep Neural Networks (Policy + Value)
- Monte Carlo Tree Search (MCTS)
- Self-Play Reinforcement Learning

Unlike traditional chess engines, this system **learns purely from self-play**, without human data.

---

## Key Features

- Full chess environment using `python-chess`
- Board encoding into neural-friendly tensors (19×8×8)
- Residual CNN architecture (AlphaZero-style)
- Policy Head → move probabilities  
- Value Head → board evaluation (-1 to 1)
- MCTS with:
  - PUCT formula
  - Dirichlet noise (exploration)
  - Visit-based action selection
- Self-play training pipeline
- Replay buffer
- AlphaZero loss function
- Checkpointing system
- Model vs model evaluation

---

## System Architecture

```mermaid
flowchart TD

A[Chess Board State] --> B[Board Encoder]
B --> C[Neural Network]

C --> D1[Policy Head]
C --> D2[Value Head]

D1 --> E[MCTS Search]
D2 --> E

E --> F[Visit Counts]
F --> G[Move Selection]

G --> H[Next Board State]
H --> A
```

---

## AI Decision Process

```mermaid
flowchart TD

Start[Current Position] --> Encode[Encode Board]
Encode --> Network[Neural Network]

Network --> Policy[Policy Probabilities]
Network --> Value[Position Value]

Policy --> MCTS
Value --> MCTS

MCTS --> Simulations[Run Simulations]
Simulations --> Visits[Visit Counts]

Visits --> Decision[Select Best Move]
Decision --> Output[Final Move]
```

---

## Training Pipeline

```mermaid
flowchart TD

A[Self-Play Games] --> B[Store in Replay Buffer]
B --> C[Sample Batch]
C --> D[Train Neural Network]
D --> E[Update Model]

E --> F[New Self-Play]
F --> A
```
---

## Project Structure

```
src/
├── engine/        # Chess logic & encoding
├── model/         # Neural network (policy + value)
├── mcts/          # Monte Carlo Tree Search
├── agents/        # MCTS agent
├── training/      # Self-play + training pipeline

tests/             # Unit tests
train_pipeline.py  # Full training loop
main.py            # Quick inference test
```

---



