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
