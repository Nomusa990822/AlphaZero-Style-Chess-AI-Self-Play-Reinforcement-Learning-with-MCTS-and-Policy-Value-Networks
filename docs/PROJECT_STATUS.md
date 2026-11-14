# Project Status

**Project:** AlphaZero-Style Chess AI  
**Status:** Active research and engineering  
**Default branch:** `main`  
**Latest main revision at this snapshot:** `68cf3a4e2e40aa7b3f92fd5b5d430c6d7a6ddbf8` (2026-11-14)

## Current verified state

The implementation includes a 20-plane board encoder, 4,672-action move representation, residual policy-value network, PUCT MCTS, self-play, replay persistence, candidate training/evaluation, checkpoint management, tactical-root safeguards, a tactical benchmark runner, and a resource-bounded search-configuration sweep.

The current curated tactical corpora contain **35 positions** (19 White-to-move, 16 Black-to-move) and **11 annotated sequences / 37 plies**. The latest defensive-countercheck semantic-test revision passed **189 CPU tests** and the Stockfish audit supported **35/35 positions and 11/11 sequences / 37/37 plies with zero flagged entries**. See the linked workflow records in [DEVELOPMENT_LOG.md](DEVELOPMENT_LOG.md) and [benchmarks/README.md](../benchmarks/README.md).

## Training and checkpoint state

A bounded fresh-start CPU pipeline pilot **was executed successfully** on 2026-11-13 (workflow [43497298757](https://github.com/Nomusa990822/AlphaZero-Style-Chess-AI-Self-Play-Reinforcement-Learning-with-MCTS-and-Policy-Value-Networks/actions/runs/43497298757)). It completed one iteration, four self-play games, 274 positions, one training epoch, and two colour-swapped candidate-evaluation games. Both evaluation games were draws (score 0.50); the candidate was **not promoted**. The pilot validated the pipeline and backup process; it did not establish playing strength or Elo.

The baseline checkpoint remains the selected model:
- `best_model.pt`, epoch 0; SHA-256 `7a9fdacbd14f6423e34b2edb470d255e15081a12b1e66faf204a5e07e24e4471`.
- Candidate `latest_candidate.pt`, epoch 1; SHA-256 `3b471702e89659307f11ec95b3f83316ccae7c29a4c7d9d6faa7afaa4f7231a7`; retained separately and not promoted.

Both checkpoints and their manifest are preserved in the durable prerelease [fresh-pilot-checkpoint-43497298757-1](https://github.com/Nomusa990822/AlphaZero-Style-Chess-AI-Self-Play-Reinforcement-Learning-with-MCTS-and-Policy-Value-Networks/releases/tag/fresh-pilot-checkpoint-43497298757-1). The release contains `best_model.pt`, `latest_candidate.pt`, and `fresh-pilot-checkpoint-manifest.json`. The corresponding Actions artifact [14071428532](https://github.com/Nomusa990822/AlphaZero-Style-Chess-AI-Self-Play-Reinforcement-Learning-with-MCTS-and-Policy-Value-Networks/actions/runs/43497298757) also preserves replay data and logs.

The normal `.github/workflows/train-and-backup.yml` workflow is **resume-only**: it requires a non-empty `data/checkpoints/best_model.pt` before dependency installation and requires the user to select `YES`. The tracked repository does not contain the binary checkpoint. Restore the released baseline into that path and verify its SHA-256 against the manifest before dispatching further training. Do not start a fresh random run or overwrite either checkpoint as a workaround.

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

1. Download the baseline checkpoint and manifest from the durable prerelease; verify the SHA-256 and retain an independent copy.
2. Restore `best_model.pt` into the intended training/evaluation environment without committing it to Git.
3. Run checkpoint integrity/metadata diagnostics and the fixed tactical-position and sequence benchmarks on the current 35-position / 11-sequence corpora. Preserve raw JSON reports and checkpoint hash.
4. Run the paired tactical-root-filter ablation and resource-bounded search sweep with the same checkpoint, CPU device, corpus and declared simulation budget.
5. Design the next staged training schedule only after baseline diagnostics; preserve the baseline and candidate separately and do not promote without a suitably powered, colour-balanced evaluation.
6. Establish a repeatable fixed-opponent match protocol with enough paired games and uncertainty reporting before making strength claims.

## Verification and documentation protocol

- Latest main snapshot: `68cf3a4e2e40aa7b3f92fd5b5d430c6d7a6ddbf8`.
- Latest semantic regression CI: CPU [43641897416](https://github.com/Nomusa990822/AlphaZero-Style-Chess-AI-Self-Play-Reinforcement-Learning-with-MCTS-and-Policy-Value-Networks/actions/runs/43641897416), **189 passed**.
- Latest tactical audit: [43641897417](https://github.com/Nomusa990822/AlphaZero-Style-Chess-AI-Self-Play-Reinforcement-Learning-with-MCTS-and-Policy-Value-Networks/actions/runs/43641897417), **35/35 positions and 11/11 sequences / 37/37 plies supported; zero flagged**, artifact [14132283194](https://github.com/Nomusa990822/AlphaZero-Style-Chess-AI-Self-Play-Reinforcement-Learning-with-MCTS-and-Policy-Value-Networks/actions/runs/43641897417).
- Update `README.md`, `benchmarks/README.md`, this status file and `DEVELOPMENT_LOG.md` with each meaningful engineering batch.
- Add entries to `EXPERIMENT_LOG.md` only when an actual training or benchmark experiment runs.
- Record exact revisions, workflow links, failures and repairs. Never replace unknown data with estimates.
