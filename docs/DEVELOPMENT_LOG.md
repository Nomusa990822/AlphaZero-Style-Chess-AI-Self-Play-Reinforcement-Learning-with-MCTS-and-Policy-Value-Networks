## 2026-11-13 — Verify paired tactical-filter runner and final tracking revision

### Verification
- Final tracking/documentation revision tested: `b05fc8e82460864674dc682d2b0fa3b05639b8f7`.
- CPU workflow [43407927386](https://github.com/Nomusa990822/AlphaZero-Style-Chess-AI-Self-Play-Reinforcement-Learning-with-MCTS-and-Policy-Value-Networks/actions/runs/43407927386): **passed; 117 tests passed in 3.64 seconds** on Python 3.11.
- Stockfish tactical audit [43407927265](https://github.com/Nomusa990822/AlphaZero-Style-Chess-AI-Self-Play-Reinforcement-Learning-with-MCTS-and-Policy-Value-Networks/actions/runs/43407927265): **passed**; all 13 curated positions were reviewed, all 13 had at least one accepted move within the configured 150-centipawn tolerance, and 0 positions were flagged for human review. The `tactical-engine-audit` artifact uploaded successfully (artifact ID `14028002780`).
- Duplicate workflow attempts on the same revision also completed successfully: CPU run [43407920821](https://github.com/Nomusa990822/AlphaZero-Style-Chess-AI-Self-Play-Reinforcement-Learning-with-MCTS-and-Policy-Value-Networks/actions/runs/43407920821) and audit run [43407920724](https://github.com/Nomusa990822/AlphaZero-Style-Chess-AI-Self-Play-Reinforcement-Learning-with-MCTS-and-Policy-Value-Networks/actions/runs/43407920724). These are additional successful runs, not failures or cancellations.
- Earlier implementation/test revision `861602a6f258266f3c39561b58cbb1aa3af74ce5` also passed 117 tests in CPU run [43407844131](https://github.com/Nomusa990822/AlphaZero-Style-Chess-AI-Self-Play-Reinforcement-Learning-with-MCTS-and-Policy-Value-Networks/actions/runs/43407844131).
- The paired tactical-filter runner and its regression tests are CI-verified. The audit checks the curated corpus with finite-depth Stockfish; it does not establish neural-network playing strength or Elo.
- No committed compatible checkpoint was found in the repository. The real checkpoint-on/off experiment remains **not run**; no experimental score or strength improvement is claimed.

### Follow-up
- Run the paired comparison only when a compatible trained checkpoint is available. Use identical checkpoint, corpus, device and simulation budget for both modes, then preserve the generated JSON and checkpoint hash in `EXPERIMENT_LOG.md`.

## 2026-11-13 — Add a single-process paired tactical-filter benchmark

### Goal and implementation
- Added `compare_tactical_filters.py` to compare root tactical filtering enabled versus disabled using one checkpoint load, one shared model/inference wrapper, the same corpus, device, simulation budget, no Dirichlet noise and deterministic temperature-zero selection.
- The JSON report records checkpoint SHA-256/epoch, per-position moves and correctness, paired selection changes and correctness disagreements, per-motif/colour/phase scores, and descriptive runtime.
- Added `tests/test_compare_tactical_filters.py` to verify both configurations, shared checkpoint/inference setup, paired result accounting and report writing.
- Documented the one-command workflow and report interpretation in `benchmarks/README.md`.

### Verification
- Implementation commits: `6c74171c3f1fae51fb649a7dca6fb3155c8e8347` (runner), `12817ee5ec53bcb03aa09320bb8c8180b97a6932` (test), and `861602a6f258266f3c39561b58cbb1aa3af74ce5` (report newline correction).
- Documentation and tracking update: CI pending on the final commit created for this batch.
- Repository tree inspection found no committed checkpoint file. A compatible local checkpoint is required to produce a meaningful paired benchmark; no untrained-network result will be presented as learned strength.
- No benchmark experiment has been run and no playing-strength or Elo claim is made.

### Follow-up
- Verify the new test and both CI workflows. Once a compatible checkpoint is available locally, run the documented paired command and preserve its JSON report and checkpoint hash in `EXPERIMENT_LOG.md`.

## 2026-11-13 — Verify configurable tactical-root-filter ablation

### Verification
- Final branch head tested: `975783715abe5fa218fd6b9eec7c8c75be8f0e59`.
- Earlier queued/superseded workflow attempts [43407141233](https://github.com/Nomusa990822/AlphaZero-Style-Chess-AI-Self-Play-Reinforcement-Learning-with-MCTS-and-Policy-Value-Networks/actions/runs/43407141233) and [43407141255](https://github.com/Nomusa990822/AlphaZero-Style-Chess-AI-Self-Play-Reinforcement-Learning-with-MCTS-and-Policy-Value-Networks/actions/runs/43407141255) were cancelled before completing. These are recorded as cancellations, not test failures.
- Final CPU test workflow [43407151824](https://github.com/Nomusa990822/AlphaZero-Style-Chess-AI-Self-Play-Reinforcement-Learning-with-MCTS-and-Policy-Value-Networks/actions/runs/43407151824): **passed; 116 tests passed in 3.40 seconds** on Python 3.11.
- Final Stockfish tactical audit workflow [43407151987](https://github.com/Nomusa990822/AlphaZero-Style-Chess-AI-Self-Play-Reinforcement-Learning-with-MCTS-and-Policy-Value-Networks/actions/runs/43407151987): **passed**; finite-depth tactical review completed and the `tactical-engine-audit` JSON artifact was uploaded successfully (artifact ID `14027892081`).
- Both final workflows tested the same PR head revision. The ablation implementation is therefore CI-verified. No real-checkpoint filter-on/filter-off comparison has been run; no playing-strength improvement or Elo claim is made.

### Follow-up
- Run the documented paired tactical benchmark with the same actual checkpoint, corpus, device and simulation budget when a compatible checkpoint is available. Record measured results in `EXPERIMENT_LOG.md`, not from CI.

## 2026-11-13 — Add tactical-root-filter ablation for reproducible comparisons

### Changes
- Added `MCTSConfig.use_tactical_root_filter`, enabled by default, to switch exact root mate-in-one priority and one-ply mate-safety filtering on or off for controlled experiments.
- Applied the setting consistently during root simulation candidate selection, final move selection, and action-probability generation. Default behavior remains unchanged.
- Added `evaluate_tactics.py --disable-tactical-root-filter` and included the active setting in the JSON report.
- Added a regression test proving that disabling the filter restores ordinary visit-based root selection and includes all legal root actions in the policy target.
- Documented paired on/off benchmark commands. Meaningful comparison requires the same checkpoint, corpus, device, and simulation budget.

### Verification
- Latest code/test changes: `4aa7ab0aa8bc075e59a07e3edfe0c47a22136fd2`; benchmark documentation subsequently updated in `85dc43e8801a35f62e9e465a34f32c3a24fe4489`.
- CPU tests and Stockfish audit for this ablation change: **pending**.
- No trained checkpoint comparison or playing-strength result has been produced. The ablation switch enables a future controlled measurement; it does not itself demonstrate improvement.

### Follow-up
- Inspect CI, preserve any failure and repair details, and record the first passing run. Then use the same real checkpoint and budget for filter-on/filter-off benchmark runs when a checkpoint is available.

## 2026-11-13 — Extend root tactical-search regression coverage to Black and forced-loss positions

### Changes
- Added a Black-to-move MCTS simulation regression proving that all root simulations are allocated to immediate mating moves when available.
- Added a forced-loss MCTS regression proving that, when every legal move permits an immediate opponent mate, the search candidate set retains every legal root move rather than collapsing to an empty set.
- These tests cover both colours and the forced-loss fallback in the actual simulation path, complementing the existing White mate-in-one simulation test.

### Verification
- Test-only code revision: `187ad05954a70f28c7c3576f4d70139f4c1dbdc5`; the final workflow-triggering branch head also included the documentation-only tracking update `c1720e7b70ee4d48f78e7c79af565f7576444dcb`.
- CPU test workflow [43406633328](https://github.com/Nomusa990822/AlphaZero-Style-Chess-AI-Self-Play-Reinforcement-Learning-with-MCTS-and-Policy-Value-Networks/actions/runs/43406633328): **passed**; all **115 tests passed** in 3.52 seconds on Python 3.11.
- Stockfish tactical audit workflow [43406633323](https://github.com/Nomusa990822/AlphaZero-Style-Chess-AI-Self-Play-Reinforcement-Learning-with-MCTS-and-Policy-Value-Networks/actions/runs/43406633323): **passed**; finite-depth review and report upload completed successfully. No tactical corpus or audit implementation changed in this test-only batch.
- Superseded runs [43406629168](https://github.com/Nomusa990822/AlphaZero-Style-Chess-AI-Self-Play-Reinforcement-Learning-with-MCTS-and-Policy-Value-Networks/actions/runs/43406629168) and [43406629166](https://github.com/Nomusa990822/AlphaZero-Style-Chess-AI-Self-Play-Reinforcement-Learning-with-MCTS-and-Policy-Value-Networks/actions/runs/43406629166) also completed successfully on the same final branch head.
- No real-checkpoint benchmark, training run, or playing-strength measurement was produced.

### Follow-up
- Continue with a reproducible, resource-bounded search-quality benchmark. Preserve every future failure and successful CI run in this log.

## 2026-11-13 — Apply root tactical constraints during MCTS simulation

### Changes
- Extended PUCT child selection to accept an explicit eligible-child set while preserving unrestricted selection as the default.
- MCTS now computes its root tactical candidate set once before simulations and uses that set whenever selecting the root action.
- Root search prioritises all legal mate-in-one moves; otherwise it excludes moves that permit an immediate opponent mate when at least one safe move exists.
- The existing forced-loss fallback is preserved: if every legal move permits mate in one, all root children remain eligible.
- Added regressions proving restricted PUCT selection and that a mate-in-one root spends its simulations on mating moves only. Deeper tree selection remains unrestricted.

### Verification
- Verified implementation revision: `7f39e43b0b0174b730f3facf194d68577c6d3a10`.
- CPU test workflow [43406066354](https://github.com/Nomusa990822/AlphaZero-Style-Chess-AI-Self-Play-Reinforcement-Learning-with-MCTS-and-Policy-Value-Networks/actions/runs/43406066354): **passed**; all **113 tests passed** in 3.78 seconds on Python 3.11.
- Stockfish tactical audit workflow [43406066235](https://github.com/Nomusa990822/AlphaZero-Style-Chess-AI-Self-Play-Reinforcement-Learning-with-MCTS-and-Policy-Value-Networks/actions/runs/43406066235): **passed**; the finite-depth review completed and uploaded the `tactical-engine-audit` artifact (artifact ID `14026509085`).
- Both workflows tested the same implementation revision. The root tactical candidate-set regression tests are included in the 113-test suite.
- No real-checkpoint tactical benchmark, training run, or playing-strength measurement was produced by this search change. This is a search-budget allocation improvement; strength improvement must be measured separately.

### Follow-up
- Continue with measurable search-quality work and a reproducible fixed-opponent evaluation protocol. Preserve every future failed and successful CI result in this log.

## 2026-11-13 — Semantic regression repair verified by CI

### Verification
- Repaired revision: `592671dc283ab86d0dc52a285c74da8204f0fc3b`.
- CPU test workflow [43404899202](https://github.com/Nomusa990822/AlphaZero-Style-Chess-AI-Self-Play-Reinforcement-Learning-with-MCTS-and-Policy-Value-Networks/actions/runs/43404899202): **completed successfully** on the repaired revision.
- Stockfish tactical audit workflow [43404899148](https://github.com/Nomusa990822/AlphaZero-Style-Chess-AI-Self-Play-Reinforcement-Learning-with-MCTS-and-Policy-Value-Networks/actions/runs/43404899148): **completed successfully** on the same revision.
- These are the first successful follow-up runs after the fork-test coordinate failure [43404336724](https://github.com/Nomusa990822/AlphaZero-Style-Chess-AI-Self-Play-Reinforcement-Learning-with-MCTS-and-Policy-Value-Networks/actions/runs/43404336724). The failed run remains in this history; it is not overwritten.
- The CPU suite validates automated behavior, and the audit validates finite-depth engine agreement for the curated corpus. Neither result establishes neural-network playing strength or an Elo rating.

## 2026-11-13 — Add motif-specific tactical semantics tests; correct fork geometry

### Changes
- Added `tests/test_tactical_corpus_semantics.py` to verify that curated moves demonstrate their stated ideas, including checkmate, forks, undefended-piece captures, absolute pins, skewers, discovered check/attack, a defensive check evasion, and promotion with check.
- The first full CI run for these tests, [43404336724](https://github.com/Nomusa990822/AlphaZero-Style-Chess-AI-Self-Play-Reinforcement-Learning-with-MCTS-and-Policy-Value-Networks/actions/runs/43404336724), **failed** in `test_both_fork_moves_attack_the_king_and_queen`: the test expected the black king on e8, but the corpus FEN places it on f8. This was a test-coordinate error; the failure did not show that the corpus move was illegal.
- Corrected the expected king square from e8 to f8 in commit `62bbeff2df149e525715cf119474a0591e6069e8`.

### Verification
- Failed run: [43404336724](https://github.com/Nomusa990822/AlphaZero-Style-Chess-AI-Self-Play-Reinforcement-Learning-with-MCTS-and-Policy-Value-Networks/actions/runs/43404336724) — test suite failed on the incorrect square assertion.
- Repair revision: `62bbeff2df149e525715cf119474a0591e6069e8` — **CI pending; do not mark the semantic-test batch as passed until a completed successful run is recorded.**
- The prior thirteen-position Stockfish audit and prior CPU test run remain successful historical checks; they do not validate this newly added test file.
- No checkpoint benchmark or playing-strength result was produced by this test-only change.

### Follow-up
- Check the next full CPU test run. If another semantic assertion fails, inspect the exact FEN and board geometry, correct the test only when the corpus annotation is sound, and record each run outcome here and in Project Status.

## 2026-11-13 — Add reproducible Stockfish-assisted tactical review

### Changes
- Added `scripts/audit_tactical_corpus.py` to compare engine top lines with each curated acceptable move at a fixed search depth.
- Added a dedicated GitHub Actions workflow that installs Stockfish, runs a depth-16/MultiPV-5 review, and uploads a JSON report artifact.
- The report records engine identity, principal variations, per-accepted-move scores, score loss from the engine's best line, and positions flagged for human review.
- Added unit tests for supported and flagged accepted-move scenarios using a deterministic fake engine.

### Verification
- GitHub Actions Stockfish audit run [43403925496](https://github.com/Nomusa990822/AlphaZero-Style-Chess-AI-Self-Play-Reinforcement-Learning-with-MCTS-and-Policy-Networks/actions/runs/43403925496): **completed successfully** using Stockfish 17.1, depth 16, MultiPV 5, one thread, 256 MB hash and a 150-centipawn tolerance.
- The engine reviewed all thirteen positions: **13/13 accepted moves were within tolerance; 0 positions were flagged**. The workflow uploaded the `tactical-engine-audit` JSON artifact, and its report was also printed to the workflow log for inspection.
- CPU test workflow run [43403925592](https://github.com/Nomusa990822/AlphaZero-Style-Chess-AI-Self-Play-Reinforcement-Learning-with-MCTS-and-Policy-Networks/actions/runs/43403925592): **completed successfully**.
- Finite-depth engine agreement supports the accepted moves but does not prove tactical optimality or validate every human motif label/annotation. No real neural-network checkpoint benchmark or playing-strength gain is claimed.

### Follow-up
- Inspect the uploaded JSON artifact, manually review flagged positions and motif explanations, then update the corpus only when the rationale and accepted move set are supported.

## 2026-11-13 — Add discovered attack, defensive resource and promotion tactics

### Changes
- Expanded the tactical corpus from nine to thirteen positions.
- Added a White-to-move discovered check that attacks a queen, a Black-to-move capture of a checking rook, and pawn promotions with check for both colours.
- Added tests for each position's motif, side to move, phase and accepted legal UCI move; strengthened corpus coverage checks.
- The corpus now has seven White-to-move and six Black-to-move positions and represents eight tactical labels. It remains a small diagnostic set.

### Verification
- The existing corpus loader checks FEN validity, terminal-state status, duplicate identifiers and accepted-move legality. CI is required to verify this batch.
- Tactical annotations explain the intended idea but do not substitute for engine analysis or a large independent puzzle source.
- No real-checkpoint benchmark or playing-strength gain is claimed.

### Follow-up
- Review CI, then consider adding more examples and improving benchmark ground truth with engine-assisted review before relying on scores.

## 2026-11-13 — Expand tactical corpus with skewers and black-to-move examples

### Changes
- Expanded `benchmarks/tactical_positions.jsonl` from five to nine positions.
- Added a White-to-move rook skewer, a Black-to-move rook skewer, a Black-to-move knight capture of an undefended rook, and a Black-to-move capture of an absolutely pinned rook.
- Added explicit tests for each new position's side to move, motif, and accepted legal UCI move; strengthened corpus coverage checks.
- Corrected a literal escaped newline in the benchmark README and updated corpus/report descriptions.
- The corpus now has five White-to-move and four Black-to-move positions. This improves balance but remains a small diagnostic sample, not a comprehensive tactics suite.

### Verification
- The existing `python-chess` loader checks FEN validity, terminal-state status, and accepted-move legality; the expanded corpus tests exercise those checks for every entry.
- GitHub Actions for this update is pending; do not treat this commit as verified until the PR workflow completes.
- No real-checkpoint tactical benchmark was run and no playing-strength gain is claimed.

### Follow-up
- Review the new CI run. Then add defensive-resource, discovered-attack, and endgame examples only when their tactical correctness and acceptable move sets can be checked.

## 2026-11-13 — Expand tactical corpus with skewers and black-to-move examples

### Changes
- Expanded `benchmarks/tactical_positions.jsonl` from five to nine positions.
- Added a White-to-move rook skewer, a Black-to-move rook skewer, a Black-to-move knight capture of an undefended rook, and a Black-to-move queen checking fork.
- Added explicit tests for each new position's side to move, motif, and accepted legal UCI move; strengthened corpus coverage checks.
- Corrected a literal escaped newline in the benchmark README and updated corpus/report descriptions.
- The corpus now has five White-to-move and four Black-to-move positions. This improves balance but remains a small diagnostic sample, not a comprehensive tactics suite.

### Verification
- FEN validity, terminal-state checks, and accepted-move legality are enforced by the existing `python-chess` corpus loader and the GitHub Actions test suite.
- The new positions have not yet been CI-verified; the latest workflow result must be checked before calling this batch complete.
- No real-checkpoint tactical benchmark was run and no playing-strength gain is claimed.

### Follow-up
- Review the new CI run. Then add defensive-resource, discovered-attack, and endgame examples only when their tactical correctness and acceptable move sets can be checked.

## 2026-11-13 — Add explicit game-phase tactical reporting

### Changes
- Added a required curated `phase` field to tactical benchmark records: `opening`, `middlegame`, or `endgame`.
- Deliberately avoided inferring phase from material count; composed tactical positions can make automatic phase heuristics misleading.
- Added per-phase totals, correct/illegal counts, and accuracy to benchmark results and the checkpoint JSON report.
- Labelled all five existing corpus positions and added tests for missing/unknown phases and phase aggregation.
- This change adds diagnostic segmentation only; it does not add positions or establish tactical strength.

### Verification
- The preceding syntax-repair revision `b2dfa830d6100c900e5c944b4bb1c7b3e6361059` passed GitHub Actions run [43398823052](https://github.com/Nomusa990822/AlphaZero-Style-Chess-AI-Self-Play-Reinforcement-Learning-with-MCTS-and-Policy-Value-Networks/actions/runs/43398823052).
- CI for this phase-reporting change is pending until the new workflow run completes.
- No real-checkpoint tactical benchmark was run.

### Follow-up
- Use the new phase/motif/colour breakdowns to identify actual coverage gaps before adding independently reviewed positions.

## 2026-11-13 — Repair tactical benchmark validation and add colour-balanced scoring

**Implementation:** `9e3e4f397e3da11de75cdef7b79e7bedd1113ba8`  
**Core regression tests:** `dbf3494b15402c9a37973770086eb6f9ce05c88d`  
**CLI/report tests:** `35c97c6188371d19944b277e91e2a2e30a105f41`  
**Additional colour tests:** `69749f5f1d2d99ffb6a806ca71cc0dc2dca833a9`  
**Documentation:** `48468a527c522396e84b630ce697f91be5d097eb`

### Changes
- Fixed literal newline escape sequences introduced in the previous annotation-validation patch. The failed CI run [43397911821](https://github.com/Nomusa990822/AlphaZero-Style-Chess-AI-Self-Play-Reinforcement-Learning-with-MCTS-and-Policy-Value-Networks/actions/runs/43397911821) identified Python syntax errors during test collection; no test assertions ran in that attempt.
- Tactical benchmark results now include separate White-to-move and Black-to-move totals, correct counts, illegal counts, and accuracy.
- The JSON CLI report includes these colour-specific metrics.
- Added regression coverage for multiple acceptable moves and separate colour scoring; the existing corpus test checks both sides to move.
- Updated benchmark documentation. No new FEN positions were added in this repair/evaluation batch.

### Verification
- CI for the corrected branch revision is pending.
- The five-position corpus remains a small starter set. Side-specific reporting makes imbalance visible; it does not itself create broad tactical coverage.
- No real-checkpoint tactical benchmark or playing-strength improvement is claimed.

### Follow-up
- Wait for CI; then extend the corpus only with positions whose tactical idea and acceptable moves have been independently checked.

## 2026-11-13 — Require tactical rationales and add a reviewed pin example

**Corpus revision:** `580d95901d8670eb5387fc77ede0874a218b9d01`  
**Validation implementation:** `b0f373afc1eb4398c8913e4669b8f63426c9e42b`  
**Regression tests:** `69749f5f1d2d99ffb6a806ca71cc0dc2dca833a9`  
**Benchmark documentation:** `abefc8d86345a90212712b5d1bfc2beaa75303fb`

### Changes
- Added a required, non-empty human annotation to each tactical benchmark record. The annotation explains the intended motif and why the accepted move demonstrates it; it improves auditability but does not automatically prove tactical soundness.
- Extended the starter corpus to five positions with a rook capture of an absolutely pinned rook, in addition to the existing mating net, two-colour knight forks and hanging-queen capture.
- Added tests for missing and blank annotations and documented the updated JSONL schema and corpus limitations.
- Kept the corpus intentionally small rather than adding unverified positions.

### Verification
- The preceding branch revision passed GitHub Actions run [43397248955](https://github.com/Nomusa990822/AlphaZero-Style-Chess-AI-Self-Play-Reinforcement-Learning-with-MCTS-and-Policy-Value-Networks/actions/runs/43397248955).
- CI for the annotation/pin update is pending.
- No real-checkpoint tactical benchmark or playing-strength improvement is claimed.

### Follow-up
- Check CI, then add further positions only after checking legality and the tactical idea for both sides to move.

## 2026-11-13 — Enforce a controlled tactical motif taxonomy

**Implementation revision:** `55bcd72f494f575f9171cf35bc569eb341371b77`  
**Regression-test revision:** `135b863d5acc80e118455918506661a16342609e`  
**Benchmark documentation revision:** `058097ce1928300e4130eeb781f02f72e6aba843`

### Changes
- Added a canonical set of supported tactical motif labels covering mating nets, forks, hanging pieces, pins, skewers, discovered attacks, double attacks, deflections, decoys, overloaded defenders, trapped pieces, defensive resources and endgame tactics.
- The corpus loader now rejects unknown labels rather than silently creating inconsistent per-motif score groups.
- Added a regression test for unknown motif rejection and documented the accepted taxonomy.

### Verification
- The preceding code batch passed the full GitHub Actions CPU test suite in run [43396703300](https://github.com/Nomusa990822/AlphaZero-Style-Chess-AI-Self-Play-Reinforcement-Learning-with-MCTS-and-Policy-Value-Networks/actions/runs/43396703300).
- CI for this taxonomy change is pending.
- This is a data-quality safeguard; it does not increase chess playing strength by itself.

### Follow-up
- Grow the corpus with independently reviewed tactical examples, then run it against a real checkpoint when a compatible checkpoint is available.

## 2026-11-13 — Test the tactical evaluation CLI

**Test revision:** `3d203b13dff5931b882bfbb1ec9f191a2229d00e`  
**Documentation revision:** `5fd50caab0da4971c218c9eaced4140fd982d70d`

### Changes
- Added isolated tests for CPU device selection and explicit failure when CUDA is requested but unavailable.
- Added a mocked end-to-end CLI test covering checkpoint loading, deterministic MCTS configuration (no Dirichlet noise, zero temperature), selector invocation, JSON report contents and output-file writing.
- Added a missing-checkpoint regression test.
- Updated benchmark documentation to describe the four-position starter corpus and its limitations.

### Verification
- GitHub Actions for the previous corpus update was queued when checked; the new CLI tests are awaiting CI.
- Tests mock model/search execution and do not require a real checkpoint or GPU.
- No real-checkpoint tactical benchmark or playing-strength improvement is claimed.

### Follow-up
- Review the CI result, then continue growing the tactical corpus only with independently verified positions and meaningful tactical ground truth.

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


## 2026-11-13 — Protect trained checkpoints from ephemeral workspace loss

**Implementation revision:** `822b2213d5931499853c1c67391e8d8243140ab5` — CI verified.

### Changes
- Added a manual-only GitHub Actions training workflow requiring explicit `YES`; ordinary pushes and pull requests never start training.
- The workflow uploads generated `.pt` files as a 90-day Actions artifact, including when training fails after producing a checkpoint.
- Successful training publishes checkpoint files and a SHA-256 manifest as a durable GitHub prerelease asset.
- Added a manifest generator and regression tests for hashing, empty directories and symlink exclusion.
- Documented the recovery procedure while keeping model binaries out of Git history.

### Verification
- CPU workflow [43409861234](https://github.com/Nomusa990822/AlphaZero-Style-Chess-AI-Self-Play-Reinforcement-Learning-with-MCTS-and-Policy-Value-Networks/actions/runs/43409861234): **passed; 120 tests passed in 3.65 seconds** on Python 3.11, including the three new checkpoint-manifest tests.
- Stockfish tactical audit [43409861252](https://github.com/Nomusa990822/AlphaZero-Style-Chess-AI-Self-Play-Reinforcement-Learning-with-MCTS-and-Policy-Value-Networks/actions/runs/43409861252): **passed**; finite-depth tactical review and report upload completed successfully.
- Both workflows tested commit `822b2213d5931499853c1c67391e8d8243140ab5`. No training run was started and no new model weights are claimed.
- Release backup occurs only after successful training; artifact upload is attempted regardless of training success.

### Follow-up
- When training is intentionally authorised, use the manual workflow and explicitly confirm `YES`. After successful training, download the prerelease checkpoint and manifest to independent storage. The 90-day Actions artifact is temporary, not a permanent archive.


## 2026-11-13 — Resource-bounded MCTS configuration benchmark

- **Goal:** compare simulation budgets, PUCT constants and tactical-root-filter modes without launching training.
- **Design:** load one real checkpoint and inference wrapper; disable Dirichlet noise; select at temperature zero; preflight the complete simulation count and reject over-budget runs before loading the model.
- **Implementation:** added `benchmark_search_configs.py`, parser/budget regression tests and usage documentation.
- **Verification:** pending CI on this revision. No real-checkpoint benchmark was executed because no compatible checkpoint is available; no playing-strength result is claimed.
- **Prior verification:** documentation commit `e100f226b9df853e0bb36873989eb2eb5996dcff` passed CPU workflow [43410650186](https://github.com/Nomusa990822/AlphaZero-Style-Chess-AI-Self-Play-Reinforcement-Learning-with-MCTS-and-Policy-Value-Networks/actions/runs/43410650186): **120 passed in 3.68 seconds**.
- **Follow-up:** run this sweep only after a compatible checkpoint is generated and independently backed up; record actual measurements in `EXPERIMENT_LOG.md`.


## 2026-11-13 — Verify resource-bounded MCTS configuration benchmark

### Verification
- Tested branch revision: `040877a1ab822e7023a68b8f025eb17535eac073`.
- CPU test workflow [43411211787](https://github.com/Nomusa990822/AlphaZero-Style-Chess-AI-Self-Play-Reinforcement-Learning-with-MCTS-and-Policy-Value-Networks/actions/runs/43411211787): **passed; 135 tests passed in 3.58 seconds** on Python 3.11.
- Stockfish tactical audit workflow [43411211867](https://github.com/Nomusa990822/AlphaZero-Style-Chess-AI-Self-Play-Reinforcement-Learning-with-MCTS-and-Policy-Value-Networks/actions/runs/43411211867): **passed**; finite-depth review completed and the `tactical-engine-audit` JSON artifact uploaded successfully (artifact ID `14029253397`).
- Both workflows completed successfully on the same benchmark revision. The new budget/parser regression tests are included in the 135-test CPU suite.
- The search-configuration benchmark itself has **not** been executed: no compatible trained checkpoint is currently available. No training run, real-checkpoint experiment, playing-strength gain or Elo claim is made.

### Follow-up
- Preserve a compatible checkpoint independently before running the resource-bounded search sweep. Use the same checkpoint, corpus, device and controlled budgets; save actual output and checkpoint hash in `EXPERIMENT_LOG.md`.


## 2026-11-13 — Exercise the MCTS configuration benchmark execution path

### Changes
- Refactored the sweep orchestration into \`run_benchmark(args)\` so the execution path can be tested independently of CLI parsing and with replaceable model/search components.
- Added mocked end-to-end orchestration coverage for all simulation-budget, PUCT and filter-mode combinations, single network construction, deterministic search settings, checkpoint SHA-256/epoch metadata, per-position selections, and persisted JSON report round-tripping.
- Added preflight regression coverage proving an over-budget plan is rejected before network construction and a missing checkpoint is rejected before corpus loading.
- Hardened the PUCT parser to reject non-finite values (\`nan\`, positive/negative infinity) as well as non-positive values.
- No training or actual checkpoint search is performed by these tests.

### Verification
- Implementation/test revision `0f12e052434a66f03499bd1f91abafa1afeeb2fa`: CPU CI and Stockfish audit both **passed** (details below).
- Existing latest verified baseline remains \`040877a1ab822e7023a68b8f025eb17535eac073\`: 135 CPU tests passed in 3.58 seconds (run [43411211787](https://github.com/Nomusa990822/AlphaZero-Style-Chess-AI-Self-Play-Reinforcement-Learning-with-MCTS-and-Policy-Value-Networks/actions/runs/43411211787)); Stockfish audit [43411211867](https://github.com/Nomusa990822/AlphaZero-Style-Chess-AI-Self-Play-Reinforcement-Learning-with-MCTS-and-Policy-Value-Networks/actions/runs/43411211867) passed.
- No compatible trained checkpoint is available; no search sweep, training run, playing-strength result or Elo claim is produced.

### Follow-up
- Inspect the first CI run for this batch. Preserve any failure and repair it before updating the verified revision. Once CI passes, use the real checkpoint only when it has been recovered and independently backed up.


### CI verification
- CPU test workflow [43412113192](https://github.com/Nomusa990822/AlphaZero-Style-Chess-AI-Self-Play-Reinforcement-Learning-with-MCTS-and-Policy-Value-Networks/actions/runs/43412113192): **passed; 142 tests passed in 3.20 seconds** on Python 3.11.
- Stockfish tactical audit workflow [43412113210](https://github.com/Nomusa990822/AlphaZero-Style-Chess-AI-Self-Play-Reinforcement-Learning-with-MCTS-and-Policy-Value-Networks/actions/runs/43412113210): **passed**; the \`tactical-engine-audit\` artifact uploaded successfully (artifact ID \`14030281382\`).
- Both workflows tested the same revision \`0f12e052434a66f03499bd1f91abafa1afeeb2fa\`. The new mocked execution-path and parser tests are included in the 142-test CPU suite.
- The benchmark has still **not** been run against a real checkpoint. No training, actual search experiment, playing-strength gain or Elo claim is made.


## 2026-11-13 — Add bounded forced-mate-in-two root detection

### Changes
- Added find_forced_mate_in_two, which verifies every opponent reply for a candidate root move and checks whether the moving side then has a legal mate-in-one.
- Added a strict reply-inspection budget (512 across the root position). If the budget interrupts a candidate, that candidate is discarded rather than treated as proven. This deliberately favours false negatives over false tactical claims in high-branching positions.
- Integrated verified mate-in-two candidates into the root simulation/action candidate set, after immediate mate-in-one and before the existing one-ply mate-avoidance filter. MCTS, neural priors and PUCT remain the main search.
- Added tests for the all-replies condition, board-state preservation and incomplete-candidate handling.
- This is a tactical root extension, not a general quiescence search or full minimax engine.

### Verification
- Implementation revision: pending commit and GitHub Actions.
- CPU tests and Stockfish audit: pending. Do not treat this change as verified until both workflows complete.
- No checkpoint search, training, playing-strength measurement or Elo result was produced. The bounded detector may miss a genuine mate-in-two when the reply budget is exhausted.

### Follow-up
- Review runtime and test results. If the safeguard is too costly or causes regressions, narrow or disable it rather than weakening its correctness conditions.


### Failure and repair — 2026-11-13
- CPU workflow [43414004807](https://github.com/Nomusa990822/AlphaZero-Style-Chess-AI-Self-Play-Reinforcement-Learning-with-MCTS-and-Policy-Value-Networks/actions/runs/43414004807): **failed during pytest collection**. Python reported a SyntaxError on line 17 of src/mcts/search.py because the multiline tactics import contained literal backslash-n sequences.
- Repeated CPU workflow [43414014065](https://github.com/Nomusa990822/AlphaZero-Style-Chess-AI-Self-Play-Reinforcement-Learning-with-MCTS-and-Policy-Value-Networks/actions/runs/43414014065): **same failure**, not an independent test regression. Twelve modules could not be collected; no test assertions ran.
- Root cause: the generated import string encoded newline escapes literally. Corrected the import to use real source line breaks.
- These failed attempts remain recorded as failures. A new successful CI run is required before this code revision is considered verified.


### Repair follow-up — 2026-11-13
- The first repair commit 96a1d06e6cec6f93b2d1997cde0d5ff4b995b0d6 did not fully replace the literal escape sequences; the import remained syntactically invalid. This was caught by inspecting the committed source before relying on a new CI result.
- Replaced the literal backslash-n characters with actual source newlines in the tactics import. A fresh CI run is required; both earlier failed runs remain recorded above.


## 2026-11-13 — Forced mate-in-two CI failure and source repair follow-up

- Repaired revision `fff08dcc147e5275914816244b7d09d8ac15b7ae` CPU workflow [43415963144](https://github.com/Nomusa990822/AlphaZero-Style-Chess-AI-Self-Play-Reinforcement-Learning-with-MCTS-and-Policy-Value-Networks/actions/runs/43415963144): **failed during pytest collection**. Python reported a SyntaxError at line 205 of `src/mcts/search.py`: the forced-mate integration block contained literal `\\n` sequences. Twelve test modules could not be collected; no test assertions ran.
- Stockfish tactical audit [43415963147](https://github.com/Nomusa990822/AlphaZero-Style-Chess-AI-Self-Play-Reinforcement-Learning-with-MCTS-and-Policy-Value-Networks/actions/runs/43415963147): **passed** on the same revision and uploaded artifact `14031965643`. This does not compensate for the failed CPU suite.
- Corrected the malformed forced-mate block to use actual source line breaks in commit `ba247182a03ce116e0e038679f62d15deabb5cab`. This is a source-format repair, not yet CI-verified. Fresh CPU tests and the Stockfish audit are required before marking the feature verified.
- Preserve both outcomes above as separate workflow results; do not describe the feature as passed until the repaired revision completes both workflows successfully.


## 2026-11-13 — Bounded forced mate-in-two safeguard verified

- Final verified branch revision: `065d9165df3e0c40873ddd6e8c9f551f48d8182c`. This revision includes the corrected source block from `ba247182a03ce116e0e038679f62d15deabb5cab` plus the tracking-document updates.
- CPU workflow [43416399616](https://github.com/Nomusa990822/AlphaZero-Style-Chess-AI-Self-Play-Reinforcement-Learning-with-MCTS-and-Policy-Value-Networks/actions/runs/43416399616): **passed; 144 tests passed in 3.34 seconds** on Python 3.11.
- Stockfish tactical audit [43416399760](https://github.com/Nomusa990822/AlphaZero-Style-Chess-AI-Self-Play-Reinforcement-Learning-with-MCTS-and-Policy-Value-Networks/actions/runs/43416399760): **passed**; Stockfish 17.1 reviewed all 13 corpus positions, 13 were supported within the configured tolerance, 0 were flagged for human review, and artifact `tactical-engine-audit` (ID `14031444001`) uploaded successfully.
- The immediately preceding runs [43416353605](https://github.com/Nomusa990822/AlphaZero-Style-Chess-AI-Self-Play-Reinforcement-Learning-with-MCTS-and-Policy-Value-Networks/actions/runs/43416353605) and [43416353083](https://github.com/Nomusa990822/AlphaZero-Style-Chess-AI-Self-Play-Reinforcement-Learning-with-MCTS-and-Policy-Value-Networks/actions/runs/43416353083) were cancelled when subsequent tracking-document commits superseded their source revision. They are recorded as cancellations, not failures or passes. The final successful workflows ran on the newer branch head containing the same repaired source.
- The earlier syntax/collection failures and unsuccessful first repair remain preserved above. The bounded mate-in-two safeguard is now CI-verified. No trained checkpoint experiment, training run, playing-strength gain or Elo result is claimed.


## 2026-11-13 — Cache root tactical analysis across MCTS consumers

### Goal and design
- Avoid repeating the same exact root tactical scans when the same MCTS root is used for simulation selection, final move selection and policy-target generation.
- Cache is scoped to one root object and invalidated if its FEN or move history changes. It stores eligible root children and the immediate-mate result; deeper-tree selection is unchanged.

### Changes
- Added per-search root tactical cache fields in src/mcts/search.py.
- Refactored root filtering so the bounded mate-in-two and one-ply mate-avoidance checks run once for a stable root state.
- Reused cached immediate-mate results in both select_action and get_action_probs.
- Added a detector-call-count regression test covering all three MCTS consumers.

### Verification
- Implementation and test revision: c9c19ccaa8554ec34045d2ed436f01ec769f3685.
- CPU workflow [43417951501](https://github.com/Nomusa990822/AlphaZero-Style-Chess-AI-Self-Play-Reinforcement-Learning-with-MCTS-and-Policy-Value-Networks/actions/runs/43417951501): **passed; 145 tests passed in 3.35 seconds** on Python 3.11.
- Stockfish audit [43417951289](https://github.com/Nomusa990822/AlphaZero-Style-Chess-AI-Self-Play-Reinforcement-Learning-with-MCTS-and-Policy-Value-Networks/actions/runs/43417951289): **passed**; all 13 corpus positions supported within the configured tolerance, 0 flagged for human review; audit artifact ID 14032288263.
- The new detector-call-count regression test passed as part of the 145-test suite.
- No checkpoint experiment, training run, measured runtime comparison, playing-strength gain or Elo result is claimed.


## 2026-11-13 — Add bounded static exchange evaluation

### Goal and design
- Introduce a reliable material-exchange calculation as the foundation for hanging-piece and poisoned-capture awareness.
- Follow only legal captures onto the moved piece's destination square. Each side may stop exchanging; promotions and en-passant are accounted for.
- Bound the total recapture nodes. If the budget is exhausted, return None rather than an incomplete numerical score.

### Changes
- Added static_exchange_evaluation to src/mcts/tactics.py.
- Added regression tests for a free queen capture (+900), a poisoned rook capture (-400), en-passant (+100), queen promotion (+800), illegal moves and invalid budgets.
- The helper is not yet wired into MCTS move pruning or prior adjustment. This isolates and validates the exchange calculation before allowing it to influence search.

### Verification
- Implementation/test revision: `274275f7f617cee4b5f55dc959661986426e34b7`.
- CPU test workflow [43418653846](https://github.com/Nomusa990822/AlphaZero-Style-Chess-AI-Self-Play-Reinforcement-Learning-with-MCTS-and-Policy-Networks/actions/runs/43418653846): **passed; 149 tests passed in 3.82 seconds** on Python 3.11.
- Duplicate CPU workflow [43418661520](https://github.com/Nomusa990822/AlphaZero-Style-Chess-AI-Self-Play-Reinforcement-Learning-with-MCTS-and-Policy-Networks/actions/runs/43418661520) also passed: 149 tests in 3.87 seconds.
- Stockfish audit [43418653867](https://github.com/Nomusa990822/AlphaZero-Style-Chess-AI-Self-Play-Reinforcement-Learning-with-MCTS-and-Policy-Networks/actions/runs/43418653867): **passed**; all 13 corpus positions supported, 0 flagged for human review; artifact ID 14032962642. Duplicate audit run [43418661598](https://github.com/Nomusa990822/AlphaZero-Style-Chess-AI-Self-Play-Reinforcement-Learning-with-MCTS-and-Policy-Networks/actions/runs/43418661598) also passed.
- The four new static-exchange regression tests are included in the 149-test suite.
- No checkpoint experiment, training run, measured playing-strength gain or Elo result is claimed.


## 2026-11-13 — Integrate static exchange evaluation into root move priors

### Goal and design
- Let the bounded SEE primitive inform root tactical exploration without hard-pruning legal moves or replacing neural policy priors.
- Apply a conservative, bounded multiplier only to captures and promotions during root expansion. Keep the network prior as the base signal, renormalise the result, and leave any move with an unknown SEE score unchanged.
- Restrict this first integration to the root to avoid imposing SEE recursion cost at every expanded node. Deeper-tree MCTS remains unchanged.

### Changes
- Added the opt-out configuration flag `use_static_exchange_ordering` (enabled by default).
- Added `_apply_static_exchange_prior_bias` in `src/mcts/search.py`. Scores are scaled and clamped to an exponent range of -0.5 to +0.5, limiting the multiplier to approximately 0.61–1.65.
- Applied the adjustment after neural policy conversion and before root expansion/Dirichlet noise.
- Added tests for favourable captures for both White and Black, poisoned captures, preservation of all legal moves, normalised priors, and budget-exhaustion fallback.
- No real checkpoint, training run, runtime comparison or playing-strength experiment was performed.

### Verification
- Implementation/test revision: pending commit and GitHub Actions.
- CPU pytest workflow: pending.
- Stockfish tactical audit: pending.
- Previous verified baseline remains `274275f7f617cee4b5f55dc959661986426e34b7` (149 CPU tests passed; Stockfish audit passed). The new integration must not be described as verified until fresh workflows pass.

### Follow-up
- Inspect CI for this revision, preserve any failures in this log, and repair before updating the verified revision. If verified, next measure the added root expansion cost and use a real checkpoint before making any strength claim.


### Verification — SEE-guided root prior adjustment

- Implementation/test revision: `4fabc4562de186955f909059997ac23b15a0493e`.
- CPU workflow [43419431349](https://github.com/Nomusa990822/AlphaZero-Style-Chess-AI-Self-Play-Reinforcement-Learning-with-MCTS-and-Policy-Value-Networks/actions/runs/43419431349): **passed; 152 tests passed in 2.56 seconds** on Python 3.11.
- Duplicate CPU workflow [43419439368](https://github.com/Nomusa990822/AlphaZero-Style-Chess-AI-Self-Play-Reinforcement-Learning-with-MCTS-and-Policy-Value-Networks/actions/runs/43419439368) also passed.
- Stockfish tactical audit [43419439546](https://github.com/Nomusa990822/AlphaZero-Style-Chess-AI-Self-Play-Reinforcement-Learning-with-MCTS-and-Policy-Value-Networks/actions/runs/43419439546): **passed**; all 13 corpus positions supported within the configured tolerance, 0 flagged for human review; artifact `tactical-engine-audit` ID `14033895065`.
- The CI suite includes the new White/Black favourable-capture, poisoned-capture, legal-move preservation, prior normalisation and unknown-SEE fallback tests.
- These are correctness/compatibility checks, not a real-checkpoint playing-strength experiment. No training, runtime benchmark, Elo result or strength gain is claimed.


## 2026-11-13 — Add controlled SEE root-expansion overhead benchmark

### Goal and design
- Quantify the incremental CPU cost of SEE-guided root expansion before increasing its influence or extending it deeper into the tree.
- Compare otherwise identical root expansions with SEE ordering disabled/enabled. Use deterministic uniform synthetic inference to isolate root policy conversion, SEE adjustment and child creation from neural model inference.
- Exercise a starting position, a simple capture, a defended/poisoned queen capture and promotion choices. Alternate measurement order, include warmups, and report per-position and aggregate median/p95 latency.
- Keep all legal moves, check prior normalisation, preserve input board state, and fail loudly if those invariants break.

### Changes
- Added `scripts/benchmark_see_overhead.py`.
- Added a lightweight test that validates benchmark output structure and scope.
- Updated `.github/workflows/tests.yml` to run the bounded microbenchmark after pytest and upload `see-root-overhead-benchmark` (30-day retention).
- The report records runner/Python details and the tested code revision.
- This excludes trained inference, MCTS simulations and tactical root filtering. It is a microbenchmark, not end-to-end engine speed or playing-strength evidence.

### Verification
- Implementation revision: pending commit and GitHub Actions.
- CPU pytest and benchmark execution: pending.
- Benchmark artifact: pending.
- Prior verified implementation remains `4fabc4562de186955f909059997ac23b15a0493e` (152 CPU tests passed; Stockfish audit passed). This new batch is not yet verified.
- No training, checkpoint experiment, playing-strength gain or Elo result is claimed.


### Failure and repair — benchmark module import

- CPU workflow [43420810604](https://github.com/Nomusa990822/AlphaZero-Style-Chess-AI-Self-Play-Reinforcement-Learning-with-MCTS-and-Policy-Value-Networks/actions/runs/43420810604) on revision `58f460d443fc5619ba4240af43a3c0d21b80cf37`: **153 tests passed in 3.61 seconds**, but the subsequent benchmark step failed with `ModuleNotFoundError: No module named 'src'` because the workflow executed the file path directly.
- The benchmark artifact upload was skipped because the benchmark command failed. The failure is retained; it is not counted as a successful benchmark.
- Repair: changed the workflow invocation to `python -m scripts.benchmark_see_overhead`, ensuring the repository root is on the module import path. This repair requires fresh CPU tests and benchmark artifact verification.


### Benchmark launch failure, repair and successful measurement

- First revision `58f460d443fc5619ba4240af43a3c0d21b80cf37`: CPU runs [43420810604](https://github.com/Nomusa990822/AlphaZero-Style-Chess-AI-Self-Play-Reinforcement-Learning-with-MCTS-and-Policy-Value-Networks/actions/runs/43420810604) and [43420817142](https://github.com/Nomusa990822/AlphaZero-Style-Chess-AI-Self-Play-Reinforcement-Learning-with-MCTS-and-Policy-Value-Networks/actions/runs/43420817142) both passed pytest (153 tests) but failed at the benchmark step with `ModuleNotFoundError: No module named 'src'`. The artifact upload was skipped. These failures are preserved as failures.
- The audit on that implementation revision passed: [43420810302](https://github.com/Nomusa990822/AlphaZero-Style-Chess-AI-Self-Play-Reinforcement-Learning-with-MCTS-and-Policy-Value-Networks/actions/runs/43420810302).
- Repaired workflow invocation to `python -m scripts.benchmark_see_overhead` in `816c4593a7a8ab158dcbe246ed32a388c736b206`.
- CPU workflow [43420960017](https://github.com/Nomusa990822/AlphaZero-Style-Chess-AI-Self-Play-Reinforcement-Learning-with-MCTS-and-Policy-Value-Networks/actions/runs/43420960017): **passed; 153 tests passed in 3.53 seconds**, benchmark ran and artifact `see-root-overhead-benchmark` uploaded (ID `14033642158`). Duplicate CPU run [43420967360](https://github.com/Nomusa990822/AlphaZero-Style-Chess-AI-Self-Play-Reinforcement-Learning-with-MCTS-and-Policy-Value-Networks/actions/runs/43420967360) also passed.
- Stockfish audit [43420959887](https://github.com/Nomusa990822/AlphaZero-Style-Chess-AI-Self-Play-Reinforcement-Learning-with-MCTS-and-Policy-Value-Networks/actions/runs/43420959887): **passed**; 13/13 tactical corpus positions supported, 0 flagged for human review; artifact ID `14033706954`. Duplicate audit [43420967336](https://github.com/Nomusa990822/AlphaZero-Style-Chess-AI-Self-Play-Reinforcement-Learning-with-MCTS-and-Policy-Value-Networks/actions/runs/43420967336) also passed.
- Measured aggregate medians: SEE disabled `0.150311 ms`, enabled `0.245393 ms`, nominal overhead `63.26%`; pooled p95 `0.268644 ms` disabled and `0.365839 ms` enabled.
- Per-position nominal median overhead: starting position `26.83%` (0 capture/promotion candidates), simple capture `27.21%`, poisoned queen capture `46.91%`, promotion choices `69.71%`.
- **Interpretation caution:** each root expansion is sub-millisecond and the starting-position comparison has no SEE candidates, demonstrating that runner noise materially affects these short timings. The result is a preliminary microbenchmark only. Before using the percentage to change defaults, time batches of multiple expansions per sample and repeat on another runner or controlled environment.
- No checkpoint, neural inference, MCTS simulations, training, playing-strength result or Elo measurement was involved.


## 2026-11-13 — Improve SEE overhead benchmark with batched timing

### Motivation and design
- The first benchmark timed individual sub-millisecond root expansions. Its nominal +63.26% aggregate overhead was too sensitive to timer/scheduler noise to guide a default-setting decision.
- Replace single-expansion timing with batches of ten independent root expansions. Prepare boards, search objects and root nodes before starting the timer; time only the expansion calls, then validate every result.
- Use 25 paired batches per position and mode, three warmup batches, and alternating measurement order. Report normalized milliseconds per expansion, batch size, total timed expansions and p95.
- Keep the same four positions and synthetic uniform inference so the benchmark remains focused on the incremental root-expansion cost.

### Changes
- Reworked `scripts/benchmark_see_overhead.py` to time batches and expose a validated `--batch-size` option.
- Strengthened `tests/test_see_overhead_benchmark.py` to verify batch accounting and normalized report fields.
- Updated the CPU workflow to run 25 repeats × 10 expansions per position/mode and upload the JSON report.
- No engine default was changed; this benchmark still excludes neural inference, simulations, tactical root filters and trained checkpoints.

### Verification
- Implementation revision: pending GitHub Actions.
- CPU tests, batched benchmark and artifact upload: pending.
- Stockfish tactical audit: pending.
- Previous verified branch head: `da7fc28f070cf1058b3082c734f1897bcce2765e`; both CPU tests and Stockfish audit passed on that documentation revision (runs `43421210565`, `43421210590`, plus duplicate runs `43421202306`, `43421202305`).
- The initial individual-expansion measurements remain recorded above as preliminary/noisy; they are not replaced or presented as end-to-end engine performance.
- No checkpoint experiment, training run, playing-strength gain or Elo result is claimed.


### Verification — Batched SEE benchmark
- Code revision `bf2ceebe4fe5738c4dc94ea44cf3f06185ad0e9a` passed CPU workflow [43421598036](https://github.com/Nomusa990822/AlphaZero-Style-Chess-AI-Self-Play-Reinforcement-Learning-with-MCTS-and-Policy-Value-Networks/actions/runs/43421598036): **153 passed in 2.78 seconds**. The batch benchmark ran and uploaded artifact ID `14033619165`.
- Stockfish audit [43421598059](https://github.com/Nomusa990822/AlphaZero-Style-Chess-AI-Self-Play-Reinforcement-Learning-with-MCTS-and-Policy-Value-Networks/actions/runs/43421598059) passed; duplicate audit [43421606287](https://github.com/Nomusa990822/AlphaZero-Style-Chess-AI-Self-Play-Reinforcement-Learning-with-MCTS-and-Policy-Networks/actions/runs/43421606287) also passed.
- Batch size 10, 25 paired batches per position/mode, 1,000 timed expansions per mode across four positions.
- Aggregate median per expansion: disabled 0.158494 ms; enabled 0.267257 ms; nominal +68.62%. Pooled p95: disabled 0.321696 ms; enabled 0.414722 ms.
- Position median overhead: starting position +10.19% (zero tactical candidates), simple capture +27.80%, poisoned queen capture +50.10%, promotion choices +68.04%.
- This confirms measurable added work in the synthetic root-expansion path, but does not establish end-to-end slowdown or a reason to disable SEE. Keep default unchanged pending profiling/optimisation and, later, real-checkpoint tests. No training, playing-strength gain or Elo result is claimed.


## 2026-11-13 — Add a no-tactics fast path to SEE root-prior adjustment

### Motivation and change
- The batched benchmark showed a nominal +10.19% median cost even in the starting position, which has no capture or promotion candidates. That cost came from copying and renormalizing the policy-prior dictionary despite there being nothing for SEE to score.
- The root SEE helper now first gathers capture/promotion candidates. If none exist, it returns the already-normalized neural prior dictionary unchanged, avoiding the copy, SEE scoring loop and second normalization.
- Positions with tactical candidates retain the same bounded SEE multipliers, fallback handling, legal-move set and normalization behaviour.
- Added a regression test that forbids any SEE call on a quiet starting position and verifies the original prior dictionary is returned unchanged and remains normalized.

### Verification
- Implementation revision: pending GitHub Actions.
- CPU test suite and batched benchmark: pending.
- Stockfish tactical audit: pending.
- Previous implementation revision `bf2ceebe4fe5738c4dc94ea44cf3f06185ad0e9a`: 153 CPU tests passed in 2.78 seconds; benchmark artifact `14033619165`; Stockfish audit passed.
- No default changed, no training/checkpoint experiment, no playing-strength result or Elo result claimed.


### Verification — SEE quiet-position fast path
- Implementation revision `8124b000aef61645b57fd3f686ef81a13174530d`.
- CPU run [43423373600](https://github.com/Nomusa990822/AlphaZero-Style-Chess-AI-Self-Play-Reinforcement-Learning-with-MCTS-and-Policy-Value-Networks/actions/runs/43423373600): **154 passed in 3.72 seconds**; batched benchmark completed and uploaded artifact ID `14034344758`.
- Duplicate CPU run [43423379443](https://github.com/Nomusa990822/AlphaZero-Style-Chess-AI-Self-Play-Reinforcement-Learning-with-MCTS-and-Policy-Value-Networks/actions/runs/43423379443): passed; **154 passed in 3.22 seconds**; benchmark artifact ID `14034629057`.
- Stockfish audit [43423379514](https://github.com/Nomusa990822/AlphaZero-Style-Chess-AI-Self-Play-Reinforcement-Learning-with-MCTS-and-Policy-Value-Networks/actions/runs/43423379514): passed. Duplicate audit [43423373448](https://github.com/Nomusa990822/AlphaZero-Style-Chess-AI-Self-Play-Reinforcement-Learning-with-MCTS-and-Policy-Networks/actions/runs/43423373448) also passed.
- The quiet-position fast path is covered by a regression test that asserts the SEE evaluator is not called and the original normalized prior dictionary is returned unchanged.
- The concurrent benchmark runs reported differing absolute baselines (including SEE-disabled starting-position medians of 0.410099 ms and 0.263501 ms) and nominal starting-position overhead of 7.54% and 9.15%. Other position overheads remained substantial. Because the paired workflows ran concurrently on shared GitHub-hosted runner capacity, these measurements are not a controlled before/after comparison and do not establish a reliable speedup. Keep the SEE default unchanged; isolate benchmark runs before making performance decisions.
- No checkpoint experiment, training, playing-strength gain or Elo result is claimed.


## 2026-11-13 — Deduplicate push and pull-request CI runs

### Motivation and change
- The feature branch was triggering both push and pull-request workflows. Their concurrency groups used `github.ref`, which differs between a branch push and its pull-request ref, so duplicate jobs could run simultaneously.
- This duplicated CPU/Stockfish work and introduced contention into the batched microbenchmark, making timing comparisons unreliable.
- Updated both CPU-test and tactical-audit concurrency keys to `github.head_ref || github.ref_name`. Pushes and pull-request events for the same source branch now share a concurrency group; newer commits cancel stale in-progress runs for that branch.
- This is a CI scheduling change only; no chess search, SEE scoring, or engine defaults changed.

### Verification
- Workflow configuration change: pending GitHub Actions.
- Previous verified code revision `8124b000aef61645b57fd3f686ef81a13174530d`: 154 CPU tests passed on both CPU runs; both Stockfish audit runs passed.
- Previous benchmark artifacts `14034344758` and `14034629057` were produced by concurrent jobs and are recorded as noisy, not as proof of a performance improvement.


## 2026-11-13 — Verify CI concurrency deduplication and isolated SEE benchmark

### Verification
- Workflow configuration revision: `223b2423eb8980c9d5d080384685cceaf395d735`.
- Push-event CPU run [43423653700](https://github.com/Nomusa990822/AlphaZero-Style-Chess-AI-Self-Play-Reinforcement-Learning-with-MCTS-and-Policy-Value-Networks/actions/runs/43423653700) and push-event tactical audit [43423653471](https://github.com/Nomusa990822/AlphaZero-Style-Chess-AI-Self-Play-Reinforcement-Learning-with-MCTS-and-Policy-Value-Networks/actions/runs/43423653471) were automatically cancelled when the matching pull-request runs entered the shared branch concurrency groups. These are expected duplicate cancellations, not test failures.
- Pull-request CPU run [43423663811](https://github.com/Nomusa990822/AlphaZero-Style-Chess-AI-Self-Play-Reinforcement-Learning-with-MCTS-and-Policy-Value-Networks/actions/runs/43423663811): **154 tests passed in 3.87 seconds** on Python 3.11. The batched SEE benchmark completed and artifact `see-root-overhead-benchmark` uploaded (artifact ID `14035332107`).
- Pull-request Stockfish audit [43423663646](https://github.com/Nomusa990822/AlphaZero-Style-Chess-AI-Self-Play-Reinforcement-Learning-with-MCTS-and-Policy-Value-Networks/actions/runs/43423663646): **passed**; all **13/13** curated positions were supported and **0** were flagged for human review. The audit artifact uploaded (ID `14035351972`).
- The concurrency change therefore prevented the same-commit push and pull-request events from consuming two complete sets of runners. The surviving pull-request workflows verified the branch revision; the push-run cancellations are recorded as part of the history.

### Latest SEE benchmark observations
- With one surviving CPU workflow, the starting-position median was 0.395490 ms/expansion with SEE disabled and 0.422475 ms enabled (**+6.82%** nominal).
- Other per-position nominal overheads were simple capture **+28.76%**, poisoned queen capture **+48.78%**, and promotion **+70.50%**. The aggregate median was 0.220435 ms disabled versus 0.368765 ms enabled (**+67.29%**).
- These are synthetic CPU root-expansion microbenchmarks with uniform inference, not full MCTS throughput or end-to-end move latency. A single isolated run is useful diagnostic evidence but is not sufficient to tune the default. The quiet-position fast path reduces the no-candidate overhead, while tactical candidates still incur SEE work. Keep SEE behavior/defaults unchanged until repeated controlled profiling establishes a robust benefit/cost.
- No real checkpoint, training run, playing-strength improvement or Elo result is claimed.

### Follow-up
- Continue engine correctness and search-quality work; do not spend further CI cycles repeating the same benchmark unless a code change or a controlled profiling question justifies it.


## 2026-11-13 — CI deduplication verification and tactical-cache configuration fix

### CI verification for the preceding documentation revision
- Documentation revision `b06b5df954156620e9824c89cce3b152d8308a31` passed CPU workflow [43423960670](https://github.com/Nomusa990822/AlphaZero-Style-Chess-AI-Self-Play-Reinforcement-Learning-with-MCTS-and-Policy-Value-Networks/actions/runs/43423960670): **154 tests passed in 2.74 seconds**; the batched SEE benchmark completed and artifact `see-root-overhead-benchmark` uploaded (ID `14035481672`).
- Stockfish audit [43423960833](https://github.com/Nomusa990822/AlphaZero-Style-Chess-AI-Self-Play-Reinforcement-Learning-with-MCTS-and-Policy-Value-Networks/actions/runs/43423960833) passed. The prior revision's 13/13 tactical-corpus result remains the measured audit summary.
- The matching push-event runs [43423953162](https://github.com/Nomusa990822/AlphaZero-Style-Chess-AI-Self-Play-Reinforcement-Learning-with-MCTS-and-Policy-Value-Networks/actions/runs/43423953162) and [43423953259](https://github.com/Nomusa990822/AlphaZero-Style-Chess-AI-Self-Play-Reinforcement-Learning-with-MCTS-and-Policy-Value-Networks/actions/runs/43423953259) were cancelled in favour of pull-request workflows, confirming shared concurrency groups work as intended.

### New cache correctness change — verification pending
- Found that `_root_children_for_action` cached candidates by root object, FEN and move history but omitted the mutable `use_tactical_root_filter` configuration flag.
- If a caller toggled that flag on an existing MCTS instance, the old candidate set and cached mate-in-one list could be reused under the new setting. This could incorrectly keep tactical filtering active after it was disabled, or skip it after re-enabling.
- Added the configuration flag to the cache key. The same root now triggers recomputation whenever the tactical-filter setting changes; repeated calls with unchanged position/history/config still reuse the cached result.
- Added a regression test that enables, disables and re-enables the filter on the same root, checking both eligible-child sets and the mate-in-one cache.
- This is a correctness/cache-invalidation fix only. No search-strength, speed, training or Elo improvement is claimed.
- CPU tests and Stockfish audit are pending for the implementation revision. Preserve any failures and only mark it verified after completed successful workflows.



## 2026-11-13 — Tactical-root cache verification and mate-policy consistency fix

### Verified cache invalidation revision
- Implementation revision: `1c2d4e472496c3080fd7df9e188bfa504b635d49`.
- CPU workflow [43424484996](https://github.com/Nomusa990822/AlphaZero-Style-Chess-AI-Self-Play-Reinforcement-Learning-with-MCTS-and-Policy-Value-Networks/actions/runs/43424484996): **155 tests passed in 4.98 seconds** on Python 3.11. The batched SEE benchmark completed and artifact `see-root-overhead-benchmark` uploaded (ID `14036345110`).
- Aggregate SEE benchmark: disabled median **0.297020 ms/expansion**, enabled median **0.486085 ms/expansion**, nominal overhead **+63.65%**. This is a synthetic root-expansion microbenchmark with uniform inference, not end-to-end search speed or playing strength.
- Stockfish tactical audit [43424485735](https://github.com/Nomusa990822/AlphaZero-Style-Chess-AI-Self-Play-Reinforcement-Learning-with-MCTS-and-Policy-Value-Networks/actions/runs/43424485735): **13/13** curated positions supported, **0** flagged for human review; artifact ID `14036055893`.
- Duplicate push-event runs [43424476585](https://github.com/Nomusa990822/AlphaZero-Style-Chess-AI-Self-Play-Reinforcement-Learning-with-MCTS-and-Policy-Value-Networks/actions/runs/43424476585) and [43424476487](https://github.com/Nomusa990822/AlphaZero-Style-Chess-AI-Self-Play-Reinforcement-Learning-with-MCTS-and-Policy-Value-Networks/actions/runs/43424476487) were cancelled by the shared concurrency groups; the pull-request runs above completed successfully.
- This verifies the cache-key configuration fix. No training, checkpoint evaluation, Elo or playing-strength experiment was run.

### New correctness issue — verification pending
- Review found a mismatch in the immediate-mate override: `get_action_probs` assigned equal probability to every mate-in-one move, but `select_action` always chose the first mate, even at positive temperature. At zero temperature, the policy target also remained uniform although action selection was deterministic.
- This made the recorded self-play policy target inconsistent with the actual move-selection distribution in positions with multiple mating moves.
- Updated action selection to sample uniformly among cached mating moves at positive temperature and select the first move at effectively zero temperature. Updated policy-target generation to use the matching uniform or one-hot distribution.
- Added a regression test covering positive-temperature sampling and zero-temperature deterministic selection against the corresponding full action-space targets.
- This is a self-play/search-policy consistency correction. It does not establish a playing-strength improvement.
- CPU tests and Stockfish audit are pending for the new implementation revision.


## 2026-11-13 — Multi-ply tactical-combination benchmark foundation (verification pending)

- Added a separate JSONL schema for curated multi-ply tactical combinations, preserving the original 13 single-position cases unchanged.
- Added validation for motif combinations, game phase, legal moves at every ply, annotations, unique IDs and non-terminal continuation.
- Added a sequence evaluator that reports complete-line success, per-ply accuracy, colour/phase breakdowns and the first missed ply.
- Added two illustrative three-ply combinations: a checking knight fork followed by a queen capture, and a discovered check followed by a queen capture.
- Added `evaluate_tactical_sequences.py` to run the same deterministic MCTS/checkpoint evaluation path on the sequence corpus. Its report explicitly states that this is principal-variation line-following, not proof that the line is forced against every defence.
- Added tests for legal line replay, full sequence success, first-missed-ply reporting and invalid sequence data.
- No model training, checkpoint evaluation, Elo claim or strength improvement is asserted. CI verification is pending.


### First CI verification attempt for multi-ply tactical-combination benchmark
- Implementation commit `cda8fb2e4a2b0a37e4a31d7e0f68460b42fff622` CPU run [43426943254](https://github.com/Nomusa990822/AlphaZero-Style-Chess-AI-Self-Play-Reinforcement-Learning-with-MCTS-and-Policy-Value-Networks/actions/runs/43426943254): **2 failed, 158 passed**. The failures were test-fixture expectation mistakes: one intended a legal but unaccepted move but supplied an illegal move; the other intended to test an illegal annotation but used an invalid starting board. The other 158 tests passed.
- Stockfish audit [43426943127](https://github.com/Nomusa990822/AlphaZero-Style-Chess-AI-Self-Play-Reinforcement-Learning-with-MCTS-and-Policy-Value-Networks/actions/runs/43426943127): original corpus **13/13 supported, 0 flagged**, artifact `14038596188`. The original corpus was not changed.
- Corrected the test fixtures in commit `b10ce6b6faefc2a5ae6351817dc9afc639b81755`. The failed run remains part of the record; re-verification is pending.


### Corrected tactical-sequence benchmark — verified
- Verified revision `d1f33d1920c2cb909dbad20405a296544acf9c54` (includes the fixture correction and the recorded initial failure).
- CPU workflow [43427256968](https://github.com/Nomusa990822/AlphaZero-Style-Chess-AI-Self-Play-Reinforcement-Learning-with-MCTS-and-Policy-Value-Networks/actions/runs/43427256968): **160 passed in 3.30 seconds**. The SEE microbenchmark completed and artifact `14038486847` was uploaded. Aggregate median SEE overhead was **+67.96%** in this synthetic root-expansion benchmark; this is not end-to-end search speed or playing strength.
- Stockfish audit [43427256921](https://github.com/Nomusa990822/AlphaZero-Style-Chess-AI-Self-Play-Reinforcement-Learning-with-MCTS-and-Policy-Value-Networks/actions/runs/43427256921): original corpus **13/13 supported, 0 flagged**, artifact `14038297049`. This remains a finite-depth review, not proof of correctness.
- Push-event runs [43427253170](https://github.com/Nomusa990822/AlphaZero-Style-Chess-AI-Self-Play-Reinforcement-Learning-with-MCTS-and-Policy-Value-Networks/actions/runs/43427253170) and [43427253316](https://github.com/Nomusa990822/AlphaZero-Style-Chess-AI-Self-Play-Reinforcement-Learning-with-MCTS-and-Policy-Value-Networks/actions/runs/43427253316) were cancelled by the shared concurrency groups in favour of the matching pull-request runs. Earlier duplicate push runs [43427220854](https://github.com/Nomusa990822/AlphaZero-Style-Chess-AI-Self-Play-Reinforcement-Learning-with-MCTS-and-Policy-Value-Networks/actions/runs/43427220854) and [43427220881](https://github.com/Nomusa990822/AlphaZero-Style-Chess-AI-Self-Play-Reinforcement-Learning-with-MCTS-and-Policy-Value-Networks/actions/runs/43427220881) and the superseded PR CPU run [43427228054](https://github.com/Nomusa990822/AlphaZero-Style-Chess-AI-Self-Play-Reinforcement-Learning-with-MCTS-and-Policy-Value-Networks/actions/runs/43427228054) were also cancelled as duplicate/superseded runs, not test failures.
- The sequence metric is explicitly annotated principal-variation line-following. It does not prove the line is forced against all defences. No checkpoint was evaluated, no training was run, and no Elo or playing-strength improvement is claimed.


## 2026-11-13 — Stockfish audit extended to tactical combinations

- Extended `scripts/audit_tactical_corpus.py` to review every annotated ply in each multi-motif sequence, following the canonical principal variation. Reports now include sequence-level support, flagged sequences and supported/flagged plies alongside the original single-position audit.
- Added `tests/test_tactical_sequence_audit.py` to verify that each annotated ply is audited on the correct replayed board.
- Corrected sequence-benchmark implementation and audit verified on revision `2944ad7326880e7a020219c2652b33525df20c5a`.
- CPU workflow [43427628807](https://github.com/Nomusa990822/AlphaZero-Style-Chess-AI-Self-Play-Reinforcement-Learning-with-MCTS-and-Policy-Value-Networks/actions/runs/43427628807): **161 passed in 3.99 seconds**; SEE microbenchmark completed. Aggregate median overhead **+67.25%** in the synthetic root-expansion benchmark; not an end-to-end speed or strength result.
- Stockfish audit [43427628961](https://github.com/Nomusa990822/AlphaZero-Style-Chess-AI-Self-Play-Reinforcement-Learning-with-MCTS-and-Policy-Value-Networks/actions/runs/43427628961): **13/13** single positions supported, **0** flagged; **2/2** tactical sequences supported, **0** flagged; **6/6** sequence plies supported. Audit artifact `14037203389`.
- Duplicate push runs [43427623653](https://github.com/Nomusa990822/AlphaZero-Style-Chess-AI-Self-Play-Reinforcement-Learning-with-MCTS-and-Policy-Value-Networks/actions/runs/43427623653) and [43427623672](https://github.com/Nomusa990822/AlphaZero-Style-Chess-AI-Self-Play-Reinforcement-Learning-with-MCTS-and-Policy-Value-Networks/actions/runs/43427623672) were cancelled in favour of the matching PR runs; expected concurrency behaviour, not failures.
- The two combinations are illustrative annotated lines. Stockfish support at finite depth does not prove every defence is forced or validate every human motif label. No checkpoint was evaluated and no training, Elo or playing-strength claim was made.

### In progress — first verified-source deflection corpus addition (2026-11-13)
- Added one Black-to-move deflection candidate from the Chess Tempo tactical-motifs example: the bishop check on d4 draws the white queen away from f1, allowing a mating finish.
- Added a semantic test for the checking bishop sacrifice, queen capture and mating continuation; expanded corpus motif and colour-count assertions from 14 positions (White 8 / Black 6) to 15 (White 8 / Black 7).
- This is a one-position controlled addition, not the previously planned eight-position batch. Further positions will be added only when their FEN, legal continuation and tactical idea can be validated.
- CPU tests and Stockfish audit are pending. No training or checkpoint evaluation was run.



### Deflection corpus addition — CI verified (2026-11-13)
- Corrected revision: `7bdf9bb25b96ae003a8c3f75f5f4d67a6c97db3e` (the semantic assertion correction is included).
- The first replacement attempts on the earlier commit `e7725e0` were cancelled; their reruns later completed successfully, but those results alone did not verify the corrected assertion.
- Corrected-head CPU workflow [43429806549](https://github.com/Nomusa990822/AlphaZero-Style-Chess-AI-Self-Play-Reinforcement-Learning-with-MCTS-and-Policy-Value-Networks/actions/runs/43429806549): **163 passed in 4.29 seconds**. SEE microbenchmark artifact `14039481148`; synthetic root-expansion aggregate median overhead **+63.24%** (0.270415 ms disabled / 0.441425 ms enabled). This is a synthetic microbenchmark, not end-to-end search speed or playing strength.
- Corrected-head Stockfish audit [43429806151](https://github.com/Nomusa990822/AlphaZero-Style-Chess-AI-Self-Play-Reinforcement-Learning-with-MCTS-and-Policy-Value-Networks/actions/runs/43429806151): **15/15 individual positions supported, 0 flagged; 2/2 sequences supported, 6/6 annotated plies supported, 0 flagged**. Audit artifact `14038701315`.
- Earlier cancelled attempts [43429753749](https://github.com/Nomusa990822/AlphaZero-Style-Chess-AI-Self-Play-Reinforcement-Learning-with-MCTS-and-Policy-Value-Networks/actions/runs/43429753749), [43429753847](https://github.com/Nomusa990822/AlphaZero-Style-Chess-AI-Self-Play-Reinforcement-Learning-with-MCTS-and-Policy-Value-Networks/actions/runs/43429753847), [43429795529](https://github.com/Nomusa990822/AlphaZero-Style-Chess-AI-Self-Play-Reinforcement-Learning-with-MCTS-and-Policy-Value-Networks/actions/runs/43429795529), and [43429795629](https://github.com/Nomusa990822/AlphaZero-Style-Chess-AI-Self-Play-Reinforcement-Learning-with-MCTS-and-Policy-Value-Networks/actions/runs/43429795629) remain recorded as cancelled/superseded, not test failures.
- The Stockfish audit is finite-depth support for at least one accepted move per position; it is not proof that all alternatives or every defence have been exhaustively validated. No model training or checkpoint evaluation was run; no Elo or playing-strength improvement is claimed.


### Decoy motif corpus expansion — verification pending (2026-11-13)
- Added one White-to-move queen-sacrifice decoy candidate based on the published Chess Tempo motif example: `Qxh7+` attracts the black king to h7, followed by `Rh5#`.
- Added semantic regression for the queen sacrifice, king capture and mating rook continuation; expanded the expected corpus to 16 positions (White 9 / Black 7) and required motifs to include `decoy`.
- CPU tests and Stockfish audit are pending for this candidate. It is not counted as verified until both workflows complete on the same revision.
- The prior Black deflection addition remains verified on `7bdf9bb`: 163 CPU tests passed and Stockfish supported all 15 positions.
- No training or checkpoint evaluation was run.
