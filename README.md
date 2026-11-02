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

---

# Core Capabilities

## 1. Self-Play Reinforcement Learning

The engine generates its own training data by playing chess against itself.

Each self-play game produces training examples containing information derived from the position, search policy, and eventual game outcome.

The system can generate multiple games per training iteration:

```text
Current Best Model
        ↓
     Self-Play
        ↓
   Game Positions
        ↓
   Training Samples
        ↓
   Replay Buffer
```

This allows the model to learn from positions that arise naturally from its own playing behaviour.

---

## 2. Monte Carlo Tree Search

MCTS is responsible for exploring possible moves before the engine commits to a move.

The search repeatedly evaluates candidate actions and builds a search tree around the current position.

Conceptually:

```text
                  Current Position
                         │
          ┌──────────────┼──────────────┐
          ↓              ↓              ↓
        Move A         Move B         Move C
          │              │              │
       Search          Search          Search
          │              │              │
          └──────────────┼──────────────┘
                         ↓
                  Select Best Move
```

The neural network provides guidance to the search rather than forcing the engine to examine every legal move equally.

---

## 3. Policy-Value Neural Network

The model learns two outputs from a chess position.

### Policy Head

The policy component estimates the probability distribution over possible moves.

```text
Chess Position
      ↓
Neural Network
      ↓
Policy Head
      ↓
Move Probabilities
```

This gives MCTS a learned prior about which moves deserve more attention.

### Value Head

The value component estimates the expected outcome of the position.

```text
Chess Position
      ↓
Neural Network
      ↓
Value Head
      ↓
Position Evaluation
```

Together, the policy and value predictions provide MCTS with both:

- Where to search
- How promising a position appears

---

# Learning Loop

The complete training pipeline operates iteratively.

```text
┌───────────────────────────────┐
│       CURRENT BEST MODEL      │
└───────────────┬───────────────┘
                ↓
        Generate Self-Play
                ↓
        ┌───────────────┐
        │ Chess Games   │
        └───────┬───────┘
                ↓
        Training Samples
                ↓
        Replay Buffer
                ↓
        Train Candidate Model
                ↓
        Candidate Evaluation
                ↓
       ┌────────┴─────────┐
       ↓                  ↓
   Candidate            Candidate
   Promoted             Rejected
       ↓                  ↓
   New BEST          Keep BEST
       │                  │
       └────────┬─────────┘
                ↓
          Next Iteration
```

This creates an iterative improvement mechanism rather than simply training one model once.

---

# Candidate Model System

A major part of the training architecture is the separation between the current best model and the candidate model.

The candidate is trained from experience generated from the current best model.

After training, the candidate is evaluated against the current best model.

For example:

```text
BEST MODEL
    │
    ├── Self-play
    │
    └── Training data
            │
            ↓
      CANDIDATE MODEL
            │
            ↓
       Evaluation
            │
       ┌────┴────┐
       ↓         ↓
   Promoted    Rejected
       │         │
       ↓         ↓
    NEW BEST   KEEP BEST
```

This prevents every newly trained model from automatically replacing the existing model.

A candidate must demonstrate sufficient performance according to the configured promotion criteria.

---

# Replay Buffer

The replay buffer stores training experiences generated through self-play.

Its purpose is to provide the neural network with a larger and more diverse collection of positions instead of training only on the most recently generated games.

The pipeline is:

```text
Self-Play Games
      ↓
Training Samples
      ↓
Replay Buffer
      ↓
Mini-Batches
      ↓
Neural Network Training
```

The replay buffer has a configurable capacity so that training remains bounded as additional self-play games are generated.

---

# Training System

The neural network is trained using batches sampled from the replay buffer.

Training tracks multiple loss components, including:

- Total loss
- Policy loss
- Value loss

Example training output:

```text
Epoch 1:
    total = ...
    policy = ...
    value = ...

Epoch 2:
    total = ...
    policy = ...
    value = ...

...

Epoch 6:
    total = ...
    policy = ...
    value = ...
```

Monitoring both policy and value loss helps provide visibility into how the different learning objectives are behaving during training.

---

# Self-Play Configuration

The training pipeline exposes configurable parameters controlling the self-play process.

Examples include:

| Parameter | Purpose |
|---|---|
| `self_play_games_per_iteration` | Number of self-play games generated per iteration |
| `self_play_max_moves` | Maximum number of moves allowed in a game |
| `self_play_opening_temperature_moves` | Number of opening moves affected by exploration temperature |
| `self_play_opening_temperature` | Exploration temperature during opening play |
| `self_play_late_temperature` | Exploration temperature later in the game |
| `self_play_resign_threshold` | Optional resignation threshold |
| `self_play_min_moves_before_resign` | Minimum game length before resignation |
| `self_play_adjudicate_on_max_moves` | Whether games reaching the move limit are adjudicated |
| `self_play_adjudication_threshold` | Threshold used for max-move adjudication |

