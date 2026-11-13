# Project Status

**Project:** AlphaZero-Style Chess AI  
**Status:** Active research and engineering  
**Tracking branch:** `chess-strength-training-upgrade`  
**Base branch:** `main`  
************Latest verified code revision:** `36ad6dd4ddcd06d7215b4abd99aa7d21d183201d` (170 CPU tests passed; CPU run 43437925480; Stockfish review 22/22 positions and 5/5 sequences / 19/19 plies supported, 0 flagged; run 43437925723).n 43437583240; Stockfish review 22/22 positions and 3/3 sequences / 11/11 plies supported, 0 flagged; run 43437583217).n 43437190901; Stockfish review 22/22 positions, 2/2 sequences and 6/6 plies supported, 0 flagged; run 43437190817).n 43436850141; Stockfish review 21/21 positions, 2/2 sequences and 6/6 plies supported, 0 flagged; run 43436850163).n 43435423576; Stockfish tactical review 19/19 positions and 2/2 sequences / 6/6 plies supported, 0 flagged; run 43435423818).n 2.78 seconds; CPU run 43421598036; batched benchmark completed and artifact 14033619165 uploaded; Stockfish audit run 43421598059 passed, with duplicate audit 43421606287 also passed).
**Current state:** checkpoint recovery/manifest tooling, the resource-bounded MCTS configuration benchmark, its mocked execution-path/report tests, the bounded forced-mate-in-two root safeguard, the bounded static exchange evaluator and conservative root-prior integration, and the expanded 22-position tactical corpus with three annotated combinations are CI-verified. PUCT parsing rejects non-finite values. No compatible trained checkpoint is currently available, so no real-checkpoint ablation or search-sweep experiment has been run. Training remains manual-only and has not been started. The current branch caches root tactical analysis to avoid repeating costly legal-move scans across search, action selection and policy-target generation; this change is CI-verified.
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


### In progress — SEE quiet-position fast path
- The root SEE prior adjustment now returns existing normalized priors immediately when the position contains no captures or promotions. This avoids copying and renormalizing the dictionary in quiet positions.
- A regression test verifies that the no-candidate path never calls SEE and preserves the original prior object/distribution.
- CPU tests, the batched benchmark and Stockfish audit are pending on the new implementation revision. Tactical positions continue through the existing bounded SEE scoring path.


### Verified — SEE quiet-position fast path
- Latest verified implementation revision: `8124b000aef61645b57fd3f686ef81a13174530d`.
- CPU tests: **154 passed** on runs `43423373600` (3.72 sec) and `43423379443` (3.22 sec). The benchmark artifact uploaded in both runs (`14034344758`, `14034629057`).
- Stockfish audit passed on runs `43423379514` and `43423373448`.
- Quiet positions with no captures/promotions now bypass SEE scoring, prior dictionary copying and renormalization. The tactical-candidate path is unchanged.
- Benchmark timing was affected by concurrent runner activity; the new measurements do not establish a reliable performance gain. Keep SEE enabled/disabled defaults unchanged pending isolated profiling.


### In progress — CI concurrency deduplication
- CPU-test and Stockfish-audit workflows now share concurrency groups between push and pull-request events for the same source branch, preventing duplicate simultaneous runs and reducing runner contention.
- This should make the benchmark environment less noisy and avoid unnecessary CI usage. The workflow configuration awaits Actions verification.


## Latest verified branch state — 2026-11-13

