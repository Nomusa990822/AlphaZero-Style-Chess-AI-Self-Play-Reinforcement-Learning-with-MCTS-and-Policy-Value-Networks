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
