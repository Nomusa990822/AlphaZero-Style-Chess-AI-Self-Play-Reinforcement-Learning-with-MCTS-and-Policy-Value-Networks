# Paired checkpoint strength-evaluation protocol

**Status:** confirmatory v1 executed; independent v2 implementation merged, follow-up evaluation pending (2026-11-15)  
**Protocol version:** 1.0  
**Prepared:** 2026-11-15  
**Purpose:** compare one immutable candidate checkpoint directly against one immutable incumbent without training, checkpoint mutation, or automatic promotion during the evaluation itself.

## 1. Decision question and scope

The primary question is:

> Does the candidate score more than 0.50 against the exact incumbent on a frozen, colour-balanced set of distinct opening positions, with the predeclared paired uncertainty bound also above 0.50?

This is a relative, fixed-suite result. It is not an Elo rating, an absolute playing-strength estimate, a proof of generalisation to every opening, or a value-calibration measurement.

The first comparison target is the preserved pair:

| Role | Checkpoint | SHA-256 |
|---|---|---|
| Incumbent / baseline | epoch-0 `best_model.pt` | `7a9fdacbd14f6423e34b2edb470d255e15081a12b1e66faf204a5e07e24e4471` |
| Candidate / challenger | epoch-10 `latest_candidate.pt` | `101294ee17c79fd9e4816b3e2676b8f87487c4932172861f59b96550c345af00` |

These identities must be verified against the downloaded bytes before any game starts. A mismatch, missing file, incompatible checkpoint, or metadata inconsistency aborts the run.

## 2. Opening-suite design

The repository's current `benchmarks/evaluation_openings.jsonl` contains 12 distinct opening positions. It has already been used in prior diagnostics and should be treated as a development/regression suite, not as a repeatedly reused untouched confirmation set.

Create a separate, versioned confirmatory suite:

- **24 distinct opening positions**, yielding 24 paired observations and 48 games.
- Cover at least 8 opening families, with no family contributing more than 4 positions.
- Include open, semi-open, closed, queen-pawn, king-pawn and flank-opening structures.
- Use a mixture of common main-line and sound less-common continuations; do not select positions based on how either evaluated checkpoint performs.
- Store stable IDs, the exact legal UCI move sequence from the standard initial board, resulting FEN, opening-family label and suite version.
- Each position must be non-terminal, valid, reachable through legal moves, and unique by normalized FEN.
- Exclude the existing 12 development-suite positions and positions copied from the 35-position tactical corpus or its 11 annotated tactical sequences.
- Freeze the suite and record its SHA-256 before loading either checkpoint for evaluation. Do not change positions after seeing results.

The suite is a curated, reproducible sample of opening diversity, not a statistically random sample of all possible chess positions. Conclusions must remain scoped accordingly.

## 3. Paired and colour-balanced match design

Each opening produces exactly two games:

1. Candidate plays White and incumbent plays Black from the stored opening position.
2. Candidate plays Black and incumbent plays White from the colour-mirrored version of that same opening position.

Thus each opening pair contributes one game for each candidate colour. Across 24 opening pairs:

- 48 completed games total.
- Candidate plays White 24 times and Black 24 times.
- Incumbent plays White 24 times and Black 24 times.
- Each pair is scored as one paired observation.

Use the same model inference path and MCTS settings for both checkpoints. Evaluation settings are fixed before dispatch:

| Setting | Protocol value |
|---|---|
| Device | CPU |
| MCTS simulations per move | 50 |
| Dirichlet root noise | Disabled |
| Move temperature | 0.0 |
| Maximum plies per game | 200 |
| Opening pairs | 24 |
| Games | 48 |
| Checkpoint inference | Evaluation mode; no gradients or optimizer |
| Checkpoint writes | None |

The exact Python, PyTorch, chess-library, source commit and workflow-run IDs must be included in the report. Set and record random seeds for every supported random source. If any component remains nondeterministic, disclose that limitation rather than claiming bit-for-bit reproducibility.

A game ending under the chess rules is scored normally. A game reaching the 200-ply cap is recorded as a draw with an explicit `move_cap_draw` termination reason. Report cap draws separately. No engine adjudication or manual result substitution is allowed.

An illegal move from either agent aborts the complete evaluation. It is a protocol failure, not a loss, and the result is ineligible for promotion. Do not silently skip the game, replace it, or count it as a candidate loss.

## 4. Scoring and primary statistical criterion

