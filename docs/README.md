# Project documentation

Use these documents as the project's source of truth:

| Document | Purpose |
|---|---|
| [Project status](PROJECT_STATUS.md) | Current verified state, limitations and next priorities |
| [Development log](DEVELOPMENT_LOG.md) | Chronological engineering changes, design decisions and test evidence |
| [Experiment log](EXPERIMENT_LOG.md) | Training runs, benchmark measurements and reproducibility details |
| [Training flow](training_flow.md) | Training pipeline notes |

## How we keep the record current

Every meaningful implementation batch should update the development log and project status in the same pull request. Changes to tactical data must also update `benchmarks/README.md`, the root `README.md`, affected regression tests, and any relevant technical notes. Only actual training or benchmark runs belong in the experiment log. Preserve raw outputs under `data/logs/` and link to them rather than replacing them with manually transcribed estimates.
