# Tactical benchmark corpus

This directory is the home for human-validated tactical positions used to
measure move-selection quality independently of training and CI correctness.

## Position format

Store one JSON object per line in a `.jsonl` file:

```json
{"id":"unique-id","motif":"fork","fen":"FEN position","acceptable_moves":["e2e4"]}
```

- `id`: stable, unique position identifier.
- `motif`: primary motif label, such as `fork`, `pin`, `skewer`,
  `hanging_piece`, `discovered_attack`, `defensive_resource`, or
  `mating_net`.
- `fen`: position before the engine moves.
- `acceptable_moves`: one or more acceptable first moves in UCI notation.
  Multiple moves are supported where more than one continuation is sound.

The loader validates FENs, terminal positions, duplicate IDs, and move legality.
Do not add a position until its motif and acceptable move set have been
reviewed; a legal move is not necessarily a tactically good move.

The committed `tactical_positions.jsonl` is only a small four-position starter
corpus. It covers a mating net, knight forks for both sides to move, and a
hanging-piece capture. It is not large or diverse enough to support a general
tactical-strength claim.

## Run a checkpoint benchmark

From the repository root, with dependencies installed:

```bash
python evaluate_tactics.py \
  --checkpoint data/checkpoints/best_model.pt \
  --positions benchmarks/tactical_positions.jsonl \
  --simulations 100 \
  --device auto \
  --output data/logs/tactical_benchmark.json
```

The runner uses the same 20-plane, 64-filter, 3-residual-block network
configuration as `train_pipeline.py`, loads the checkpoint, disables
Dirichlet noise, and selects deterministically at temperature zero. The JSON
report records checkpoint path/epoch, device, simulation count, overall
accuracy, per-motif results, and missed positions.

For meaningful comparisons, keep checkpoint, corpus, simulation count,
search configuration, and hardware fixed. A larger simulation count can
change both runtime and accuracy.

## Programmatic scoring

Use `src.training.tactical_benchmark.load_tactical_positions` to load the
corpus and `evaluate_tactical_selector` to score a callable that accepts a
`python-chess` board and returns a `chess.Move` or UCI string.

The result reports overall accuracy, per-motif accuracy, illegal outputs, and
the positions missed. This harness is intentionally separate from the CI
suite: CI verifies the benchmark implementation, while benchmark scores
measure playing decisions. Never treat an unreviewed or tiny corpus as
evidence of tactical strength.