Score each candidate game from the candidate's perspective:

- Win = 1.0
- Draw = 0.5
- Loss = 0.0

For opening pair \(i\), define the paired score:

\[
P_i = \frac{S_{i,\text{candidate-white}} + S_{i,\text{candidate-black}}}{2}
\]

Each \(P_i\) is in \{0, 0.25, 0.5, 0.75, 1\}. The overall candidate score is the mean of the 24 paired scores (equivalently the score across all 48 games).

The predeclared promotion-evidence gate is conjunctive:

1. All 24 opening pairs / 48 games complete successfully.
2. Candidate overall score is strictly greater than 0.50.
3. The one-sided 90% lower confidence bound for the mean paired score is strictly greater than 0.50.
4. No illegal move, missing game, checkpoint mismatch, invalid opening, or report-integrity failure occurs.
5. The candidate does not show a material colour-specific regression hidden by the aggregate score; report White/Black outcomes separately and require a human review if one colour's score is below 0.40.

For the paired lower bound, use the one-sided Student-t interval over the 24 opening-pair scores:

\[
LCB_{90} = \bar P - t_{0.90,23}\frac{s_P}{\sqrt{24}}
\]

where \(\bar P\) is the mean paired score, \(s_P\) is the sample standard deviation and \(t_{0.90,23}\) is the 90th percentile of Student's t distribution with 23 degrees of freedom. The implementation must compute this quantile from a trusted statistical library or a verified constant and test it.

**Important existing-code correction:** `src/training/evaluator.py` currently subtracts `1.645 × standard error` while labelling the result a one-sided 90% lower bound. 1.645 is approximately the standard-normal one-sided 95% critical value, not the one-sided 90% value; it also does not use the finite-sample Student-t critical value. Do not reuse that statistic unchanged under a 90% label. Correct the implementation and add numerical unit tests before using the revised gate. The existing evaluator also has a 12-pair minimum; its constants and suite-loading validation must be updated together for this 24-pair protocol.

This confidence bound is an approximate fixed-suite uncertainty summary, not an Elo confidence interval or a population-wide chess-strength guarantee. The 24 opening pairs are the analysis units; do not treat the 48 individual games as 48 independent observations.

## 5. Secondary diagnostics (reported, not substituted for the primary gate)

The report must preserve raw game-level results and include:

- Wins, losses and draws overall.
- Candidate-as-White and candidate-as-Black results and scores.
- Every opening ID and its two game outcomes and paired score.
- Termination type and ply count for every game, including move-cap draws.
- Illegal-move count (must be zero for a valid run).
- Per-game PGN, UCI move list, starting FEN and final result.
- Checkpoint filenames, sizes, metadata and SHA-256 hashes.
- Opening-suite version and SHA-256.
- Exact MCTS and runtime configuration.
- Aggregate score, paired-score mean/standard deviation and one-sided 90% LCB.
- A clear list of gate failures and interpretation limits.

Tactical-position accuracy, annotated sequence completion, policy top-1, MCTS root choices and colour-mirror consistency remain separate diagnostic measures. They must not be blended into the primary match score or used to rescue a failed match gate.

Value calibration is a separate experiment. It requires raw model value predictions paired with final game outcomes on held-out games, with train/validation/test separation by complete game. Do not infer calibration from this head-to-head result or from outcome-target distributions alone.

## 6. Reproducibility, independence and anti-overfitting controls

- Keep the existing 12-opening suite as a development/regression suite.
- Freeze a new 24-opening confirmatory suite before evaluating these checkpoint identities.
- Record the suite hash and source revision in the run artifact.
- Do not tune model weights, MCTS settings, opening selection or acceptance criteria after inspecting confirmatory results.
- Do not repeatedly use the same confirmatory result to claim evidence for later candidates. Track every candidate evaluated against each suite version; after repeated development against a frozen suite, require a newly constructed confirmatory suite for a final independent confirmation.
- A failed or incomplete run is invalid and must be repaired and rerun under the same frozen protocol; never combine partial games from separate runs.
- A result that fails any promotion condition leaves the incumbent checkpoint unchanged and the candidate unpromoted.

## 7. Implementation checklist before dispatch

The v1 protocol is implemented and has been executed. The independent_v2 implementation is also merged; its second match awaits manual dispatch.

