# Confirmatory evaluation implementation

The confirmatory path is isolated in `src/training/confirmatory_evaluator.py`.
It does not change `NetworkEvaluator`, the training pipeline, its 12-opening
development suite, or its routine candidate-promotion gate.

The frozen suite is `evaluation_openings_confirmatory_v1.jsonl`: 24 positions,
at least eight labelled families, no more than four positions per family.
The loader replays every UCI line from the standard initial board, validates
legality and non-terminal status, checks unique IDs/FENs, and rejects overlap
with the existing development suite.

The evaluator requires all 24 pairs / 48 games and uses the predeclared
one-sided 90% Student-t critical value for 23 degrees of freedom (1.319460).
The existing training evaluator's statistic is deliberately untouched.

This module is implementation scaffolding for the frozen protocol. The
current report records aggregate and pair-level outcomes. Before any dispatch,
the workflow must additionally pin and verify both checkpoint hashes, record
the suite SHA-256 and runtime metadata, and preserve raw per-game PGNs/UCI
records. No workflow dispatch, training, checkpoint write, or promotion is
performed by these changes.
