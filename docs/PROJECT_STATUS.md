# Project Status

**Project:** AlphaZero-Style Chess AI  
**Status:** Active research and engineering  
**Tracking branch:** `chess-strength-training-upgrade`  
**Base branch:** `main`  
**Latest verified code revision:** `bf2ceebe4fe5738c4dc94ea44cf3f06185ad0e9a` (153 CPU tests passed in 2.78 seconds; CPU run 43421598036; batched benchmark completed and artifact 14033619165 uploaded; Stockfish audit run 43421598059 passed, with duplicate audit 43421606287 also passed).
**Current state:** checkpoint recovery/manifest tooling, the resource-bounded MCTS configuration benchmark, its mocked execution-path/report tests, the bounded forced-mate-in-two root safeguard, and the bounded static exchange evaluator, and its conservative root-prior integration are CI-verified. PUCT parsing rejects non-finite values. No compatible trained checkpoint is currently available, so no real-checkpoint ablation or search-sweep experiment has been run. Training remains manual-only and has not been started. The current branch caches root tactical analysis to avoid repeating costly legal-move scans across search, action selection and policy-target generation; this change is CI-verified.
**Pull request:** [#1 — Harden chess search, self-play and model evaluation](https://github.com/Nomusa990822/AlphaZero-Style-Chess-AI-Self-Play-Reinforcement-Learning-with-MCTS-and-Policy-Value-Networks/pull/1) (draft; not merged)

> This file is the current snapshot. The chronological engineering record is in [DEVELOPMENT_LOG.md](DEVELOPMENT_LOG.md), and measured training/benchmark results belong in [EXPERIMENT_LOG.md](EXPERIMENT_LOG.md).

- Checkpoint durability: `.pt` files remain excluded from Git. The manual workflow requires explicit `YES`, uploads produced checkpoints as a 90-day Actions artifact even after a failed training run, and on successful training publishes a durable GitHub prerelease asset with a SHA-256 manifest. Download release assets to independent storage; neither GitHub backup is a substitute for a second copy. Workflow implementation CI passed on commit `822b2213d5931499853c1c67391e8d8243140ab5`: CPU run [43409861234](https://github.com/Nomusa990822/AlphaZero-Style-Chess-AI-Self-Play-Reinforcement-Learning-with-MCTS-and-Policy-Value-Networks/actions/runs/43409861234) reported 120 passed; Stockfish audit [43409861252](https://github.com/Nomusa990822/AlphaZero-Style-Chess-AI-Self-Play-Reinforcement-Learning-with-MCTS-and-Policy-Networks/actions/runs/43409861252) passed.
- The repository does not contain a committed model checkpoint. A compatible locally generated checkpoint is required for the paired ablation experiment; do not report a random/untrained model score as learned playing strength.

- Tactical-root-filter ablation is **CI-verified** on `96303e4d5f4f0c39c4abd7252c97bb3e9c0c0d86`. CPU workflow [43407430846](https://github.com/Nomusa990822/AlphaZero-Style-Chess-AI-Self-Play-Reinforcement-Learning-with-MCTS-and-Policy-Value-Networks/actions/runs/43407430846) passed; Stockfish audit [43407430853](https://github.com/Nomusa990822/AlphaZero-Style-Chess-AI-Self-Play-Reinforcement-Learning-with-MCTS-and-Policy-Value-Networks/actions/runs/43407430853) passed and uploaded its report. The earlier paired ablation change also passed 116 CPU tests in run [43407151824](https://github.com/Nomusa990822/AlphaZero-Style-Chess-AI-Self-Play-Reinforcement-Learning-with-MCTS-and-Policy-Networks/actions/runs/43407151824). The paired comparison runner is CI-verified; no real-checkpoint experiment or playing-strength claim has been made.

- New test-only revision `187ad05954a70f28c7c3576f4d70139f4c1dbdc5` adds Black mate-in-one simulation coverage and verifies that forced-loss positions retain every legal root move. Both workflows passed on the final CI branch head: CPU tests [43406633328](https://github.com/Nomusa990822/AlphaZero-Style-Chess-AI-Self-Play-Reinforcement-Learning-with-MCTS-and-Policy-Value-Networks/actions/runs/43406633328) reported **115 passed in 3.52 seconds**; Stockfish tactical audit [43406633323](https://github.com/Nomusa990822/AlphaZero-Style-Chess-AI-Self-Play-Reinforcement-Learning-with-MCTS-and-Policy-Value-Networks/actions/runs/43406633323) completed review and artifact upload successfully.

- Latest search-efficiency change: **verified by CI** on code revision `7f39e43b0b0174b730f3facf194d68577c6d3a10`. Root MCTS selection computes one candidate set before simulations: it prioritises all legal mate-in-one moves, otherwise excludes moves allowing an immediate opponent mate when safe alternatives exist. Forced-loss fallback is preserved, and deeper-tree selection remains unrestricted. The CPU suite passed **113 tests** in run [43406066354](https://github.com/Nomusa990822/AlphaZero-Style-Chess-AI-Self-Play-Reinforcement-Learning-with-MCTS-and-Policy-Value-Networks/actions/runs/43406066354). The Stockfish tactical audit workflow also passed in run [43406066235](https://github.com/Nomusa990822/AlphaZero-Style-Chess-AI-Self-Play-Reinforcement-Learning-with-MCTS-and-Policy-Value-Networks/actions/runs/43406066235), uploading artifact `tactical-engine-audit` (ID `14026509085`).

- Both follow-up workflows passed on branch head `592671dc283ab86d0dc52a285c74da8204f0fc3b`: CPU tests run [43404899202](https://github.com/Nomusa990822/AlphaZero-Style-Chess-AI-Self-Play-Reinforcement-Learning-with-MCTS-and-Policy-Value-Networks/actions/runs/43404899202), and Stockfish tactical audit run [43404899148](https://github.com/Nomusa990822/AlphaZero-Style-Chess-AI-Self-Play-Reinforcement-Learning-with-MCTS-and-Policy-Value-Networks/actions/runs/43404899148). The fork-coordinate failure and its repair are retained in the chronological log.

- **Latest semantic-test CI failure and repair:** run [43404336724](https://github.com/Nomusa990822/AlphaZero-Style-Chess-AI-Self-Play-Reinforcement-Learning-with-MCTS-and-Policy-Value-Networks/actions/runs/43404336724) failed because the fork test expected the black king on e8 rather than f8. The test coordinate was corrected, and the repaired revision `592671dc283ab86d0dc52a285c74da8204f0fc3b` passed the CPU test workflow [43404899202](https://github.com/Nomusa990822/AlphaZero-Style-Chess-AI-Self-Play-Reinforcement-Learning-with-MCTS-and-Policy-Value-Networks/actions/runs/43404899202) and the Stockfish audit workflow [43404899148](https://github.com/Nomusa990822/AlphaZero-Style-Chess-AI-Self-Play-Reinforcement-Learning-with-MCTS-and-Policy-Value-Networks/actions/runs/43404899148). The original failure remains preserved in `DEVELOPMENT_LOG.md`.

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
- Bounded static-exchange scores adjust root priors for captures/promotions using a conservative multiplier; verified on `4fabc4562de186955f909059997ac23b15a0493e`.
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

- Resource-bounded search sweep: `benchmark_search_configs.py` compares simulation budgets, PUCT constants and filter modes under a preflight total-simulation cap. **CI-verified** on `040877a1ab822e7023a68b8f025eb17535eac073`: CPU workflow [43411211787](https://github.com/Nomusa990822/AlphaZero-Style-Chess-AI-Self-Play-Reinforcement-Learning-with-MCTS-and-Policy-Value-Networks/actions/runs/43411211787) passed **135 tests in 3.58 seconds**; Stockfish audit [43411211867](https://github.com/Nomusa990822/AlphaZero-Style-Chess-AI-Self-Play-Reinforcement-Learning-with-MCTS-and-Policy-Value-Networks/actions/runs/43411211867) passed and uploaded artifact `14029253397`. The actual sweep remains **not run** because no compatible checkpoint is available.

## Prioritised next work

1. Run `compare_tactical_filters.py` against a real compatible trained checkpoint using identical corpus, device and simulation budget; record the JSON report and checkpoint hash. The runner and tests have already passed CI.
2. Run the resource-bounded search sweep against a real compatible checkpoint after preserving an independent backup; inspect per-position changes before drawing conclusions.
3. Expand the tactical corpus with independently checked positions across defensive resources, discovered attacks, and endgame tactics.
4. Establish repeatable playing-strength evaluation: fixed opponents, colour-swapped pairs, sufficient games, openings/starting positions, time or node controls, and uncertainty reporting.
5. Improve search quality and efficiency only with tests and measured comparisons; avoid hard-coded piece-specific move tricks.
6. Keep this status file, development log and experiment log updated in the same change as each meaningful implementation batch. Record every CI run (including failures), the exact failing test/reason, repair revision and the first successful verification run; do not overwrite failures with later passes.

## Update protocol

For every meaningful development batch:
1. Record the date, goal, files/components affected and design decision in `DEVELOPMENT_LOG.md`.
2. Record test command/workflow, exact commit, and pass/fail outcome. Distinguish local tests, CI tests, and benchmark measurements.
3. Add training or benchmark measurements to `EXPERIMENT_LOG.md` only when an actual run produced them.
4. Update this file's verified revision, current state, limitations and next priorities.
5. Never replace missing data with estimates. Use **not run**, **not recorded**, or **pending** explicitly.


- **Current unverified benchmark-test expansion:** \`benchmark_search_configs.py\` now exposes a testable orchestration function; mocked tests exercise all eight default grid combinations, single network construction, deterministic settings, report persistence and checkpoint hashing. Additional tests check preflight budget rejection and missing-checkpoint ordering. PUCT values now reject NaN and infinity. CI is pending; do not treat these tests as passed until the current revision's workflow completes.


- **Benchmark orchestration test verification:** revision \`0f12e052434a66f03499bd1f91abafa1afeeb2fa\` passed CPU workflow [43412113192](https://github.com/Nomusa990822/AlphaZero-Style-Chess-AI-Self-Play-Reinforcement-Learning-with-MCTS-and-Policy-Value-Networks/actions/runs/43412113192): **142 tests passed in 3.20 seconds**. Stockfish audit [43412113210](https://github.com/Nomusa990822/AlphaZero-Style-Chess-AI-Self-Play-Reinforcement-Learning-with-MCTS-and-Policy-Value-Networks/actions/runs/43412113210) passed and uploaded artifact \`14030281382\`. Mocked tests cover all eight default grid configurations, shared network construction, deterministic search, checkpoint metadata/hash, JSON report persistence, budget preflight and missing-checkpoint ordering. No actual checkpoint search or training run was performed.


## Unverified work in progress — bounded mate-in-two detection
- Added an exact all-opponent-replies check for root moves that force a mate-in-one on the following turn, with a 512-reply global inspection budget. An interrupted candidate is never reported as proven.
- The new safeguard is wired into root candidate selection after immediate mate-in-one detection. Existing MCTS/PUCT and neural evaluation remain intact.
- CPU CI and Stockfish audit are pending for this branch update. Until they pass, this is unverified and must not be described as a demonstrated strength improvement.
- The bound can miss forced mates in high-branching positions; actual runtime overhead has not yet been measured.


### Verification failure and repair — bounded mate-in-two batch
- CPU runs 43414004807 and 43414014065 failed during collection due to literal newline escape sequences in the tactics import in src/mcts/search.py. Twelve test modules failed to import; no assertions ran.
- The import formatting has been corrected in the current unverified repair. Awaiting fresh CPU tests and tactical audit; the previous failures remain part of the history.


### Repair follow-up
- Initial repair attempt 96a1d06e6cec6f93b2d1997cde0d5ff4b995b0d6 retained literal newline escapes in the import. Source inspection caught this before verification.
- Corrected the import to actual line breaks in the current unverified revision. Await fresh CI.


## Verification update — 2026-11-13 (supersedes the pending state below)
- Latest source repair: `ba247182a03ce116e0e038679f62d15deabb5cab`; it replaces literal escaped newline sequences in the forced-mate root-filter block in `src/mcts/search.py` with real line breaks. **Verification pending.**
- Previous revision `fff08dcc147e5275914816244b7d09d8ac15b7ae`: CPU run [43415963144](https://github.com/Nomusa990822/AlphaZero-Style-Chess-AI-Self-Play-Reinforcement-Learning-with-MCTS-and-Policy-Value-Networks/actions/runs/43415963144) failed during collection at line 205 of `src/mcts/search.py`; twelve modules failed to import and no assertions ran. Stockfish audit [43415963147](https://github.com/Nomusa990822/AlphaZero-Style-Chess-AI-Self-Play-Reinforcement-Learning-with-MCTS-and-Policy-Value-Networks/actions/runs/43415963147) passed and uploaded artifact `14031965643`.
- The latest verified code revision remains `0f12e052434a66f03499bd1f91abafa1afeeb2fa` until both workflows pass on the repaired revision. No checkpoint training, benchmark or playing-strength experiment has been run.


- **Bounded forced mate-in-two safeguard — CI-verified:** final branch revision `065d9165df3e0c40873ddd6e8c9f551f48d8182c`. CPU workflow [43416399616](https://github.com/Nomusa990822/AlphaZero-Style-Chess-AI-Self-Play-Reinforcement-Learning-with-MCTS-and-Policy-Value-Networks/actions/runs/43416399616) passed **144 tests in 3.34 seconds**. Stockfish audit [43416399760](https://github.com/Nomusa990822/AlphaZero-Style-Chess-AI-Self-Play-Reinforcement-Learning-with-MCTS-and-Policy-Value-Networks/actions/runs/43416399760) passed: **13/13** corpus positions supported, **0** flagged; artifact ID `14031444001` uploaded. Runs [43416353605](https://github.com/Nomusa990822/AlphaZero-Style-Chess-AI-Self-Play-Reinforcement-Learning-with-MCTS-and-Policy-Value-Networks/actions/runs/43416353605) and [43416353083](https://github.com/Nomusa990822/AlphaZero-Style-Chess-AI-Self-Play-Reinforcement-Learning-with-MCTS-and-Policy-Value-Networks/actions/runs/43416353083) were cancelled after a newer tracking commit superseded them; the final workflows on the updated branch head passed. The historical failures remain documented in the development log.
- The bounded detector is an exact but budget-limited root tactic check, not a full tactical engine. It may miss a forced mate when its 512-reply inspection budget is exhausted. No real-checkpoint strength experiment or Elo result has been produced.


## Verified search-efficiency improvement — cached root tactical analysis

- The MCTS root tactical candidate set and immediate-mate result are now cached against the root node plus its FEN and move history.
- run, select_action and get_action_probs reuse the same result instead of repeating the bounded mate-in-two and mate-avoidance scans.
- Added a regression test that counts detector calls and verifies each is run only once across candidate lookup, action selection and policy-target generation.
- This is a search-overhead reduction only. It does not change tactical coverage or establish a playing-strength improvement.
- CPU workflow [43417951501](https://github.com/Nomusa990822/AlphaZero-Style-Chess-AI-Self-Play-Reinforcement-Learning-with-MCTS-and-Policy-Value-Networks/actions/runs/43417951501): **passed; 145 tests passed in 3.35 seconds** on Python 3.11.
- Stockfish audit [43417951289](https://github.com/Nomusa990822/AlphaZero-Style-Chess-AI-Self-Play-Reinforcement-Learning-with-MCTS-and-Policy-Value-Networks/actions/runs/43417951289): **passed**; 13/13 corpus positions supported, 0 flagged for human review; artifact ID 14032288263.


## Current batch — static exchange evaluation (verification pending)

- Added a bounded legal-recapture exchange evaluator in src/mcts/tactics.py.
- It evaluates captures, en-passant and promotions on the move's destination square, allowing either side to stop the exchange.
- Legal recaptures are enumerated through python-chess, excluding pinned pieces and illegal king captures.
- A finite capture-node budget returns None when the result is incomplete; unknown is not silently treated as a favourable exchange.
- Added tests for an undefended queen capture, a poisoned rook capture, en-passant, promotion, invalid moves and invalid budgets.
- This is a tactical evaluation primitive; it is not yet used to prune or bias MCTS moves. No playing-strength gain is claimed.
- CPU workflow [43418653846](https://github.com/Nomusa990822/AlphaZero-Style-Chess-AI-Self-Play-Reinforcement-Learning-with-MCTS-and-Policy-Value-Networks/actions/runs/43418653846): **passed; 149 tests passed in 3.82 seconds** on Python 3.11.
- Stockfish audit [43418653867](https://github.com/Nomusa990822/AlphaZero-Style-Chess-AI-Self-Play-Reinforcement-Learning-with-MCTS-and-Policy-Networks/actions/runs/43418653867): **passed**; 13/13 tactical corpus positions supported, 0 flagged for human review; artifact ID 14032962642.


## Verified — SEE-guided root prior adjustment

- Integrated bounded static exchange evaluation into root expansion as a modest policy-prior adjustment for captures and promotions.
- The neural policy remains the base prior; the SEE multiplier is capped at exp(+/-0.5), then priors are renormalised.
- No move is removed. Unknown SEE results (budget exhaustion) leave the neural prior unchanged.
- Added regression coverage for favourable captures by White and Black, poisoned-capture de-prioritisation, legal-move preservation, prior normalisation and unknown-result fallback.
- This changes root exploration priorities only; no deeper-node SEE calculation, checkpoint experiment, runtime benchmark, playing-strength gain or Elo result is claimed.
- CPU workflow [43419431349](https://github.com/Nomusa990822/AlphaZero-Style-Chess-AI-Self-Play-Reinforcement-Learning-with-MCTS-and-Policy-Value-Networks/actions/runs/43419431349): **passed; 152 tests passed in 2.56 seconds** on Python 3.11.
- Stockfish tactical audit [43419439546](https://github.com/Nomusa990822/AlphaZero-Style-Chess-AI-Self-Play-Reinforcement-Learning-with-MCTS-and-Policy-Value-Networks/actions/runs/43419439546): **passed**; 13/13 corpus positions supported, 0 flagged for human review; artifact ID `14033895065`.
- Duplicate CPU run [43419439368](https://github.com/Nomusa990822/AlphaZero-Style-Chess-AI-Self-Play-Reinforcement-Learning-with-MCTS-and-Policy-Value-Networks/actions/runs/43419439368) also passed. An earlier duplicate audit run [43419431278](https://github.com/Nomusa990822/AlphaZero-Style-Chess-AI-Self-Play-Reinforcement-Learning-with-MCTS-and-Policy-Value-Networks/actions/runs/43419431278) remained in progress when checked; the successful audit run above completed the same code SHA.
- The integration is CI-verified. No checkpoint experiment, training run, runtime comparison, measured playing-strength gain or Elo result is claimed.


## Verified — SEE root-expansion overhead benchmark

- Added a deterministic CPU microbenchmark comparing root expansion with SEE ordering disabled and enabled across the starting position, simple capture, poisoned queen capture and promotion positions.
- Uses uniform synthetic inference to isolate policy conversion, SEE adjustment and child expansion; neural inference, simulations and tactical root filters are excluded.
- Paired measurements alternate order, include warmups, and report per-position plus aggregate median/p95 latency and overhead percentage.
- The CPU workflow now runs the benchmark and uploads `see-root-overhead-benchmark` as an artifact.
- This is not an end-to-end engine speed or playing-strength measurement. No trained checkpoint is required or used.
- Verified revision: `816c4593a7a8ab158dcbe246ed32a388c736b206`.
- CPU workflow [43420960017](https://github.com/Nomusa990822/AlphaZero-Style-Chess-AI-Self-Play-Reinforcement-Learning-with-MCTS-and-Policy-Value-Networks/actions/runs/43420960017): 153 tests passed in 3.53 seconds; benchmark step and artifact upload succeeded.
- Aggregate microbenchmark: SEE disabled median 0.150311 ms, enabled median 0.245393 ms, nominal +63.26%; pooled p95 0.268644 ms disabled and 0.365839 ms enabled. Artifact ID `14033642158`.
- These sub-millisecond measurements are runner-specific and likely sensitive to timer/scheduler noise; the percentage is preliminary, not an end-to-end speed penalty. A batched timing pass now exists; its first results are recorded below but still require interpretation as synthetic root-expansion microbenchmarks.
- Stockfish audit [43420959887](https://github.com/Nomusa990822/AlphaZero-Style-Chess-AI-Self-Play-Reinforcement-Learning-with-MCTS-and-Policy-Value-Networks/actions/runs/43420959887) passed; 13/13 positions supported, 0 flagged for human review; artifact ID `14033706954`.


### Benchmark invocation repair — 2026-11-13
- First run on `58f460d443fc5619ba4240af43a3c0d21b80cf37` passed all 153 pytest tests but the benchmark step failed because direct script execution placed `scripts/`, not the repository root, on Python's import path (`ModuleNotFoundError: src`). The artifact upload was consequently skipped.
- Updated the workflow to invoke the script as a module (`python -m scripts.benchmark_see_overhead`), which keeps the repository root on the import path. Fresh CPU CI and benchmark artifact are required.


### CI history and benchmark measurement interpretation

- The first benchmark launch failed on `58f460d443fc5619ba4240af43a3c0d21b80cf37` because direct script invocation could not import `src`. Both CPU runs `43420810604` and `43420817142` failed at the benchmark step after their test suites passed. The audit runs on that revision passed.
- The workflow repair uses module invocation. On `816c4593a7a8ab158dcbe246ed32a388c736b206`, CPU run `43420960017` passed (153 tests in 3.53 seconds) and uploaded the benchmark artifact; Stockfish audit `43420959887` passed. Duplicate runs `43420967360` and `43420967336` also passed.
- Initial aggregate measurements: disabled median 0.150311 ms, enabled median 0.245393 ms (+63.26% nominal); p95 0.268644 ms disabled and 0.365839 ms enabled.
- Because individual root expansions take only fractions of a millisecond, these measurements are sensitive to scheduling/timer noise. Treat the percentage as preliminary; batch multiple expansions per timed sample before using it to tune the default.


### In progress — Batched SEE overhead benchmark
- The individual-expansion benchmark's sub-millisecond timings were too noise-sensitive for tuning decisions. The new implementation times batches of ten independently prepared root expansions, with 25 paired batches per position/mode and three warmups.
- The timed region excludes setup and normalizes batch elapsed time per expansion. It continues to check legal-move preservation, prior normalization and board immutability.
- The benchmark, its test and the CPU workflow update are awaiting CI on the new revision. No default setting has been changed pending more reliable measurements.


### Verified — Batched SEE root-expansion overhead benchmark
- Implementation revision: `bf2ceebe4fe5738c4dc94ea44cf3f06185ad0e9a`.
- CPU workflow [43421598036](https://github.com/Nomusa990822/AlphaZero-Style-Chess-AI-Self-Play-Reinforcement-Learning-with-MCTS-and-Policy-Value-Networks/actions/runs/43421598036): **153 tests passed in 2.78 seconds**; batched benchmark completed and artifact `see-root-overhead-benchmark` uploaded (ID `14033619165`).
- Stockfish audit [43421598059](https://github.com/Nomusa990822/AlphaZero-Style-Chess-AI-Self-Play-Reinforcement-Learning-with-MCTS-and-Policy-Networks/actions/runs/43421598059): passed. Duplicate audit [43421606287](https://github.com/Nomusa990822/AlphaZero-Style-Chess-AI-Self-Play-Reinforcement-Learning-with-MCTS-and-Policy-Networks/actions/runs/43421606287) also passed.
- Each sample times ten prepared root expansions; 25 batches per position/mode; 1,000 timed expansions per mode across four positions.
- Aggregate median: SEE disabled **0.158494 ms/expansion**; enabled **0.267257 ms/expansion**; nominal overhead **68.62%**. Pooled p95: **0.321696 ms** disabled and **0.414722 ms** enabled.
- Per-position nominal median overhead: starting position 10.19% (no SEE candidates), simple capture 27.80%, poisoned queen capture 50.10%, promotion choices 68.04%.
- Batching provides longer timed intervals and a more informative comparison than the first single-expansion pass, but these remain runner-specific synthetic measurements. The starting-position overhead with no SEE candidates indicates a fixed integration/path cost, while the larger tactical-position costs reflect additional SEE work. Do not interpret the percentages as an end-to-end slowdown; model inference and simulations are excluded.
- The first single-expansion measurements remain preserved above as preliminary data. No default was changed; no real checkpoint, training, playing-strength or Elo result is claimed.
