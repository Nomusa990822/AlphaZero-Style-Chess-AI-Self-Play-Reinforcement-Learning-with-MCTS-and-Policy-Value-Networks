# Experiment Log

This file records measured training and evaluation runs. It separates training optimisation metrics from playing-strength evidence. Raw iteration summaries remain under `data/logs/`.

## Reporting rules

- Preserve the exact configuration and raw result source whenever available.
- Record the checkpoint identifier/hash where possible.
- Distinguish training loss from chess-playing strength.
- A draw score against a weak, identical or uncalibrated opponent is not an Elo rating.
- Do not compare runs unless the relevant settings are controlled or differences are disclosed.
- Use **not run** rather than inventing missing values.
- Tactical benchmark scores must include the corpus revision, checkpoint, simulation count, device and output report path.

## Historical training runs already in the repository

The repository contains five iteration summary files for a six-self-play-game configuration and three earlier records in the append-only metrics file. The five summary files report:

| Iteration | Self-play games | Positions generated | Replay buffer | Training epochs | Final total loss | Evaluation games | W/L/D | Score | Promoted |
|---:|---:|---:|---:|---:|---:|---:|---|---:|---|
| 1 | 6 | 900 | 900 | 3 | 5.862993 | 4 | 0/0/4 | 0.50 | No |
| 2 | 6 | 900 | 1,800 | 3 | 6.172966 | 4 | 0/0/4 | 0.50 | No |
| 3 | 6 | 900 | 2,700 | 3 | 6.304053 | 4 | 0/0/4 | 0.50 | No |
| 4 | 6 | 900 | 3,600 | 3 | 6.374887 | 4 | 0/0/4 | 0.50 | No |
| 5 | 6 | 900 | 4,500 | 3 | 6.385190 | 4 | 0/0/4 | 0.50 | No |

Sources:
- `data/logs/iteration_001_summary.json`
- `data/logs/iteration_002_summary.json`
- `data/logs/iteration_003_summary.json`
- `data/logs/iteration_004_summary.json`
- `data/logs/iteration_005_summary.json`

The append-only `data/logs/training_metrics.jsonl` also contains three earlier entries with three self-play games per iteration, 234/240/240 positions generated, two training epochs and four evaluation draws per iteration. Those records are retained as historical observations; they are not merged into the five-iteration table because they belong to a different run/configuration context.

### Interpretation

- All five six-game summaries show a 0–0–4 evaluation record and a score of 0.50.
- No candidate was promoted in these records.
- Total loss increased across those five summaries; this is not evidence of improved playing strength.
- The recorded evaluation sample is very small (four games per iteration), so it is not a reliable playing-strength estimate.
- Training run dates, hardware, exact checkpoint hashes and complete hyperparameter configurations are not present in these summary records and remain **not recorded**.

## Tactical benchmark runs

| Date | Checkpoint | Corpus | Simulations | Device | Accuracy | Result file | Status |
|---|---|---|---:|---|---:|---|---|
| Not run | Not recorded | 3-position starter corpus | — | — | — | — | Awaiting a real checkpoint benchmark |

The CI workflow tests the benchmark code and corpus loading. It does not execute a meaningful checkpoint-strength experiment.

## New experiment entry template

### YYYY-MM-DD — Experiment name

- **Purpose/hypothesis:**
- **Code revision:**
- **Checkpoint path and SHA-256:**
- **Dataset/corpus revision:**
- **Hardware/device:**
- **Configuration:** simulations, temperature, noise, batch size, learning rate, epochs, opponents, time/node controls, as applicable.
- **Games/positions:**
- **Results:** wins, losses, draws, score, loss metrics, accuracy and uncertainty, as applicable.
- **Runtime/resource use:**
- **Artifacts:** raw JSON/JSONL/PGN/report paths.
- **Interpretation:**
- **Limitations and next experiment:**



### 2026-11-13 — Fresh-start CPU pipeline pilot (run 43497298757)

