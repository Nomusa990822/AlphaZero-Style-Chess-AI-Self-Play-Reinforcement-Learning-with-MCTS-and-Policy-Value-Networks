# Project Status

**Project:** AlphaZero-Style Chess AI  
**Status:** Active research and engineering  
**Default branch:** `main`  
**Latest main revision at this snapshot:** `560163afe1050a2a4fc18fd30b320d06969b2242` (2026-11-14; baseline recovery PR #26)

## Current verified state

The implementation includes a 20-plane board encoder, 4,672-action move representation, residual policy-value network, PUCT MCTS, self-play, replay persistence, candidate training/evaluation, checkpoint management, tactical-root safeguards, a tactical benchmark runner, and a resource-bounded search-configuration sweep.

The current curated tactical corpora contain **35 positions** (19 White-to-move, 16 Black-to-move) and **11 annotated sequences / 37 plies**. The latest defensive-countercheck semantic-test revision passed **189 CPU tests** and the Stockfish audit supported **35/35 positions and 11/11 sequences / 37/37 plies with zero flagged entries**. See the linked workflow records in [DEVELOPMENT_LOG.md](DEVELOPMENT_LOG.md) and [benchmarks/README.md](../benchmarks/README.md).

## Training and checkpoint state

A bounded fresh-start CPU pipeline pilot **was executed successfully** on 2026-11-13 (workflow [43497298757](https://github.com/Nomusa990822/AlphaZero-Style-Chess-AI-Self-Play-Reinforcement-Learning-with-MCTS-and-Policy-Value-Networks/actions/runs/43497298757)). It completed one iteration, four self-play games, 274 positions, one training epoch, and two colour-swapped candidate-evaluation games. Both evaluation games were draws (score 0.50); the candidate was **not promoted**. The pilot validated the pipeline and backup process; it did not establish playing strength or Elo.

The baseline checkpoint remains the selected model:
- `best_model.pt`, epoch 0; SHA-256 `7a9fdacbd14f6423e34b2edb470d255e15081a12b1e66faf204a5e07e24e4471`.
- Candidate `latest_candidate.pt`, epoch 1; SHA-256 `3b471702e89659307f11ec95b3f83316ccae7c29a4c7d9d6faa7afaa4f7231a7`; retained separately and not promoted.

Both checkpoints and their manifest are preserved in the durable prerelease [fresh-pilot-checkpoint-43497298757-1](https://github.com/Nomusa990822/AlphaZero-Style-Chess-AI-Self-Play-Reinforcement-Learning-with-MCTS-and-Policy-Value-Networks/releases/tag/fresh-pilot-checkpoint-43497298757-1). The release contains `best_model.pt`, `latest_candidate.pt`, and `fresh-pilot-checkpoint-manifest.json`. The corresponding Actions artifact [14071428532](https://github.com/Nomusa990822/AlphaZero-Style-Chess-AI-Self-Play-Reinforcement-Learning-with-MCTS-and-Policy-Value-Networks/actions/runs/43497298757) also preserves replay data and logs.

The normal `.github/workflows/train-and-backup.yml` workflow is **resume-only** and requires the user to select confirm_training=YES. PR #26 merged the safe recovery step: on a clean checkout it downloads the immutable epoch-0 baseline from the durable prerelease, verifies SHA-256 7a9fdacbd14f6423e34b2edb470d255e15081a12b1e66faf204a5e07e24e4471, and installs it only if no non-empty best checkpoint exists. Existing champions are never overwritten by recovery. No training was dispatched by that change.

## Tactical checkpoint evaluation

The pilot baseline and candidate were later evaluated on the earlier tactical corpus at 100 MCTS simulations:
- Individual positions: baseline 4/22 (18.18%); candidate 5/22 (22.73%).
- Annotated sequences: both 3/7 plies (42.86%) and 1/5 complete lines (20%).
- Neither checkpoint made an illegal move in either diagnostic.

The small curated corpus and prescribed sequence lines do not measure general playing strength. The candidate's one-position difference is insufficient evidence for promotion. Full details and checkpoint identities are in [EXPERIMENT_LOG.md](EXPERIMENT_LOG.md).

## Current limitations

- No reliable Elo or general playing-strength rating has been established.
- The pilot's two-game promotion evaluation is far too small for a strength conclusion.
- Tactical positions and annotated principal variations are curated diagnostics, not comprehensive tactical coverage or forced-line proofs.
- The Black-to-move counterpart for the knight double-attack motif was removed after repeated Stockfish rejection; colour-balanced coverage for that motif is not claimed.
- Real-checkpoint MCTS ablation and search-configuration sweeps remain to be run against the recovered baseline.
- The tracked tree does not contain model weights; binary checkpoints remain in the release backup and must be restored locally/into the workflow checkout when needed.

## Prioritised next steps

1. Restore the baseline through the hash-verified recovery workflow and retain an independent copy.
2. Run checkpoint integrity/metadata diagnostics and the fixed tactical-position and sequence benchmarks on the current 35-position / 11-sequence corpora. Preserve raw JSON reports and checkpoint hash.
3. Run the paired tactical-root-filter ablation and resource-bounded search sweep with the same checkpoint, CPU device, corpus and declared simulation budget.
4. Design the next staged training schedule only after baseline diagnostics; preserve the baseline and candidate separately.
5. Use the incumbent-relative promotion gate for every candidate and establish a repeatable fixed-opponent match protocol before making strength claims.

## Verification and documentation protocol

- Latest main snapshot: `68cf3a4e2e40aa7b3f92fd5b5d430c6d7a6ddbf8`.
- Latest semantic regression CI: CPU [43641897416](https://github.com/Nomusa990822/AlphaZero-Style-Chess-AI-Self-Play-Reinforcement-Learning-with-MCTS-and-Policy-Value-Networks/actions/runs/43641897416), **189 passed**.
- Latest tactical audit: [43641897417](https://github.com/Nomusa990822/AlphaZero-Style-Chess-AI-Self-Play-Reinforcement-Learning-with-MCTS-and-Policy-Value-Networks/actions/runs/43641897417), **35/35 positions and 11/11 sequences / 37/37 plies supported; zero flagged**, artifact [14132283194](https://github.com/Nomusa990822/AlphaZero-Style-Chess-AI-Self-Play-Reinforcement-Learning-with-MCTS-and-Policy-Value-Networks/actions/runs/43641897417).
- Update `README.md`, `benchmarks/README.md`, this status file and `DEVELOPMENT_LOG.md` with each meaningful engineering batch.
- Add entries to `EXPERIMENT_LOG.md` only when an actual training or benchmark experiment runs.
- Record exact revisions, workflow links, failures and repairs. Never replace unknown data with estimates.


## Baseline restoration automation — merged

PR #26 merged at 560163afe1050a2a4fc18fd30b320d06969b2242. The manual resume
workflow restores the immutable epoch-0 baseline only when best_model.pt is
missing or empty, verifies the pinned SHA-256 before installation, and never
overwrites a non-empty champion checkpoint. The confirm_training=YES gate
remains mandatory. No training was dispatched by the recovery change.


## Incumbent-relative model promotion policy

A candidate is evaluated directly against the currently promoted champion. Its
match score is relative to that opponent: win = 1, draw = 0.5, loss = 0.
It is not an absolute model-quality score and must not be compared with scores
from unrelated opponents or separate evaluation protocols.

Promotion has no arbitrary 0.55 cutoff. A candidate is promoted only when **all**
of these checks pass:

1. At least 24 games are completed.
2. Games are colour-balanced (an even number, with each model playing both
   colours equally) and use deterministic MCTS without exploration noise.
3. The candidate's match score is strictly greater than 0.50, meaning it
   outscored the current champion.
4. The one-sided 90% lower confidence bound is also strictly greater than
   0.50, providing evidence that the advantage is not just a small-sample
   fluctuation.
5. Every move returned by either evaluator agent is legal. An illegal move
   aborts evaluation; it is never counted as a win or silently ignored.

If any condition fails, the current champion and its checkpoint are preserved.
The newly trained candidate remains separately available as latest_candidate.
The two-game smoke pilot is therefore never eligible for promotion. Every new
candidate is compared with whichever champion is currently selected at that
iteration, so the standard is relative to the best model already retained.


## Latest training state — first full run completed (2026-11-15)

The first full training run [43646981876](https://github.com/Nomusa990822/AlphaZero-Style-Chess-AI-Self-Play-Reinforcement-Learning-with-MCTS-and-Policy-Value-Networks/actions/runs/43646981876) completed successfully from `43999a6cdaa57777a9a02f25967a9cdb42eced16`. It ran two iterations, 80 self-play games, 20 epochs and 48 incumbent evaluation games. Iteration 1 candidate score was 0.250 (90% lower confidence bound 0.164); iteration 2 score was 0.000 (lower bound 0.000). Both were rejected. The epoch-0 incumbent remains unchanged and selected (SHA-256 `7a9fdacbd14f6423e34b2edb470d255e15081a12b1e66faf204a5e07e24e4471`). The final candidate is preserved separately (SHA-256 `101294ee17c79fd9e4816b3e2676b8f87487c4932172861f59b96550c345af00`). Artifact [14139456844](https://github.com/Nomusa990822/AlphaZero-Style-Chess-AI-Self-Play-Reinforcement-Learning-with-MCTS-and-Policy-Value-Networks/actions/runs/43646981876/artifacts/14139456844) and durable [checkpoint prerelease](https://github.com/Nomusa990822/AlphaZero-Style-Chess-AI-Self-Play-Reinforcement-Learning-with-MCTS-and-Policy-Value-Networks/releases/tag/model-checkpoint-43646981876-1) preserve the outputs. Full measured details are in [EXPERIMENT_LOG.md](EXPERIMENT_LOG.md). No Elo or general playing-strength claim is made.

The first reproducible baseline tactical diagnostic [43645701877](https://github.com/Nomusa990822/AlphaZero-Style-Chess-AI-Self-Play-Reinforcement-Learning-with-MCTS-and-Policy-Value-Networks/actions/runs/43645701877) was completed before training. Its 35-position results were 5/35 baseline and 10/35 pilot candidate; sequence ply accuracy was 3/13 and 5/15 respectively, with one complete sequence each and zero illegal moves. These are curated tactical diagnostics, not playing-strength ratings.

## Updated priorities

1. Preserve the immutable epoch-0 incumbent and final rejected candidate independently.
2. Inspect training data quality, self-play behaviour, candidate-versus-incumbent match protocol and model optimisation before another full run.
3. Add diagnostic evidence that can explain the poor head-to-head results; do not relax the promotion criteria.
4. Continue to record exact run IDs, checkpoint hashes, artifacts and measured outcomes in the experiment and development logs.


## Evaluation protocol correction and checkpoint postmortem tooling

A code review of the first full training run found that the previous promotion evaluator replayed the same standard-start game for every repeated colour assignment: deterministic MCTS, zero Dirichlet noise, zero move temperature and a fixed starting board yielded only two distinct game paths across 24 nominal games. The resulting game-level confidence bound treated repeated paths as independent and overstated the evidence. The old 0-24 result remains a valid observation that the candidate lost both colour assignments from the standard start, but it is not a 24-independent-game strength estimate.

The corrected evaluator uses 12 distinct, version-controlled opening positions, each played twice: candidate as White from the supplied opening and candidate as Black from its mirrored position. It reports candidate outcomes separately by colour and calculates the one-sided 90% lower confidence bound over the 12 opening-pair scores. Promotion still requires 24 games, 12 opening pairs, score strictly above 0.50 and paired lower confidence bound strictly above 0.50. It does not relax the promotion threshold.

The first full-run checkpoint metadata also confirms that the selected epoch-0 checkpoint was a random-initialisation baseline. The pipeline copied that incumbent afresh for each rejected candidate, rather than continuing from the previous rejected candidate; iteration 2 therefore did not continue the iteration-1 weights. The 80 self-play games were generated by the untrained incumbent. These are confirmed cold-start/data-quality limitations, not evidence that checkpoint integrity or backup failed.

A read-only workflow, [Checkpoint run postmortem diagnostics](.github/workflows/checkpoint-run-postmortem.yml), downloads a selected training-run artifact, verifies both checkpoint hashes against its manifest, runs the corrected paired-opening match, and records policy/value/MCTS plus tactical-position and sequence diagnostics. Default target run: [43646981876](https://github.com/Nomusa990822/AlphaZero-Style-Chess-AI-Self-Play-Reinforcement-Learning-with-MCTS-and-Policy-Value-Networks/actions/runs/43646981876). No training, checkpoint write, or promotion is performed by this diagnostic workflow.


## Paired-opening promotion evaluation

The deterministic standard-start match protocol was corrected: repeating the same deterministic game 12 times per colour does not create 24 distinct observations. The new protocol uses 12 fixed, distinct opening positions, plays each in both mirrored colour assignments, reports outcomes by candidate colour, and calculates the approximate lower confidence bound across the 12 opening-pair scores. This remains a fixed-suite comparison, not an Elo estimate. The read-only [checkpoint postmortem workflow](.github/workflows/checkpoint-run-postmortem.yml) evaluates preserved run artifacts without training or modifying checkpoints.


### Additional self-play diagnostic from workflow 43646981876

The 80 self-play games produced 15 White wins, 32 Black wins and 33 draws; four draws ended at the 250-ply cap. Iteration 1 was White 8 / Black 16 / Draw 16 (three move-cap draws); iteration 2 was White 7 / Black 16 / Draw 17 (one move-cap draw). This pronounced colour imbalance is a diagnostic signal to investigate, not proof of an encoder or search bug: only 80 games were played and every game began from the standard position. The previous evaluator did not preserve individual PGNs or per-colour match results, so its 0-24 candidate score cannot be decomposed beyond the two repeated standard-start colour assignments.


## Completed postmortem of full training run 43646981876

The read-only postmortem [43662614909](https://github.com/Nomusa990822/AlphaZero-Style-Chess-AI-Self-Play-Reinforcement-Learning-with-MCTS-and-Policy-Value-Networks/actions/runs/43662614909) completed successfully on 2026-11-15. Checkpoint hashes were verified and all six JSON reports were uploaded in artifact [14141986519](https://github.com/Nomusa990822/AlphaZero-Style-Chess-AI-Self-Play-Reinforcement-Learning-with-MCTS-and-Policy-Value-Networks/actions/runs/43662614909/artifacts/14141986519) (23,281 bytes; SHA-256 03a211d6465bc026a681e4ed42352c29f33539bce75b8cb973050a8ba3d246ec). No training, checkpoint mutation or promotion occurred.

- **Paired opening suite:** 24 games / 12 mirrored opening pairs; candidate epoch 10 scored 0.500 (1 win, 1 loss, 22 draws); one-sided 90% paired lower bound 0.4494. Candidate-as-White: 0 wins, 12 draws; candidate-as-Black: 1 win, 1 loss, 10 draws. Promotion correctly rejected.
- **35-position tactical benchmark:** baseline 6/35 (17.14%) versus candidate 8/35 (22.86%) at 25 MCTS simulations; policy top-1 1/35 versus 3/35. Zero illegal moves for both. The MCTS increase came from White-to-move positions (3/19 to 5/19); Black remained 3/16. Endgame accuracy moved 1/7 to 3/7; middlegame remained 5/28.
- **11 annotated sequences / 13 attempted plies:** both checkpoints 3/13 (23.08%) and 1/11 completed sequences (9.09%); zero illegal moves.

The candidate therefore has a modest fixed-corpus position/policy signal but no head-to-head advantage and no sequence improvement. These small curated diagnostics do not establish general playing strength or Elo. The epoch-0 baseline remains the selected checkpoint; epoch-10 remains unpromoted.

## Revised priorities after postmortem

1. Diagnose the White/Black asymmetry and weak sequence performance using targeted, controlled evaluation before changing training code.
2. Review policy/value calibration and MCTS decision traces on the 35-position corpus; distinguish policy ranking errors from search-selection errors.
3. Resolve the cold-start iteration issue in a documented design proposal, preserving incumbent/candidate separation and the promotion gate.
4. Do not start another full training run or promote the candidate until these diagnostics produce a controlled corrective plan.
5. Keep the immutable baseline and rejected candidate separately preserved; use the postmortem artifact as the raw evidence source.


## Diagnostic investigation in progress — colour symmetry and candidate lifecycle

The completed postmortem does not establish a model colour bug. The 80 self-play games had 32 Black wins, 15 White wins and 33 draws, but all began from the standard position. The corrected candidate-versus-incumbent suite was level overall (1 win, 1 loss, 22 draws), with 12 draws when the candidate played White and 1 win / 1 loss / 10 draws when it played Black. The tactical corpus is also not perfectly balanced (19 White-to-move, 16 Black-to-move): candidate MCTS accuracy was 5/19 White versus 3/16 Black, while the baseline was 3/19 White and 3/16 Black. This small sample is insufficient to attribute the difference to the encoder or search.

The checkpoint behaviour report shows candidate mean raw side-to-move value +0.134 (range -0.699 to +0.800), compared with baseline mean -0.004 (range -0.215 to +0.250). These are unlabelled tactical-position predictions; there is no held-out outcome set in this run, so this is not a calibration result. The policy top-1 diagnostic improved only from 1/35 to 3/35, and the 11-sequence benchmark remained unchanged at 3/13 attempted plies and 1/11 completed sequences.

Source review confirms the current iteration lifecycle: each iteration generates self-play from `best_model`, clones `best_model` into a new candidate, creates a fresh Adam optimizer, and trains that candidate on the accumulated replay buffer. If promotion is rejected, `best_model` remains unchanged; the next iteration therefore starts from the same incumbent weights and a new optimizer. The replay buffer grows, but the rejected candidate weights and its optimizer state are not carried forward. The trainer currently reports training loss only; it has no held-out validation split. This is confirmed implementation behaviour, not yet a decision to change the algorithm.

A read-only [checkpoint colour symmetry audit](.github/workflows/checkpoint-colour-symmetry-audit.yml) has been added. It will compare each checkpoint on 35 positions and their colour-swapped mirrors (policy distribution divergence, top-1/MCTS move equivariance, raw-value symmetry), then play each checkpoint against itself over 12 mirrored opening pairs. It verifies the preserved checkpoint hashes and does not train, write checkpoints or promote a model. Run it only after the PR is merged; keep full training paused until its results and a held-out validation design have been reviewed.


## Completed colour-symmetry audit — workflow 43745391998

The read-only [checkpoint colour-symmetry audit](https://github.com/Nomusa990822/AlphaZero-Style-Chess-AI-Self-Play-Reinforcement-Learning-with-MCTS-and-Policy-Value-Networks/actions/runs/43745391998) completed successfully on 2026-11-15. Checkpoint hashes were verified before evaluation. Artifact [14174652293](https://github.com/Nomusa990822/AlphaZero-Style-Chess-AI-Self-Play-Reinforcement-Learning-with-MCTS-and-Policy-Value-Networks/actions/runs/43745391998/artifacts/14174652293) contains the raw JSON report (8,742 bytes; ZIP SHA-256 `305eb50dd0aaea02c8bd064c2376ac00f40a084f0e10a3d52ad09eb2af6ad87f`). The run was read-only: no training, checkpoint modification or promotion occurred.

- **Checkpoint identity:** baseline epoch 0 SHA-256 `7a9fdacbd14f6423e34b2edb470d255e15081a12b1e66faf204a5e07e24e4471`; candidate epoch 10 SHA-256 `101294ee17c79fd9e4816b3e2676b8f87487c4932172861f59b96550c345af00`.
- **Mirrored policy/MCTS consistency (35 pairs):** baseline policy top-1 mirror agreement 4/35 (11.43%), MCTS agreement 8/35 (22.86%), mean legal-policy JSD 0.3112 nats. Candidate policy top-1 agreement 1/35 (2.86%), MCTS agreement 6/35 (17.14%), mean JSD 0.4017 nats. The candidate is less mirror-consistent on all three measures, despite its previously observed small tactical-position score increase.
- **Value symmetry:** training targets are explicitly defined from the side-to-move player's perspective. Therefore a position and its colour-swapped vertical mirror should have approximately the same value. Mean absolute raw-value difference was 0.0737 for the baseline and 0.7930 for the candidate (maximum candidate difference 1.4619). This is a pronounced candidate inconsistency and a priority diagnostic signal; it is not value calibration and does not by itself identify whether the cause is training data, model learning, encoding or another implementation issue.
- **Same-checkpoint self-play (24 games / 12 opening pairs):** baseline recorded 1 win, 0 losses and 23 draws (score 0.5208); as White 1-0-11, as Black 0-0-12. Candidate recorded 8 wins, 5 losses and 11 draws (score 0.5625); as White 2-3-7, as Black 6-2-4. Because the same checkpoint controls both colours, this is a colour/mirror consistency diagnostic, not a strength comparison. The sample is small and opening-suite specific.

**Assessment:** the epoch-10 candidate's mirror agreement is materially worse than the epoch-0 baseline, especially for value predictions and policy top-1. The same-checkpoint games also show a colour-dependent outcome pattern for the candidate. This supports investigating colour-perspective consistency before any further training. It does not prove a specific encoder/search defect. Keep the epoch-0 baseline selected, retain the candidate unpromoted, and do not launch another full training run until the discrepancy is investigated with targeted tests and a held-out game-level validation design.

## Updated priorities after colour-symmetry audit

1. Trace value-target perspective from game result through sample creation, training loss and MCTS backup; add controlled mirror-pair tests with known labels.
2. Verify encoder and move-index transformations under `Board.mirror()`, including piece planes, side-to-move, castling and en-passant state; verify policy distribution mapping independently of model output.
3. Investigate candidate self-play colour outcomes with a larger paired/mirrored suite and preserve per-game PGNs and traces.
4. Keep the baseline checkpoint selected; do not promote the epoch-10 candidate or start another full training run yet.
5. Design held-out validation split by complete games before making value-calibration or strength claims.


## Side-to-move contract source review and regression coverage

A source-level trace of the value contract found no obvious sign inversion in the current pipeline:

- Self-play converts the final PGN result to a White-relative value, then _value_for_player() flips it for Black-to-move samples.
- AlphaZeroDataset passes the stored scalar unchanged; alphazero_loss() applies MSE without a perspective conversion.
- The value head emits a bounded tanh scalar. ModelInference.predict() returns it unchanged as the current side-to-move value.
- MCTS terminal values are from the terminal node's side-to-move perspective; _backpropagate() alternates sign once per edge; PUCT negates the child value when scoring from the parent perspective.

The encoder uses explicit White/Black piece planes and absolute rank/file coordinates. MoveEncoding normalizes Black move deltas by a 180-degree rotation. The model architecture does not enforce exact colour-mirror equivariance, and the inspected training path does not apply mirror augmentation. These are important representational/training facts, but they are not by themselves proof of a defect. The audit's poor candidate symmetry is therefore still a learned-behaviour signal with root cause undetermined.

A focused regression module, tests/test_colour_symmetry_contract.py, now covers the Board.mirror() encoder-plane transform, legal-move encode/decode on mirrored positions (including castling, en-passant and promotions), invariant side-to-move outcome labels, alternating MCTS backup perspective, and mirrored terminal values. These tests validate contracts; they deliberately do not assert that an unconstrained neural network must produce identical mirrored predictions.

No model, checkpoint, training configuration, or promotion rule was changed. The epoch-0 checkpoint remains selected; the epoch-10 candidate remains unpromoted. Further work should inspect sample distributions and add held-out game-level validation before attempting a symmetry augmentation or architecture change.


## Per-position self-play dataset preservation and audit

The self-play game log already retains complete PGNs, but earlier records did not
retain the corresponding per-position value targets. The diagnostic branch now
adds one record per played position containing its FEN, ply, side to move and
side-to-move-relative outcome target. The logger checks each target against the
completed game's result before writing it.

The training workflow artifact is extended to retain the game log and replay
buffer/journal alongside checkpoints and the checkpoint manifest. A read-only
comparison utility, `scripts/audit_self_play_datasets.py`, validates two
separately collected game-log files and reports outcomes, termination types,
White/Black sample counts and target distributions. It rejects legacy PGN-only
records and inconsistent PGN/FEN/target data.

This is data-capture and audit infrastructure only. It does not train or promote
a model. The manual diagnostic workflow generates a matched pair of baseline
and candidate logs from the preserved checkpoints. Existing historical
training data that was never retained cannot be retrospectively reconstructed.
No checkpoint or promotion state changes.


The manual read-only workflow
`.github/workflows/self-play-dataset-audit.yml` now generates matched baseline
and candidate datasets from the preserved checkpoints in training run
[43646981876](https://github.com/Nomusa990822/AlphaZero-Style-Chess-AI-Self-Play-Reinforcement-Learning-with-MCTS-and-Policy-Value-Networks/actions/runs/43646981876).
It defaults to eight games per checkpoint, 40 MCTS simulations and a 120-ply
cap, resets the same random seed for each checkpoint, and uploads both raw
PGN/position-target logs plus the validated comparison report. It is inference
only: no optimizer, training loop, checkpoint write, promotion or release
operation is invoked. The workflow is manual and has not been dispatched by
this source change.


### Diagnostic workflow correction — checkpoint digest

The first manual dispatch (run 43749569356) stopped before Python setup or
self-play generation. The baseline checkpoint SHA-256 matched, but the
candidate digest pinned in the workflow did not. Rechecking the actual
preserved artifact ZIP established the candidate digest as
`101294ee17c79fd9e4816b3e2676b8f87487c4932172861f59b96550c345af00`.
The workflow pin has been corrected. No dataset was generated and no model
weights were changed in the failed run. The workflow must be dispatched again.


## Self-play dataset audit dispatch — import-path failure (2026-11-15)

The corrected checkpoint digests were verified successfully in workflow [43750026398](https://github.com/Nomusa990822/AlphaZero-Style-Chess-AI-Self-Play-Reinforcement-Learning-with-MCTS-and-Policy-Value-Networks/actions/runs/43750026398). The run then failed before generating either dataset: direct execution of `scripts/generate_self_play_dataset.py` placed `scripts/`, rather than the repository root, on `sys.path`, so importing `src.engine.encoder` raised `ModuleNotFoundError: No module named 'src'`. Candidate generation and comparison were skipped; no dataset artifact was produced. No checkpoint was changed and no training or promotion occurred.

A focused fix adds the repository root (derived from `__file__`) to `sys.path` before importing project modules. It changes no model, inference, search, training or checkpoint behaviour. The diagnostic workflow must be dispatched again after the fix is merged.