These parameters allow the balance between exploration, game length, and training-data generation to be adjusted without redesigning the underlying engine.

---

# MCTS Configuration

The search process is also configurable.

Important parameters include:

| Parameter | Purpose |
|---|---|
| `train_mcts_simulations` | Number of MCTS simulations during self-play |
| `eval_mcts_simulations` | Number of MCTS simulations during evaluation |
| `eval_add_dirichlet_noise` | Adds exploration noise during evaluation when enabled |
| `eval_dirichlet_alpha` | Dirichlet noise concentration |
| `eval_dirichlet_epsilon` | Noise contribution |
| `eval_temperature` | Move-selection temperature during evaluation |

This separates the computational budget used during training from the budget used when evaluating candidate models.

---

# Candidate Evaluation

After a candidate has been trained, the system evaluates it against the current best model.

The evaluation records:

```text
W     = Candidate Wins
L     = Candidate Losses
D     = Draws
Score = Candidate Evaluation Score
```

Example:

```text
Evaluation result:
W=8, L=4, D=4, Score=0.625
```

The configured promotion threshold determines whether the candidate becomes the new best model.

For example:

```text
Candidate score
      ↓
Compare against promotion threshold
      ↓
 ┌───────────────┐
 │               │
 ↓               ↓
PROMOTE        REJECT
 │               │
 ↓               ↓
BEST MODEL    KEEP BEST
```

---

# Exploration vs Exploitation

The system deliberately balances exploration and exploitation.

During self-play, temperature parameters can encourage the model to explore different moves rather than repeatedly selecting the same action.

MCTS provides another layer of exploration by searching alternative branches of the game tree.

This creates a learning cycle where the engine can discover positions and moves that were not explicitly programmed into it.

---

# Training Iterations

Training is divided into discrete iterations.

Each iteration follows the same general process:

```text
ITERATION N
│
├── Generate self-play games
│
├── Add samples to replay buffer
│
├── Build candidate from BEST model
│
├── Train candidate
│
├── Save candidate checkpoint
│
├── Evaluate candidate
│
└── Promote or reject candidate
```

The process then continues into the next iteration.

This makes the training pipeline reproducible and easier to monitor.

---

# Checkpoints

The training system maintains model checkpoints under:

```text
data/
└── checkpoints/
    ├── best_model.pt
    └── latest_candidate.pt
```

### `best_model.pt`

The currently accepted best-performing model.

This is the model used as the foundation for subsequent training iterations.

### `latest_candidate.pt`

The most recently trained candidate model.

A candidate can exist without becoming the best model.

This distinction is important because a trained model is not automatically considered an improvement.

---

# Training Logs

Training metrics are stored under:

```text
data/logs/
```

The logs provide a persistent record of training progress, allowing experiments to be compared without relying solely on terminal output.

---

# Project Structure

```text
AlphaZero-Style-Chess-AI-Self-Play-Reinforcement-Learning-with-MCTS-and-Policy-Value-Networks/
│
├── configs/
│
├── data/
│   ├── checkpoints/
│   │   ├── best_model.pt
│   │   └── latest_candidate.pt
│   │
│   └── logs/
│
├── docs/
│
├── notebooks/
│
├── src/
│
├── tests/
│
├── main.py
├── play.py
├── train_pipeline.py
├── requirements.txt
├── LICENSE
└── README.md
```

The project separates the training pipeline, gameplay interface, source modules, tests, configuration, checkpoints, and experiment data.

---

# Training Pipeline

The main training pipeline is launched with:

```bash
python train_pipeline.py
```

The pipeline loads the current best model when configured to resume training:

```text
Loaded best model from data/checkpoints/best_model.pt
```

It then begins the iterative self-play and training process.

---

# Installation

Clone the repository:

```bash
git clone https://github.com/Nomusa990822/AlphaZero-Style-Chess-AI-Self-Play-Reinforcement-Learning-with-MCTS-and-Policy-Value-Networks.git
```

Enter the project directory:

```bash
cd AlphaZero-Style-Chess-AI-Self-Play-Reinforcement-Learning-with-MCTS-and-Policy-Value-Networks
```

Create a virtual environment:

```bash
python -m venv .venv
```

Activate it on Linux/macOS:

```bash
source .venv/bin/activate
```

Activate it on Windows:

```bash
.venv\Scripts\activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

---

# Running Training

Start the reinforcement-learning pipeline:

```bash
python train_pipeline.py
```

The terminal displays the current training configuration and progress.

Example:

```text
Pipeline config:
    iterations=5
    self_play_games_per_iteration=12
    self_play_max_moves=400
    training_epochs=6
    train_mcts_simulations=80
    eval_mcts_simulations=100
    gating_games=16