- [x] Add and validate `benchmarks/evaluation_openings_confirmatory_v1.jsonl` with 24 unique positions from at least 8 opening families.
- [x] Add tests proving every opening line is legal, non-terminal, unique, and disjoint from the development/tactical suites.
- [x] Extend the paired evaluator to require exactly 24 pairs / 48 games for this confirmatory mode.
- [x] Correct the one-sided 90% paired Student-t lower-bound calculation; add reference-value and edge-case tests.
- [x] Make the 50-simulation, no-noise, zero-temperature, 200-ply configuration explicit in CLI/workflow inputs and report metadata.
- [x] Preserve per-game PGNs, UCI moves, opening FENs, termination reasons and checkpoint/suite hashes.
- [x] Add tests that illegal moves abort evaluation and prevent promotion; incomplete game pairs cannot be counted.
- [x] Ensure the workflow is read-only: download and hash-check checkpoints, run inference-only games, upload reports; no optimizer, training, checkpoint overwrite, release publication or promotion action.
- [x] Run required CPU and Stockfish checks on the implementation PR (PR #45; both required checks succeeded).
- [x] Merge the implementation and complete the manually dispatched, explicitly confirmed v1 evaluation (PR #45; workflow 43755129081).

## 8. Current decision

The epoch-0 checkpoint remains the incumbent. The epoch-10 checkpoint remains an unpromoted candidate. Confirmatory v1 completed on 2026-11-15 and passed its numerical score and paired-LCB thresholds (55.21%; LCB 50.78%). Because the lower-bound margin is narrow and the suite is curated, do not promote on v1 alone. Run the separately frozen independent_v2 suite before a promotion decision. No training or checkpoint mutation is authorised by either evaluation.

## 9. Confirmatory v1 execution record

Workflow [43755129081](https://github.com/Nomusa990822/AlphaZero-Style-Chess-AI-Self-Play-Reinforcement-Learning-with-MCTS-and-Policy-Value-Networks/actions/runs/43755129081) completed 24 opening pairs / 48 games on source commit `727639e75b7defcad5a915473258b1f13bf94389`. The candidate scored 7 wins, 39 draws and 2 losses (55.21%). Mean paired score was 0.5520833333, paired sample standard deviation 0.1645013325, and one-sided 90% Student-t lower bound 0.5077775899. Candidate-as-White: 4 wins, 20 draws, 0 losses (58.33%); candidate-as-Black: 3 wins, 19 draws, 2 losses (52.08%). All 48 games ended under chess rules; no move-cap draws. Both pinned checkpoint SHA-256 values were verified. Report artifact [14179310181](https://github.com/Nomusa990822/AlphaZero-Style-Chess-AI-Self-Play-Reinforcement-Learning-with-MCTS-and-Policy-Value-Networks/actions/runs/43755129081/artifacts/14179310181); suite SHA-256 `896c7a09997b18d848f1e4452da75dec151c3a4960fac780ad379694859813ca`.

The numerical gate passed, but this is not an Elo estimate, external-strength measurement, or value-calibration study. The lower bound exceeded 0.50 by only about 0.78 percentage points. Keep the candidate unpromoted pending independent_v2 confirmation and human review.

## 10. Independent confirmatory v2

A second frozen 24-position suite, `benchmarks/evaluation_openings_independent_v2.jsonl`, has been added with version `independent_v2` and SHA-256 `69d2582e175bf0a4bfd2867537ea7de4e43f0cfe0a2dfdc5ca6f6d5e0c2fff03`. It is intended to be disjoint from the development suite, tactical corpus, and confirmatory_v1. The loader enforces this disjointness. The dedicated manual workflow `.github/workflows/independent-confirmation-v2.yml` reuses the exact checkpoint hashes and v1 match settings, changing only the frozen opening suite. PR #46 merged at `cbf96a41089efbbb2f23a51d1b1c12a05e72657d`. The CPU suite passed 221 tests in workflow [43759061879](${repoUrl}/actions/runs/43759061879). Stockfish audit [43759061894](${repoUrl}/actions/runs/43759061894) supported 35/35 positions and 11/11 sequences with zero flagged entries. The workflow pins suite SHA-256 `69d2582e175bf0a4bfd2867537ea7de4e43f0cfe0a2dfdc5ca6f6d5e0c2fff03`, seeds Python/NumPy/PyTorch with `20261116`, and is ready for manual dispatch from `main`; the v2 match itself has not run. The two suite results must be considered separately, not pooled post hoc into a larger sample.
