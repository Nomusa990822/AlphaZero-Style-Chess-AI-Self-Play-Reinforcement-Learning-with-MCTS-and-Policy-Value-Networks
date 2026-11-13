## 2026-11-13 — Add black-to-move tactical coverage

**Corpus revision:** `2e18f4d35b12fce02d6777d0afb4f1d0d0390e94`  
**Test revision:** `8fc932a848484765f9037079cf49288adbddbc4f`

### Changes
- Added a reviewed black-to-move knight fork in which the move checks the white king while attacking the white queen.
- Strengthened the corpus test to require positions with both White and Black to move, alongside validity, non-terminal-state and legal-move checks.
- Increased the starter corpus from three to four positions. This is a small coverage improvement, not evidence of broad tactical competence.

### Verification
- The prior strict-validation revision passed GitHub Actions run [43395789548](https://github.com/Nomusa990822/AlphaZero-Style-Chess-AI-Self-Play-Reinforcement-Learning-with-MCTS-and-Policy-Value-Networks/actions/runs/43395789548).
- CI for this corpus/test update is pending.
- No real-checkpoint tactical benchmark was run; no playing-strength improvement is claimed.

### Follow-up
- Add more independently reviewed motifs and test the checkpoint evaluation CLI without requiring an actual checkpoint or accelerator.

# Development Log

## 2026-11-13 — Strict tactical-position legality validation

**Implementation revision:** `c81b7e1a91bff1fc91f98aaf4e53419a00c27360`  
**Test revisions:** `836a17bf024c0a0a8fcffe3073fc85021eef8e6a`, `573a2b6360d28d7d1769019b4e1fdff25f32afcc`

### Changes
- Strengthened `TacticalPosition.from_dict` to reject structurally invalid chess positions using `python-chess` position validation, in addition to rejecting terminal positions and illegal acceptable UCI moves.
- Added a regression test for an impossible position with adjacent kings.
- Strengthened the curated-corpus test so every entry must be a valid, non-terminal chess position and every accepted move must be legal.

### Verification
- GitHub Actions is triggered by these branch updates; the final test result is pending until the latest run completes.
- No local test execution or real-checkpoint tactical benchmark is claimed in this entry.
- No new tactical motifs or benchmark scores are claimed; this batch improves dataset integrity only.

### Follow-up
- Expand the corpus with independently checked examples for both sides and a broader set of tactical motifs, then test the checkpoint evaluation CLI.

This is the chronological engineering journal for the project. Entries describe implemented changes and verified evidence, not proposed capabilities. The initial entries consolidate earlier work so future batches can be tracked consistently.

## 2026-11-13 — Tactical checkpoint evaluation and benchmark corpus

**Revision:** `f78fa3a18f0855fc4faa59761e932294298edaf0`  
**Pull request:** [#1](https://github.com/Nomusa990822/AlphaZero-Style-Chess-AI-Self-Play-Reinforcement-Learning-with-MCTS-and-Policy-Value-Networks/pull/1)

### Changes
- Added `evaluate_tactics.py` to load a checkpoint and run deterministic MCTS against a JSONL tactical corpus.
- Added `benchmarks/tactical_positions.jsonl` with three starter examples: mating net, knight fork and hanging-piece capture.
- Added corpus loading/legality test coverage in `tests/test_tactical_corpus.py`.
- Documented corpus format, checkpoint invocation and limitations in `benchmarks/README.md`.

### Verification
- GitHub Actions workflow run [43389599997](https://github.com/Nomusa990822/AlphaZero-Style-Chess-AI-Self-Play-Reinforcement-Learning-with-MCTS-and-Policy-Value-Networks/actions/runs/43389599997): **completed successfully** for this revision.
- A real checkpoint benchmark result is **not recorded here**. CI passing is not a tactical-strength score.
- Corpus size is three positions and must not be presented as comprehensive tactical coverage.

## Earlier engineering milestones — consolidated history

The following items summarise prior implementation work on the development branch. Exact dates and commit references are included only where they were preserved in the project history available for this log; otherwise they are intentionally not inferred.

### MCTS value perspective
- Corrected PUCT value perspective so a child value, represented from the child side-to-move perspective, is negated when interpreted by its parent.
- Known implementation commit: `f903260d3e10614b3134d894dea1d7fd15f672a5`.

### Board representation and checkpoint compatibility
- Expanded the board input from 19 to 20 planes by adding a dedicated en-passant target plane.
- Preserved the fullmove counter and other existing state planes.
- Added migration handling for legacy 19-plane checkpoint weights and replay samples rather than discarding prior learned state.

### Self-play targets and game termination
- Changed value targets to use the actual final game outcome from each training position's side-to-move perspective.
- Removed distance-from-game-end discounting from outcome targets.
- Changed maximum-move adjudication to a draw rather than relying on material-only or pseudo-mobility adjudication.

### Game reporting and replay durability
- Added per-game completion reporting with PGN, UCI move sequence, result, termination reason, sample count and elapsed time.
- Added atomic per-game replay journal chunks and iteration-level snapshots.
- Added recovery from journal-only state, including the first-iteration crash case, with replay recovery designed to avoid duplication.

### Evaluation and promotion controls
- Added deterministic candidate evaluation without Dirichlet root noise.
- Added paired colour-swapped evaluation games.
- Added a one-sided 90% lower confidence-bound improvement gate to promotion decisions.
- Aligned candidate optimizer state with the candidate model when promoting.
- Added atomic checkpoint saving.

### Device portability and CI
- Added automatic device selection for CUDA, Apple MPS and CPU.
- Added a CPU GitHub Actions pytest workflow.

### Tactical search safeguards
- Added `src/mcts/tactics.py` helpers to find all legal immediate checkmates and identify moves that do not permit an immediate opponent mate-in-one.
- Updated root search/action-target handling to prioritise immediate mate and filter one-ply mate-losing moves when at least one safe legal move exists.
- Preserved a forced-loss fallback when every legal move permits mate in one.
- Added tests for both colours, policy normalisation, board-state preservation and forced-loss behaviour.
- Scope is one-ply mate detection/avoidance, not a general tactical engine.

## Ongoing record template

Copy this section for each future engineering batch.

### YYYY-MM-DD — Short change title

- **Goal:**
- **Design decision:**
- **Implementation/files:**
- **Tests added/changed:**
- **Verification:** (exact command or CI run URL; pass/fail/not run)
- **Commit:**
- **Known limitations/regressions:**
- **Follow-up:**
