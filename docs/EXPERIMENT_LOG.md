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