- Branch head: `223b2423eb8980c9d5d080384685cceaf395d735` (CI concurrency deduplication; no chess search code changed).
- Latest verified search implementation: `8124b000aef61645b57fd3f686ef81a13174530d`; the quiet-position SEE fast path remains in place.
- CPU workflow [43423663811](https://github.com/Nomusa990822/AlphaZero-Style-Chess-AI-Self-Play-Reinforcement-Learning-with-MCTS-and-Policy-Value-Networks/actions/runs/43423663811): **154 passed in 3.87 seconds**; SEE benchmark completed and artifact ID `14035332107` uploaded.
- Stockfish audit [43423663646](https://github.com/Nomusa990822/AlphaZero-Style-Chess-AI-Self-Play-Reinforcement-Learning-with-MCTS-and-Policy-Value-Networks/actions/runs/43423663646): **13/13 positions supported, 0 flagged**, artifact ID `14035351972`.
- CI deduplication verified: duplicate push runs [43423653700](https://github.com/Nomusa990822/AlphaZero-Style-Chess-AI-Self-Play-Reinforcement-Learning-with-MCTS-and-Policy-Value-Networks/actions/runs/43423653700) and [43423653471](https://github.com/Nomusa990822/AlphaZero-Style-Chess-AI-Self-Play-Reinforcement-Learning-with-MCTS-and-Policy-Value-Networks/actions/runs/43423653471) were cancelled in favour of the matching pull-request runs. This is expected concurrency behaviour, not a failed check.
- Latest isolated-run SEE benchmark medians: starting position 0.395490 ms disabled / 0.422475 ms enabled (+6.82%); simple capture +28.76%; poisoned queen capture +48.78%; promotion +70.50%; aggregate +67.29%. These remain synthetic microbenchmark results, not full-search speed or playing strength. Keep the current SEE configuration unchanged.
- No compatible trained checkpoint is available in the repository; no new training or checkpoint evaluation has occurred. No Elo or neural playing-strength claim is established.

### Next work
- Prioritise correctness/strength evaluation infrastructure and search improvements that can be validated without training or paid compute.
- Preserve the existing experiment protocol. Do not run training or claim strength gains until a compatible checkpoint exists and paired evaluation has actually completed.
- Avoid redundant CI-triggering documentation commits; bundle tracking updates with the next implementation batch.


## Latest verified baseline and current unverified change — 2026-11-13

- Documentation/CI baseline: `b06b5df954156620e9824c89cce3b152d8308a31`. CPU workflow [43423960670](https://github.com/Nomusa990822/AlphaZero-Style-Chess-AI-Self-Play-Reinforcement-Learning-with-MCTS-and-Policy-Value-Networks/actions/runs/43423960670): **154 passed in 2.74 seconds**; SEE benchmark artifact ID `14035481672`. Stockfish audit [43423960833](https://github.com/Nomusa990822/AlphaZero-Style-Chess-AI-Self-Play-Reinforcement-Learning-with-MCTS-and-Policy-Value-Networks/actions/runs/43423960833) passed.
- The shared branch concurrency groups were verified again: push runs [43423953162](https://github.com/Nomusa990822/AlphaZero-Style-Chess-AI-Self-Play-Reinforcement-Learning-with-MCTS-and-Policy-Value-Networks/actions/runs/43423953162) and [43423953259](https://github.com/Nomusa990822/AlphaZero-Style-Chess-AI-Self-Play-Reinforcement-Learning-with-MCTS-and-Policy-Value-Networks/actions/runs/43423953259) were cancelled as duplicates, while the PR runs completed successfully.
- Current unverified implementation: tactical-root cache key now includes `use_tactical_root_filter`, preventing stale eligible moves and stale mate-in-one overrides when the mutable setting changes on a reused MCTS object.
- A regression test covers enabled → disabled → enabled transitions on the same root node.
- **Verification pending** on the new code revision. The latest verified baseline remains `b06b5df954156620e9824c89cce3b152d8308a31` until its CPU and Stockfish workflows finish successfully.
- No training, checkpoint evaluation, playing-strength result or Elo claim was produced.



## Verified baseline and current change — 2026-11-13

- Latest verified code revision: `1c2d4e472496c3080fd7df9e188bfa504b635d49`.
- CPU workflow [43424484996](https://github.com/Nomusa990822/AlphaZero-Style-Chess-AI-Self-Play-Reinforcement-Learning-with-MCTS-and-Policy-Value-Networks/actions/runs/43424484996): **155 tests passed in 4.98 seconds**; SEE benchmark artifact ID `14036345110`. Aggregate synthetic root-expansion median overhead was **+63.65%** (0.297020 ms disabled / 0.486085 ms enabled); this is not an end-to-end speed or strength result.
- Stockfish audit [43424485735](https://github.com/Nomusa990822/AlphaZero-Style-Chess-AI-Self-Play-Reinforcement-Learning-with-MCTS-and-Policy-Value-Networks/actions/runs/43424485735): **13/13 positions supported, 0 flagged**, artifact ID `14036055893`.
- Current unverified change: align immediate-mate action sampling with its self-play policy target. Positive temperature samples uniformly among all mate-in-one moves; zero temperature chooses the first and emits a matching one-hot target.
- Added regression coverage for both temperature modes. **Verification pending** on the new revision.
- No training, checkpoint evaluation, playing-strength result or Elo claim was produced.


## Tactical-combination evaluation — implementation pending CI

- The original 13 single-position tactical cases remain unchanged.
- Added a separate multi-ply combination corpus and evaluator. Initial coverage includes a checking fork followed by a queen capture and a discovered check followed by a queen capture.
- Sequence reports distinguish complete-line success from per-ply accuracy and break results down by attacking/defending side and game phase.
- Important limitation: the initial sequence metric replays an annotated principal variation. It does not establish that every opponent defence is forced or that the engine has general tactical understanding.
- Individual motif expansion beyond the original 13-position corpus remains outstanding. The new sequence evaluator and CLI are awaiting CI verification.
- No compatible checkpoint is currently available; do not run training or infer playing strength from these benchmark tests.


### Multi-ply sequence benchmark — first verification attempt
- Implementation commit `cda8fb2e4a2b0a37e4a31d7e0f68460b42fff622` CPU run [43426943254](https://github.com/Nomusa990822/AlphaZero-Style-Chess-AI-Self-Play-Reinforcement-Learning-with-MCTS-and-Policy-Value-Networks/actions/runs/43426943254): **2 failed, 158 passed**. Both failures were test-fixture expectation mistakes in the newly added sequence tests; the fixtures were corrected in `b10ce6b6faefc2a5ae6351817dc9afc639b81755`. The failed run remains recorded.
- Stockfish audit [43426943127](https://github.com/Nomusa990822/AlphaZero-Style-Chess-AI-Self-Play-Reinforcement-Learning-with-MCTS-and-Policy-Value-Networks/actions/runs/43426943127): original single-position corpus **13/13 supported, 0 flagged**, artifact `14038596188`.


### Multi-ply tactical-sequence benchmark — CI verified
- Verified revision `d1f33d1920c2cb909dbad20405a296544acf9c54`.
- CPU workflow [43427256968](https://github.com/Nomusa990822/AlphaZero-Style-Chess-AI-Self-Play-Reinforcement-Learning-with-MCTS-and-Policy-Value-Networks/actions/runs/43427256968): **160 passed in 3.30 seconds**; SEE benchmark artifact `14038486847` uploaded. Synthetic root-expansion SEE overhead was +67.96%, not an end-to-end speed or strength result.
- Stockfish audit [43427256921](https://github.com/Nomusa990822/AlphaZero-Style-Chess-AI-Self-Play-Reinforcement-Learning-with-MCTS-and-Policy-Value-Networks/actions/runs/43427256921): original single-position corpus **13/13 supported, 0 flagged**, artifact `14038297049`.
- The first CPU run's two test-fixture failures are preserved in the history and corrected in `b10ce6b6faefc2a5ae6351817dc9afc639b81755`; corrected suite passed.
- Sequence evaluation is limited to annotated principal-variation line-following. It does not yet establish forcedness against every defence. Individual motif corpus expansion and tactical-search improvements remain outstanding. No model training or checkpoint/playing-strength evaluation was run.


### Latest tactical-combination audit — CI verified
- Revision `2944ad7326880e7a020219c2652b33525df20c5a` adds Stockfish review of every annotated ply in the two sequence examples.
- CPU workflow [43427628807](https://github.com/Nomusa990822/AlphaZero-Style-Chess-AI-Self-Play-Reinforcement-Learning-with-MCTS-and-Policy-Value-Networks/actions/runs/43427628807): **161 passed in 3.99 seconds**; SEE benchmark completed. Synthetic root-expansion SEE overhead: +67.25%, not a full-search or strength result.
- Stockfish audit [43427628961](https://github.com/Nomusa990822/AlphaZero-Style-Chess-AI-Self-Play-Reinforcement-Learning-with-MCTS-and-Policy-Value-Networks/actions/runs/43427628961): original corpus **13/13 supported, 0 flagged**; combination corpus **2/2 sequences and 6/6 plies supported, 0 flagged**; artifact `14037203389`.
- The sequence audit follows the annotated principal variation and is not a proof of forcedness against all defences. Individual motif corpus expansion and direct search improvements remain outstanding. No training or checkpoint strength evaluation was run.

### Tactical corpus expansion — verification pending (2026-11-13)
- Corpus now contains one additional Black-to-move deflection candidate (15 positions total; expected colour split White 8 / Black 7).
- The semantic regression checks the bishop check on d4, queen capture on d4, and ...Qf1# continuation.
- CPU CI and Stockfish audit have not yet confirmed this addition. Until both complete, the last verified corpus remains 14/14 supported.
- Planned broader motif expansion remains in progress; do not count this single candidate as completion of the eight-position batch.


### Deflection corpus expansion — verified on corrected revision (2026-11-13)
- Verified branch revision: `7bdf9bb25b96ae003a8c3f75f5f4d67a6c97db3e`.
- CPU workflow [43429806549](https://github.com/Nomusa990822/AlphaZero-Style-Chess-AI-Self-Play-Reinforcement-Learning-with-MCTS-and-Policy-Value-Networks/actions/runs/43429806549): **163 tests passed in 4.29 seconds**; SEE microbenchmark artifact `14039481148`, aggregate synthetic root-expansion median overhead +63.24%.
- Stockfish audit [43429806151](https://github.com/Nomusa990822/AlphaZero-Style-Chess-AI-Self-Play-Reinforcement-Learning-with-MCTS-and-Policy-Value-Networks/actions/runs/43429806151): **15/15 positions supported, 0 flagged**; both tactical sequences and all six annotated plies supported, 0 flagged; artifact `14038701315`.
- The 15-position corpus now includes one additional Black-to-move deflection example (White 8 / Black 7). The one-position addition is verified; the broader eight-position expansion remains outstanding.
- Earlier cancelled runs are retained in the development history. The cancelled runs are not counted as failures.
- Stockfish finite-depth support is a review signal, not exhaustive proof of forcedness or motif-label correctness. No checkpoint evaluation or training was run; no playing-strength or Elo claim is made.


### Decoy motif expansion — verification pending (2026-11-13)
- Added one White-to-move queen-sacrifice decoy candidate: `Qxh7+`, `...Kxh7`, `Rh5#` (16 total positions; expected White 9 / Black 7).
- Added semantic checks for the king attraction and mating continuation. CPU and Stockfish verification are pending on the new revision.
- The previously verified baseline remains 15/15 positions supported on `7bdf9bb`; do not count the new decoy as verified until its own audit passes.
- No model training or checkpoint evaluation was run.


### Decoy motif corpus expansion — verified (2026-11-13)
- Verified branch revision: `6598cf5d6f393926f53b6cf4e8880bc52bf3199d`.
- CPU workflow [43431101691](https://github.com/Nomusa990822/AlphaZero-Style-Chess-AI-Self-Play-Reinforcement-Learning-with-MCTS-and-Policy-Value-Networks/actions/runs/43431101691): **164 tests passed in 4.95 seconds**.
- Stockfish audit [43431101664](https://github.com/Nomusa990822/AlphaZero-Style-Chess-AI-Self-Play-Reinforcement-Learning-with-MCTS-and-Policy-Value-Networks/actions/runs/43431101664): **16/16 individual positions supported, 0 flagged; 2/2 sequences and 6/6 annotated plies supported, 0 flagged**.
- The verified addition is one White-to-move queen decoy: `Qxh7+`, `...Kxh7`, `Rh5#`. Corpus total is 16 (White 9 / Black 7).
- Matching push runs [43431088106](https://github.com/Nomusa990822/AlphaZero-Style-Chess-AI-Self-Play-Reinforcement-Learning-with-MCTS-and-Policy-Value-Networks/actions/runs/43431088106) and [43431088153](https://github.com/Nomusa990822/AlphaZero-Style-Chess-AI-Self-Play-Reinforcement-Learning-with-MCTS-and-Policy-Value-Networks/actions/runs/43431088153) were cancelled; matching PR runs above completed successfully on the exact same commit.
- Broader eight-position expansion is still incomplete. Finite-depth Stockfish support is not proof of forcedness against every defence. No training or checkpoint evaluation was run, and no playing-strength/Elo claim is made.


### Removal-of-the-defender motif — verification pending (2026-11-13)
- Added one Black-to-move candidate: `...Rxc4+`, `Rxc4`, `...Nb5#`. The rook sacrifice removes the c4-pawn that guarded b5.
- Added the new `removal_of_defender` motif to the loader taxonomy and a semantic regression for the complete annotated mate line.
- Candidate corpus total: 17 positions (White 9 / Black 8). CPU and Stockfish checks are pending; the last verified corpus remains 16/16 on `6598cf5d6f393926f53b6cf4e8880bc52bf3199d`.
- No training or checkpoint evaluation was run.


### Removal-of-the-defender candidate — CI failure recorded (2026-11-13)
- The first candidate revision `197efeac6c4fdf929568acb12e843862544eb418` failed both CPU [43431590559](https://github.com/Nomusa990822/AlphaZero-Style-Chess-AI-Self-Play-Reinforcement-Learning-with-MCTS-and-Policy-Value-Networks/actions/runs/43431590559) and Stockfish [43431590481](https://github.com/Nomusa990822/AlphaZero-Style-Chess-AI-Self-Play-Reinforcement-Learning-with-MCTS-and-Policy-Value-Networks/actions/runs/43431590481) workflows because `e5c4` was an illegal diagonal rook move.
- Corrected both corpus and semantic test to use `c8c4`, the rook's legal capture along the c-file. Re-verification is pending; the candidate is not counted as verified.
- Failures remain documented; no training or checkpoint evaluation was run.


### Removal-of-the-defender motif — verified (2026-11-13)
- Latest verified revision before the next motif addition: `1698c10c550c3c28672d1f57cc55031306267b5f`.
- CPU [43432547200](https://github.com/Nomusa990822/AlphaZero-Style-Chess-AI-Self-Play-Reinforcement-Learning-with-MCTS-and-Policy-Value-Networks/actions/runs/43432547200): **165 passed**. Stockfish [43432547005](https://github.com/Nomusa990822/AlphaZero-Style-Chess-AI-Self-Play-Reinforcement-Learning-with-MCTS-and-Policy-Value-Networks/actions/runs/43432547005): **17/17 positions supported, 0 flagged; 2/2 sequences and 6/6 plies supported, 0 flagged**.
- The Black removal-of-the-defender example is verified on that revision. Earlier failures and cancellations remain separately recorded.


### Interference motif — candidate awaiting verification (2026-11-13)
- Added one White-to-move interference example, `Nd6-c8`, to block the queen's defensive line to the rook on a8.
- Candidate corpus total: **18 positions (White 10 / Black 8)**. CPU and Stockfish checks are pending. The last verified baseline remains 17/17 positions on `1698c10c550c3c28672d1f57cc55031306267b5f`.
- The semantic test checks that the queen's line is blocked and White's rook still attacks the target. The Stockfish audit must independently support the move before it is counted.
- No training, checkpoint evaluation, or Elo claim was made.


### Interference motif — replacement candidate awaiting verification (2026-11-13)
- Rejected the earlier `Nd6-c8` example after its CPU semantic test exposed a turn-order mistake and deeper analysis showed the advertised forcing win was not sound against all captures. The initial pair [43434069458](https://github.com/Nomusa990822/AlphaZero-Style-Chess-AI-Self-Play-Reinforcement-Learning-with-MCTS-and-Policy-Value-Networks/actions/runs/43434069458) / [43434069451](https://github.com/Nomusa990822/AlphaZero-Style-Chess-AI-Self-Play-Reinforcement-Learning-with-MCTS-and-Policy-Value-Networks/actions/runs/43434069451) was cancelled; duplicate CPU [43434076143](https://github.com/Nomusa990822/AlphaZero-Style-Chess-AI-Self-Play-Reinforcement-Learning-with-MCTS-and-Policy-Value-Networks/actions/runs/43434076143) failed (1 failed, 165 passed), while duplicate Stockfish [43434076184](https://github.com/Nomusa990822/AlphaZero-Style-Chess-AI-Self-Play-Reinforcement-Learning-with-MCTS-and-Policy-Value-Networks/actions/runs/43434076184) passed its finite-depth review (17/17 supported). Cancellations and failure remain distinct in the development log.
- Replaced the position with a published example: `1.Rd8+!`; after `...Nxd8`, `2.Qc8#`, while `...Qxd8` permits `Bxd8`. Source: Ilya Korzhenevich, *Illinois Chess Bulletin*, Sep–Oct 2005, p.22.
- New candidate corpus remains 18 positions (White 10 / Black 8). Both CPU semantics and Stockfish audit are pending; it is not counted as verified.
- No training, checkpoint evaluation, or Elo claim was made.


### Interference motif — verified replacement candidate (2026-11-13)
- Verified revision: `932d10537780a9c57c1fc38f6a234d9f59b5baf3`.
- CPU [43434909575](https://github.com/Nomusa990822/AlphaZero-Style-Chess-AI-Self-Play-Reinforcement-Learning-with-MCTS-and-Policy-Value-Networks/actions/runs/43434909575): **166 passed in 3.80 seconds**.
- Stockfish [43434909567](https://github.com/Nomusa990822/AlphaZero-Style-Chess-AI-Self-Play-Reinforcement-Learning-with-MCTS-and-Policy-Value-Networks/actions/runs/43434909567): **18/18 positions supported, 0 flagged; 2/2 sequences and 6/6 annotated plies supported, 0 flagged**; artifact `14042092553`.
- Verified interference line: `1.Rd8+!`; after `...Nxd8`, `2.Qc8#`; if `...Qxd8`, `2.Bxd8`. The rejected first candidate is excluded.
- The first workflow pair on this revision was cancelled and replaced by the successful pair above. The earlier duplicate CPU failure and Stockfish pass on the rejected candidate remain documented in the development log.
- Corpus total: **18 positions (White 10 / Black 8)**. The broader balanced eight-position motif batch is still incomplete. Finite-depth Stockfish review is not exhaustive proof of all defences. No training, checkpoint evaluation or Elo claim was made.


### Interference motif — Black-to-move example verified (2026-11-13)
- Verified revision: `87ed473223d078518ca12a75ab36a1bc4a4fc527`.
- Added the second example from Cor van Wijgerden, *Step 4*, “Elimination of the defence: interfering,” position 6: `...Rd1+`; `Rxd1 Qxb2` loses White's queen, while `Bxd1 Qe1#` is mate. Source: [Step 4 PDF](https://www.stappenmethode.nl/lesmateriaal/memos/en_gs_4.pdf), lines 91–103.
- CPU [43435423576](https://github.com/Nomusa990822/AlphaZero-Style-Chess-AI-Self-Play-Reinforcement-Learning-with-MCTS-and-Policy-Value-Networks/actions/runs/43435423576): **167 passed**. Stockfish [43435423818](https://github.com/Nomusa990822/AlphaZero-Style-Chess-AI-Self-Play-Reinforcement-Learning-with-MCTS-and-Policy-Value-Networks/actions/runs/43435423818): **19/19 positions, 0 flagged; 2/2 sequences and 6/6 plies supported, 0 flagged**; artifact `14042118119`.
- The Black interference semantic tests cover both defensive branches. The earlier cancelled workflow pair [43435412949](https://github.com/Nomusa990822/AlphaZero-Style-Chess-AI-Self-Play-Reinforcement-Learning-with-MCTS-and-Policy-Value-Networks/actions/runs/43435412949) / [43435412938](https://github.com/Nomusa990822/AlphaZero-Style-Chess-AI-Self-Play-Reinforcement-Learning-with-MCTS-and-Policy-Value-Networks/actions/runs/43435412938) remains classified as cancelled, not failed.
- Corpus total: **19 positions (White 10 / Black 9)**. The planned eight-position expansion batch remains incomplete. No training, checkpoint evaluation or Elo claim was made.


## Latest verified tactical corpus state — 2026-11-13
- Feature branch revision: `87ed473223d078518ca12a75ab36a1bc4a4fc527`.
- CPU suite: **167 passed** ([run 43435423576](https://github.com/Nomusa990822/AlphaZero-Style-Chess-AI-Self-Play-Reinforcement-Learning-with-MCTS-and-Policy-Value-Networks/actions/runs/43435423576)).
- Stockfish finite-depth review: **19/19 positions supported, 0 flagged; 2/2 sequences and 6/6 annotated plies supported, 0 flagged** ([run 43435423818](https://github.com/Nomusa990822/AlphaZero-Style-Chess-AI-Self-Play-Reinforcement-Learning-with-MCTS-and-Policy-Value-Networks/actions/runs/43435423818), artifact `14042118119`).
- Current corpus balance: **White 10 / Black 9**. The Black interference example is verified; the broader eight-position motif batch remains incomplete.
- SEE aggregate synthetic root-expansion median overhead: **+67.69%** (0.162983 ms disabled / 0.273301 ms enabled; artifact `14043771602`). This is not an end-to-end speed or playing-strength measurement.
- No compatible trained checkpoint is available in the repository. No training, checkpoint evaluation, Elo estimate or neural playing-strength claim has been produced.


### Additional balanced tactical candidates — verification pending (2026-11-13)
- Added one White deflection (`Re8+ Rxe8 Qxd7`) and one Black decoy (`Qh7+ Qh6 Qxh6+ Kxh6 Nxg4+`) with motif-specific semantic tests.
- Candidate corpus: **21 positions (White 11 / Black 10)**. CPU tests and Stockfish finite-depth review are pending; the last verified baseline remains 19 positions on `87ed473`.
- These additions bring the planned eight-position batch to seven examples; one further White removal-of-the-defender example remains to be sourced and verified.
- No training, checkpoint evaluation, or Elo claim was made.


### Tactical candidate correction — White deflection rejected (2026-11-13)
- The proposed `Re8+` deflection example was removed after Stockfish review showed the accepted move was about 452 centipawns below the engine's best choice; sacrificing a rook to collect a knight did not make a sound benchmark win.
- The Black decoy example is retained; Stockfish supported its accepted move within the configured tolerance.
- Candidate corpus is reduced to **20 positions (White 10 / Black 10)**. The rejected position and its semantic test are removed in the next correction revision. The 21-position review's single flag remains recorded in DEVELOPMENT_LOG.md.
- No training, checkpoint evaluation, or Elo claim was made.


### White removal-of-the-defender candidate — verification pending (2026-11-13)
- Added the White-to-move `Rxd4 exd4 Rxd3` example from ChessFlame/Lichess puzzle 03lR8, with a semantic test covering the removal and follow-up capture.
- Candidate corpus: **21 positions (White 11 / Black 10)**. Awaiting CPU and Stockfish checks; last verified baseline is 20/20 supported with no flags on commit `4e90222`.
- The White `Re8+` deflection proposal has been rejected and removed after the Stockfish review; do not count it. The Black decoy candidate remains supported.


### Balanced tactical corpus — latest verified state (2026-11-13)
- Verified revision: `c780bd752ea49a04aa79e869f5df7cbcb1288847`.
- CPU: **169 passed** ([43436850141](https://github.com/Nomusa990822/AlphaZero-Style-Chess-AI-Self-Play-Reinforcement-Learning-with-MCTS-and-Policy-Value-Networks/actions/runs/43436850141)).
- Stockfish: **21/21 positions supported, 0 flagged; 2/2 sequences and 6/6 annotated plies supported, 0 flagged** ([43436850163](https://github.com/Nomusa990822/AlphaZero-Style-Chess-AI-Self-Play-Reinforcement-Learning-with-MCTS-and-Policy-Value-Networks/actions/runs/43436850163), artifact `14043378711`).
- Corpus balance: **White 11 / Black 10**. The White removal-of-the-defender candidate and Black decoy are verified. The proposed White `Re8+` deflection was rejected and removed after engine review; a sound White deflection counterpart remains to be found.
- Seven additions toward the planned eight-position balanced motif batch are verified; no position is counted merely because its move is legal.
- No training, checkpoint evaluation, Elo estimate or neural playing-strength claim has been produced.


### Final planned balanced-motif candidate — verified (2026-11-13)
- Verified revision: `a7bb5785f7267f854a66eecd12e13feeb8da9d3e`.
- Added the White deflection line `Nd7+ Nxd7 Qxe4`, where the checking knight offer draws Black's f6-knight away from defending its queen on e4. Source: ChessFlame/Lichess puzzle 08lqs.
- CPU [43437190901](https://github.com/Nomusa990822/AlphaZero-Style-Chess-AI-Self-Play-Reinforcement-Learning-with-MCTS-and-Policy-Value-Networks/actions/runs/43437190901): **170 passed**. Stockfish [43437190817](https://github.com/Nomusa990822/AlphaZero-Style-Chess-AI-Self-Play-Reinforcement-Learning-with-MCTS-and-Policy-Value-Networks/actions/runs/43437190817): **22/22 positions supported, 0 flagged; 2/2 sequences and 6/6 plies supported, 0 flagged**; artifact `14044385081`.
- Corpus total: **22 positions (White 12 / Black 10)**. The eight planned motif additions are complete: two examples each of deflection, decoy, removal of defender and interference, with both colours represented. The previously proposed `Re8+` candidate was rejected and is not included.
- No training, checkpoint evaluation or Elo claim was made.


### Balanced tactical motif expansion — complete and CI-verified (2026-11-13)
- Verified revision: `a7bb5785f7267f854a66eecd12e13feeb8da9d3e`.
- CPU suite: **170 passed** ([43437190901](https://github.com/Nomusa990822/AlphaZero-Style-Chess-AI-Self-Play-Reinforcement-Learning-with-MCTS-and-Policy-Value-Networks/actions/runs/43437190901)).
- Stockfish finite-depth review: **22/22 positions supported, 0 flagged; 2/2 sequences and 6/6 annotated plies supported, 0 flagged** ([43437190817](https://github.com/Nomusa990822/AlphaZero-Style-Chess-AI-Self-Play-Reinforcement-Learning-with-MCTS-and-Policy-Value-Networks/actions/runs/43437190817), artifact `14044385081`).
- The eight planned additions are complete: two examples each of deflection, decoy, removal of defender and interference, with White and Black represented for every motif.
- Corpus total: **22 positions (White 12 / Black 10)**. The unsound proposed `Re8+` candidate was removed after engine review and is not included.
- No training, checkpoint evaluation, Elo estimate or neural playing-strength claim has been produced.


### Combined tactical sequences — third combination pending verification (2026-11-13)
- Added a Black decoy sequence combining queen attraction/exchange with a follow-up knight capture of the bishop: `...Qh7+ Qh6 Qxh6+ Kxh6 Nxg4+`.
- Sequence corpus now has three annotated combinations and eleven plies. Tests cover complete-line accounting and both colours.
- CPU and Stockfish verification are pending. Sequence scoring remains principal-variation line-following and does not prove forcedness against all replies. No training or checkpoint evaluation was run.


### Combined tactical-sequence benchmark — latest verified state (2026-11-13)
- Verified revision: `21da837e3070e9cb6e96ca383f5c963e894b9cdb`.
- CPU: **170 passed** ([43437583240](https://github.com/Nomusa990822/AlphaZero-Style-Chess-AI-Self-Play-Reinforcement-Learning-with-MCTS-and-Policy-Value-Networks/actions/runs/43437583240)).
- Stockfish audit: **22/22 positions supported, 0 flagged; 3/3 sequences and 11/11 annotated plies supported, 0 flagged** ([43437583217](https://github.com/Nomusa990822/AlphaZero-Style-Chess-AI-Self-Play-Reinforcement-Learning-with-MCTS-and-Policy-Value-Networks/actions/runs/43437583217), artifact `14044310522`).
- The sequence corpus contains three multi-motif combinations: Black checking fork/hanging queen, White discovered check/hanging queen, and Black decoy/hanging bishop. Both colours are represented across eleven annotated plies.
- Sequence scoring follows curated principal variations and does not prove forcedness against every possible defence. No training, checkpoint evaluation, Elo estimate or neural playing-strength claim has been produced.


### Combined removal-of-the-defender sequences — verification pending (2026-11-13)
- Added White `Rxd4 exd4 Rxd3 Rc1+ Kh2` and Black `...Rxc4+ Rxc4 ...Nb5#` combinations.
- Sequence corpus now contains **five combinations and nineteen annotated plies**. Tests account for both colours (White 9 / Black 10).
- CPU and Stockfish sequence audit are pending. No training or checkpoint evaluation was run.


### Five-sequence tactical benchmark — latest verified state (2026-11-13)
- Verified revision: `36ad6dd4ddcd06d7215b4abd99aa7d21d183201d`.
- CPU: **170 passed** ([43437925480](https://github.com/Nomusa990822/AlphaZero-Style-Chess-AI-Self-Play-Reinforcement-Learning-with-MCTS-and-Policy-Value-Networks/actions/runs/43437925480)).
- Stockfish: **22/22 positions supported, 0 flagged; 5/5 sequences and 19/19 annotated plies supported, 0 flagged** ([43437925723](https://github.com/Nomusa990822/AlphaZero-Style-Chess-AI-Self-Play-Reinforcement-Learning-with-MCTS-and-Policy-Value-Networks/actions/runs/43437925723), artifact `14043849570`).
- Five combinations cover checking fork/hanging queen, discovered check/hanging queen, decoy/hanging bishop, and White/Black removal-of-the-defender combinations. The corpus contains nineteen annotated plies with both colours represented.
- These results validate the annotated lines at finite depth; they do not prove every line is forced against all possible replies. No training, checkpoint evaluation or Elo claim has been made.


### Checkpoint recovery/readiness audit (2026-11-13)
- No checkpoint weights are currently present in the feature-branch Git tree; `data/checkpoints/` is intentionally gitignored. The GitHub release listing contains no checkpoint release. The latest 100 Actions runs include no invocation of the dedicated training-and-backup workflow.
- Historical JSONL training metrics are not model weights and cannot reconstruct `best_model.pt`.
- Added fail-fast behaviour when `resume_best_model=True` but the configured checkpoint is missing. Added a workflow preflight before dependency installation and documented the restore/evaluation process in `docs/training_flow.md`.
- Training remains unstarted. No checkpoint evaluation, Elo estimate or neural playing-strength claim has been made. CPU CI verification is pending.


### Checkpoint safety gate — latest CI result (2026-11-13)
- Verified revision: `837a0b44c8ec2144d1da32e97b4a29f2af192fe2`.
- CPU suite: **171 passed** ([43439201868](https://github.com/Nomusa990822/AlphaZero-Style-Chess-AI-Self-Play-Reinforcement-Learning-with-MCTS-and-Policy-Value-Networks/actions/runs/43439201868)); includes missing-checkpoint resume guard coverage.
- Stockfish: **22/22 positions supported, 0 flagged; 5/5 sequences and 19/19 annotated plies supported, 0 flagged** ([43439201743](https://github.com/Nomusa990822/AlphaZero-Style-Chess-AI-Self-Play-Reinforcement-Learning-with-MCTS-and-Policy-Value-Networks/actions/runs/43439201743), artifact `14045506585`).
- The training workflow now fails before dependency installation if the configured best checkpoint is absent. No training workflow was dispatched.
- No checkpoint was found in the current tracked tree or release listing; no model tactical evaluation, Elo estimate or playing-strength claim has been made.


## Fresh-start pilot readiness (2026-11-13)
- The previous learned checkpoint is unavailable. The original resume workflow remains protected by its missing-checkpoint gate.
- A separate, manually dispatched fresh-start CPU pilot is prepared on `chess-strength-training-upgrade`; it creates a clearly labelled random baseline and uses isolated pilot output paths.
- Pilot budget: 1 iteration, 4 self-play games, 80-ply cap, 8 MCTS simulations, 1 training epoch, and 2 paired evaluation games. This is a pipeline smoke test, not an Elo/strength test.
- The pilot workflow defaults to NO and requires YES. It has not been dispatched. CPU CI and Stockfish verification are pending.


## Fresh-start pilot — CI verified, not launched (2026-11-13)
- Prepared revision: `b3d4839939176e6e9cd9dbe2710eecb760060278`.
- CPU CI: **172 passed in 4.01 seconds** ([43490761455](https://github.com/Nomusa990822/AlphaZero-Style-Chess-AI-Self-Play-Reinforcement-Learning-with-MCTS-and-Policy-Value-Networks/actions/runs/43490761455)).
- Stockfish: **22/22 positions, 5/5 sequences and 19/19 annotated plies supported; zero flags** ([43490761420](https://github.com/Nomusa990822/AlphaZero-Style-Chess-AI-Self-Play-Reinforcement-Learning-with-MCTS-and-Policy-Value-Networks/actions/runs/43490761420)).
- Two duplicate push-triggered runs were cancelled and replaced by the passing PR-triggered runs; they were not failures.
- The pilot was not run. GitHub requires manual-dispatch workflows to exist on the default branch; because `main` is intentionally unchanged, the new workflow cannot be dispatched until it is merged or otherwise installed on the default branch. The PR remains unmerged.


## Tactical corpus expansion — validation pending (2026-11-13)

- Candidate corpus: **26 positions**, 14 White to move and 12 Black to move.
- Added overloaded-defender and trapped-piece examples for both colours, with source annotations and semantic line-replay tests.
- The CPU test suite and Stockfish tactical audit must pass before these positions are treated as validated or used in checkpoint comparisons.
- No training, checkpoint evaluation, or promotion occurred.


## Tactical corpus expansion — verified (2026-11-13)

- Verified feature-branch revision: `1808a23a2b94ac442b37b2f9ba5a70100604e99a`.
- CPU tests: **174 passed in 3.15 seconds** ([run 43504822887](https://github.com/Nomusa990822/AlphaZero-Style-Chess-AI-Self-Play-Reinforcement-Learning-with-MCTS-and-Policy-Networks/actions/runs/43504822887)).
- Stockfish 17.1 depth-16/MultiPV-5 review: **26/26 positions, 5/5 sequences and 19/19 annotated plies supported; zero flags** ([run 43504822942](https://github.com/Nomusa990822/AlphaZero-Style-Chess-AI-Self-Play-Reinforcement-Learning-with-MCTS-and-Policy-Networks/actions/runs/43504822942), artifact `14075917276`).
- Corpus: **26 positions (White 14 / Black 12)**. Both overloaded-defender and trapped-piece motifs now have White and Black examples, with semantic line-replay tests.
- This finite-depth audit does not prove all possible defences or validate every human motif label. No training, checkpoint evaluation, checkpoint promotion, Elo estimate or playing-strength claim was made. The baseline remains selected.
- Earlier superseded workflow attempts were cancelled, not failed; the final CPU and Stockfish runs above both succeeded on the same commit.
