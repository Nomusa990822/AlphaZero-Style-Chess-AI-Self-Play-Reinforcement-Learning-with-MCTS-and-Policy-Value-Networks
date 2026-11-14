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