```

The pipeline then generates self-play games and trains the candidate model.

---

# Playing Against the AI

The project also provides a gameplay interface through:

```bash
python play.py
```

This allows the trained model to be used outside the training loop.

The gameplay system uses the trained neural network together with MCTS to select moves.

---

# Training Output

A typical training iteration follows this pattern:

```text
ITERATION 1

Generating self-play games...

Game 1: result=...
Game 2: result=...
Game 3: result=...
...

Replay buffer size: ...

Building candidate model from best model...

Training candidate model...

Epoch 1: ...
Epoch 2: ...
...

Saving latest candidate checkpoint...

Evaluating candidate vs current best...

Evaluation result:
W=...
L=...
D=...
Score=...

Candidate promoted to BEST model.
```

or:

```text
Candidate rejected. Keeping current BEST model.
```

This makes the learning process observable directly from the terminal.

---

# Design Philosophy

This project is built around several principles.

### 1. Learn Through Experience

The engine generates its own training data through self-play instead of depending entirely on manually labelled chess positions.

### 2. Search + Learning

The neural network and MCTS serve different but complementary purposes.

```text
Neural Network
      +
     MCTS
      ↓
Better Move Selection
```

### 3. Continuous Improvement

A candidate must demonstrate sufficient performance before replacing the current best model.

### 4. Experimentation

Training parameters are intentionally configurable so that different learning strategies can be tested.

### 5. Observable Learning

Training metrics, self-play results, replay-buffer size, candidate evaluation, and checkpoints provide visibility into the learning process.

---

# AlphaZero-Inspired Architecture

The project takes inspiration from the general AlphaZero approach:

```text
                 CHESS POSITION
                       │
                       ↓
              POLICY-VALUE NETWORK
                  │           │
                  ↓           ↓
               POLICY       VALUE
                  │           │
                  └─────┬─────┘
                        ↓
                       MCTS
                        │
                        ↓
                  SELECT MOVE
                        │
                        ↓
                   SELF-PLAY
                        │
                        ↓
               TRAINING EXAMPLES
                        │
                        ↓
                 REPLAY BUFFER
                        │
                        ↓
                 CANDIDATE MODEL
                        │
                        ↓
                  EVALUATION
                        │
                 ┌──────┴──────┐
                 ↓             ↓
              PROMOTE        REJECT
                 │             │
                 └──────┬──────┘
                        ↓
                  NEXT ITERATION
```

The implementation is AlphaZero-inspired, not a claim of reproducing the original AlphaZero system or its training scale.

---

# What Makes This Project Different

This project is not simply a chess program with a neural network attached.

The model participates in a feedback loop:

```text
PLAY
 ↓
OBSERVE
 ↓
LEARN
 ↓
SEARCH
 ↓
PLAY AGAIN
```

The objective is to allow playing strength to emerge from repeated self-play and training rather than hard-coding a complete chess strategy.

---

# Experimentation Roadmap

Future development can explore:

- Larger self-play batches
- Longer training runs
- Increased MCTS simulations
- Improved neural-network architectures
- Stronger position encoding
- More efficient replay-buffer sampling
- Candidate-vs-best evaluation improvements
- Interactive self-play visualisation
- Human-vs-AI gameplay
- AI-vs-AI gameplay
- Training dashboards
- Model strength benchmarking
- Persistent experiment tracking

---

# Current Training Direction

The training system is designed to support progressively larger self-play experiments.

For example:

```text
12 games / iteration
        ↓
25 games / iteration
        ↓
More training positions
        ↓
More diverse experience
        ↓
Potentially stronger learning signal
```

Increasing the number of self-play games increases the amount of experience available to each training iteration, while also increasing computational cost.

The appropriate configuration therefore depends on the available compute and the behaviour observed during evaluation.

---

# Technical Demonstrations

This project demonstrates practical implementation of:

- Reinforcement learning
- Self-play learning
- Monte Carlo Tree Search
- Neural-network inference
- Policy prediction
- Value prediction
- Experience replay
- Candidate model training
- Automated model evaluation
- Model checkpointing
- Iterative learning pipelines
- Exploration strategies
- Chess state representation
- AI experimentation

---

# Project Goals

The long-term objective is to develop a chess-playing system that progressively improves through its own generated experience.

The project therefore focuses not only on:

> Can the model play chess?

but also on:

> Can the model learn to play better through repeated self-play?

That distinction is the foundation of the project.

---

<div align="center">

**Play. Learn. Search. Improve.**

*An AlphaZero-inspired experiment in autonomous chess learning.*

---

© 2026 Built by Nomusa Shongwe

</div>
