# Project Status

**Project:** AlphaZero-Style Chess AI  
**Status:** Active research and engineering  
**Tracking branch:** `chess-strength-training-upgrade`  
**Base branch:** `main`  
**Latest verified baseline:** `f49d6b8f5c87d0e9e7a897c2754af07832a3f3f4` (CPU tests and Stockfish audit passed on workflow revision `55d0db1ba8d0e3331bb4d92542ab183f898a1335`)  
**Current unverified semantic-test repair:** `62bbeff2df149e525715cf119474a0591e6069e8` (fork-test king square corrected; follow-up CI pending)  
**Pull request:** [#1 — Harden chess search, self-play and model evaluation](https://github.com/Nomusa990822/AlphaZero-Style-Chess-AI-Self-Play-Reinforcement-Learning-with-MCTS-and-Policy-Value-Networks/pull/1) (draft; not merged)

> This file is the current snapshot. The chronological engineering record is in [DEVELOPMENT_LOG.md](DEVELOPMENT_LOG.md), and measured training/benchmark results belong in [EXPERIMENT_LOG.md](EXPERIMENT_LOG.md).

## Current verified state

- **Latest semantic-test CI failure:** run [43404336724](https://github.com/Nomusa990822/AlphaZero-Style-Chess-AI-Self-Play-Reinforcement-Learning-with-MCTS-and-Policy-Value-Networks/actions/runs/43404336724) failed because the new fork semantics test expected the black king on e8, while that corpus FEN places it on f8. This was an incorrect test coordinate. The assertion was corrected in `62bbeff2df149e525715cf119474a0591e6069e8`; the repaired full suite is **pending** and this test batch is not yet verified. The failure and repair are recorded in `DEVELOPMENT_LOG.md`.

- The annotation patch initially failed test collection because literal newline escapes were written into Python files (run [43397911821](https://github.com/Nomusa990822/AlphaZero-Style-Chess-AI-Self-Play-Reinforcement-Learning-with-MCTS-and-Policy-Value-Networks/actions/runs/43397911821)). The syntax issue was corrected in `b2dfa830d6100c900e5c944b4bb1c7b3e6361059`; GitHub Actions run [43398823052](https://github.com/Nomusa990822/AlphaZero-Style-Chess-AI-Self-Play-Reinforcement-Learning-with-MCTS-and-Policy-Value-Networks/actions/runs/43398823052) completed successfully.
- Pull request #1 remains a draft and is not merged.
- The documented base `main` revision is `42fecbd6767d53c1950d6bc484dd23bcf4914976`; branch work is isolated from main until the PR is reviewed and merged.
- Tactical benchmark runner and a thirteen-position starter corpus are present, including positions with both White and Black to move. Corpus loading rejects structurally invalid chess positions, terminal positions and illegal acceptable moves. The CLI has mocked tests for device handling, checkpoint errors, deterministic search configuration and JSON reporting. A separate Stockfish-assisted audit script and GitHub Actions workflow compare accepted moves with finite-depth engine evaluations. Stockfish 17.1 at depth 16/MultiPV 5 reviewed all thirteen positions: 13/13 accepted moves were within the configured 150-centipawn tolerance, with zero positions flagged. The JSON report is retained as workflow artifact `tactical-engine-audit` (run [43403925496](https://github.com/Nomusa990822/AlphaZero-Style-Chess-AI-Self-Play-Reinforcement-Learning-with-MCTS-and-Policy-Networks/actions/runs/43403925496)); CPU tests passed in run [43403925592](https://github.com/Nomusa990822/AlphaZero-Style-Chess-AI-Self-Play-Reinforcement-Learning-with-MCTS-and-Policy-Networks/actions/runs/43403925592). This finite-depth agreement is not proof of tactical optimality or motif-label correctness.
- Existing historical training summaries cover five iterations of a six-game configuration each, plus three earlier three-game runs. See the experiment log and raw files under `data/logs/`.

## Implemented capabilities

### Chess representation and network
- 20-plane, 8×8 board representation, including a dedicated en-passant target plane.
- Migration support for legacy 19-plane checkpoint weights and replay samples.
- 4,672-action move representation.
- Residual policy-value network with policy and value heads.

### Search and tactical safeguards
- PUCT-based MCTS with optional Dirichlet root noise.
- Correct side-to-move value perspective during tree backup/selection.
- Deterministic evaluation mode without root Dirichlet noise.
- Exact legal-move mate-in-one discovery and root-level one-ply mate-avoidance filtering.
- These safeguards are deliberately limited: they are not a full tactical search extension or a substitute for deeper calculation.

### Self-play, replay and training
- Self-play outcome targets use the actual final game result from each position's side-to-move perspective; no distance-to-end discount is applied.
- Move-limit adjudication is a draw rather than a material-only pseudo-result.
- Completed-game reporting includes game result, termination reason, move data, sample count and elapsed time.
- Replay persistence uses atomic per-game journal chunks and iteration snapshots, with recovery designed to avoid duplicate replay.
- Candidate training and candidate-versus-best evaluation/promotion workflow.
- Atomic checkpoint persistence and candidate optimizer state aligned with the candidate model on promotion.
- Automatic CUDA, Apple MPS or CPU device selection.

### Evaluation and reproducibility
- Paired colour-swapped candidate evaluation and a confidence-bound promotion gate.
- CPU GitHub Actions test workflow.
- Tactical benchmark loader/scorer with strict FEN validity checks, a controlled motif taxonomy and checkpoint evaluation CLI:
  `evaluate_tactics.py`.
- JSON benchmark output includes checkpoint metadata, device, simulation count, overall, per-motif, per-colour (White/Black to move), and explicitly labelled per-phase scores, plus missed positions.

## Current limitations and evidence boundaries

- The tactical corpus currently has thirteen starter positions covering mating nets, forks, hanging-piece captures, pins, skewers, discovered attacks, defensive resources and promotion tactics, with seven White-to-move and six Black-to-move cases. Each record now requires a human-written tactical rationale and an explicit opening/middlegame/endgame label; these are review metadata, not automatic tactical verification. It does not represent broad tactical coverage. Motif labels are restricted to a documented taxonomy to keep per-motif reports consistent.
- A passing CI run verifies the automated tests, not playing strength.
- Historical iteration summaries show four evaluation draws per iteration and no model promotions. They do not demonstrate an improvement in playing strength.
- No Elo/FIDE rating or engine-strength claim is established by the recorded data.
- The checkpoint evaluation CLI requires an actual compatible checkpoint file. Do not report a checkpoint benchmark score until it has been run against a real checkpoint and its output saved.
- The repository has not yet established a large, independently reviewed tactical suite or a standard external-engine match protocol.

## Prioritised next work

1. Expand the tactical corpus with independently checked positions across defensive resources, discovered attacks, and endgame tactics.
2. Run and record the tactical benchmark against an actual checkpoint when one is available.
3. Establish repeatable playing-strength evaluation: fixed opponents, colour-swapped pairs, sufficient games, openings/starting positions, time or node controls, and uncertainty reporting.
4. Improve search quality and efficiency only with tests and measured comparisons; avoid hard-coded piece-specific move tricks.
5. Keep this status file, development log and experiment log updated in the same change as each meaningful implementation batch. Record every CI run (including failures), the exact failing test/reason, repair revision and the first successful verification run; do not overwrite failures with later passes.

## Update protocol

For every meaningful development batch:
1. Record the date, goal, files/components affected and design decision in `DEVELOPMENT_LOG.md`.
2. Record test command/workflow, exact commit, and pass/fail outcome. Distinguish local tests, CI tests, and benchmark measurements.
3. Add training or benchmark measurements to `EXPERIMENT_LOG.md` only when an actual run produced them.
4. Update this file's verified revision, current state, limitations and next priorities.
5. Never replace missing data with estimates. Use **not run**, **not recorded**, or **pending** explicitly.