- Purpose: validate fresh random initialisation, one bounded self-play/training iteration, candidate evaluation, checkpoint persistence and backup. This is a pipeline smoke test, not a playing-strength experiment.
- Code revision: dbba702569372370a3488a02a4d84024f63e2aac on chess-strength-training-upgrade. [Workflow run](https://github.com/Nomusa990822/AlphaZero-Style-Chess-AI-Self-Play-Reinforcement-Learning-with-MCTS-and-Policy-Value-Networks/actions/runs/43497298757) completed successfully.
- Device: GitHub-hosted Ubuntu runner, CPU PyTorch.
- Configuration: 1 iteration; 4 self-play games; 80-move cap; 8 MCTS simulations; 1 training epoch; batch size 32; 2 colour-swapped candidate evaluation games.
- Self-play: 274 positions; average game length 68.5 moves; results were 1 White win and 3 draws (one move-cap draw, three other games ended by chess rules).
- Training: final total loss 8.0741975; policy loss 7.8813077; value loss 0.1928899. One epoch only.
- Candidate evaluation: 0 wins, 0 losses, 2 draws; score 0.50; 90% lower confidence bound 0.50. Candidate NOT promoted. Two games are far too few to establish strength or Elo.
- Baseline checkpoint best_model.pt: 3,404,943 bytes; SHA-256 7a9fdacbd14f6423e34b2edb470d255e15081a12b1e66faf204a5e07e24e4471.
- Candidate checkpoint latest_candidate.pt: 10,193,391 bytes; SHA-256 3b471702e89659307f11ec95b3f83316ccae7c29a4c7d9d6faa7afaa4f7231a7.
- Artifacts: Actions artifact [14071428532](https://github.com/Nomusa990822/AlphaZero-Style-Chess-AI-Self-Play-Reinforcement-Learning-with-MCTS-and-Policy-Value-Networks/actions/runs/43497298757) (12,562,511 bytes; contains checkpoints, replay buffer, logs and manifest). Durable prerelease [fresh-pilot-checkpoint-43497298757-1](https://github.com/Nomusa990822/AlphaZero-Style-Chess-AI-Self-Play-Reinforcement-Learning-with-MCTS-and-Policy-Value-Networks/releases/tag/fresh-pilot-checkpoint-43497298757-1) contains both checkpoints and manifest.
- Interpretation: fresh-start pipeline, training, evaluation, manifest, artifact upload and prerelease backup all completed. Baseline was retained because the candidate did not pass the promotion gate. This run is not evidence of competent chess play.
- Next: preserve the backup; inspect checkpoint metadata and replay data, then design longer staged training with fixed opponents and substantially larger paired-game evaluation. Do not infer Elo from this pilot.


### 2026-11-13 — Baseline/candidate tactical checkpoint evaluation (run 43503135826)

- **Purpose:** Compare the fresh-start pilot's epoch-0 baseline and epoch-1 candidate on the individual tactical-position corpus and combined tactical-sequence corpus. This is a tactical diagnostic, not a playing-strength match.
- **Workflow/code revision:** [GitHub Actions run 43503135826](https://github.com/Nomusa990822/AlphaZero-Style-Chess-AI-Self-Play-Reinforcement-Learning-with-MCTS-and-Policy-Value-Networks/actions/runs/43503135826), dispatched from `main` at `43a68cebd39271c687adf068859f29ca69462882`; evaluator code and corpora checked out from `chess-strength-training-upgrade`.
- **Execution:** GitHub-hosted Ubuntu CPU; CPU-only PyTorch; deterministic evaluation; 100 MCTS simulations; tactical root filter enabled. Workflow completed successfully and both checkpoint hashes were verified against the release manifest before evaluation.
- **Checkpoint identities:** baseline `best_model.pt`, epoch 0, SHA-256 `7a9fdacbd14f6423e34b2edb470d255e15081a12b1e66faf204a5e07e24e4471`; candidate `latest_candidate.pt`, epoch 1, SHA-256 `3b471702e89659307f11ec95b3f83316ccae7c29a4c7d9d6faa7afaa4f7231a7`.
- **Individual positions (22 total):** baseline 4 correct / 22 = **18.18%**; candidate 5 / 22 = **22.73%**. Both had 0 illegal moves. Baseline by colour: White 2/12, Black 2/10. Candidate by colour: White 2/12, Black 3/10. Candidate's additional correct result is on a small curated corpus; motif-level counts are too small for broad conclusions.
- **Combined sequences (5 total, 7 annotated plies):** both checkpoints matched 3/7 plies = **42.86%**, completed 1/5 sequences = **20%**, and had 0 illegal moves. Both completed the same three-ply removal-of-defender/mating-net sequence; neither completed the other four sequences.
- **Raw report paths in uploaded artifact:** `reports/checkpoint_tactical_evaluation/baseline_positions.json`, `candidate_positions.json`, `baseline_sequences.json`, and `candidate_sequences.json`. Artifact: [checkpoint-tactical-evaluation-43503135826](https://github.com/Nomusa990822/AlphaZero-Style-Chess-AI-Self-Play-Reinforcement-Learning-with-MCTS-and-Policy-Value-Networks/actions/runs/43503135826), ID `14074627894`, 4,597 bytes, expiry 2027-02-11. The original immutable checkpoint release remains [fresh-pilot-checkpoint-43497298757-1](https://github.com/Nomusa990822/AlphaZero-Style-Chess-AI-Self-Play-Reinforcement-Learning-with-MCTS-and-Policy-Value-Networks/releases/tag/fresh-pilot-checkpoint-43497298757-1).
- **Interpretation:** The candidate was one position better on the individual benchmark but tied the baseline on combined-sequence performance. The individual benchmark measures agreement with an annotated acceptable move, not tactical outcome across every defence. The sequence benchmark follows the curated principal variation; opponent replies are prescribed and alternative defences are not exhaustively searched. Twenty-two positions and five sequences are a small diagnostic sample. These scores do not establish overall playing strength or Elo.
- **Checkpoint decision:** No training, checkpoint modification, or promotion occurred. Keep the baseline as the selected checkpoint and retain the candidate separately; do not promote based on this small benchmark difference.
- **Next:** Expand the independently reviewed tactical corpus and add a larger fixed-opponent, colour-balanced match evaluation before making any playing-strength decision.


### 2026-11-13 — Tactical corpus expansion (validation pending)

- Added four candidate positions to the curated tactical corpus: overloaded-defender and trapped-piece motifs for both White and Black.
- Corpus size is 26 positions (14 White to move, 12 Black to move). Semantic tests replay the tactical lines; source notes are included with each position.
- These positions are **not yet engine-reviewed**. They must pass the Python suite and Stockfish audit before being included in future checkpoint comparisons.
- No model was evaluated or trained in this corpus-authoring step.
