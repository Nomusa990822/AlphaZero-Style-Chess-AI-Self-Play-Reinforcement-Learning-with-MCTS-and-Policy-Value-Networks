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

## Scoring

Use `src.training.tactical_benchmark.load_tactical_positions` to load the
corpus and `evaluate_tactical_selector` to score a callable that accepts a
`python-chess` board and returns a `chess.Move` or UCI string.

The result reports overall accuracy, per-motif accuracy, illegal outputs, and
the positions missed. For MCTS, the selector can run a deterministic search
and return its selected move. Keep simulation count, checkpoint, search
configuration, and hardware fixed when comparing versions.

This harness is intentionally separate from the CI suite: CI verifies the
benchmark implementation, while benchmark scores measure playing decisions.
Never treat an unreviewed or empty corpus as evidence of tactical strength.
