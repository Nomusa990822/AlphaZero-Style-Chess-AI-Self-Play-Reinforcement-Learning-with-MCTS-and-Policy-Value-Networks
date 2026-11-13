# Tactical benchmark corpus

This directory is the home for human-validated tactical positions used to
measure move-selection quality independently of training and CI correctness.

## Position format

Store one JSON object per line in a `.jsonl` file:

```json
{"id":"unique-id","motif":"fork","fen":"FEN position","acceptable_moves":["e2e4"],"annotation":"Explain the motif and accepted move.","phase":"middlegame"}
```

- `id`: stable, unique position identifier.
- `motif`: one of the validated labels: `mating_net`, `fork`,
  `hanging_piece`, `pin`, `skewer`, `discovered_attack`,
  `double_attack`, `deflection`, `decoy`, `overloaded_defender`,
  `trapped_piece`, `defensive_resource`, or `endgame_tactic`.
  Unknown labels are rejected to prevent inconsistent per-motif reporting.
- `fen`: position before the engine moves.
- `acceptable_moves`: one or more acceptable first moves in UCI notation.
  Multiple moves are supported where more than one continuation is sound.
- `annotation`: a non-empty human-written rationale connecting the position,
  motif, and accepted move. This is review metadata, not engine proof.
- `phase`: an explicitly curated label: `opening`, `middlegame`, or `endgame`.
  The loader does not infer phase from material; composed tactical positions
  can make automatic phase heuristics misleading.

The loader validates FENs, terminal positions, duplicate IDs, move legality,
controlled motif labels, and the presence of a non-empty tactical annotation.
Do not add a position until its motif and acceptable move set have been
reviewed; a legal move is not necessarily a tactically good move.

The committed `tactical_positions.jsonl` is still a small starter corpus. It
now includes a mating net, knight forks, hanging-piece captures, pins, and
rook skewers, discovered attacks, defensive resources and promotion tactics,
with examples for both sides to move. Its thirteen positions are
not large or diverse enough to support a general tactical-strength claim.

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
accuracy, per-motif, per-colour, and per-phase results, and missed positions.

For meaningful comparisons, keep checkpoint, corpus, simulation count,
search configuration, and hardware fixed. A larger simulation count can
change both runtime and accuracy.

## Programmatic scoring

Use `src.training.tactical_benchmark.load_tactical_positions` to load the
corpus and `evaluate_tactical_selector` to score a callable that accepts a
`python-chess` board and returns a `chess.Move` or UCI string.

The result reports overall accuracy, per-motif accuracy, separate White-to-move
and Black-to-move accuracy, and per-phase accuracy for explicitly labelled
opening, middlegame, and endgame groups, plus illegal outputs and missed positions. Multiple
acceptable moves are treated as a set: selecting any curated move is a success. This harness is intentionally separate from the CI
suite: CI verifies the benchmark implementation, while benchmark scores
measure playing decisions. Never treat an unreviewed or tiny corpus as
evidence of tactical strength.


## Stockfish-assisted corpus review

The optional CI workflow `.github/workflows/tactical-engine-audit.yml` runs
Stockfish against every curated position and uploads a JSON artifact named
`tactical-engine-audit`. The report includes the engine/version identity,
search depth, top principal variations, and a separate fixed-depth evaluation
for every human-accepted move. It flags accepted moves that fall more than the
configured centipawn tolerance behind the engine's best line.

The default CI audit uses depth 16, MultiPV 5, one thread, and a 150-centipawn
tolerance. These settings make the review reproducible and affordable in CI;
they are not proof of optimal play. A flagged position requires human review,
and an unflagged position still requires review of its motif annotation and
chess explanation. Engine scores are sensitive to version, depth, hash and
hardware. Do not silently replace human labels with engine top moves.

Run it where Stockfish is installed:

```bash
python scripts/audit_tactical_corpus.py \\
  --engine stockfish \\
  --depth 18 \\
  --multipv 5 \\
  --max-loss-cp 150 \\
  --output reports/tactical-engine-audit.json
```


## First recorded engine review

The thirteen-position starter corpus was reviewed by Stockfish 17.1 in GitHub
Actions on 2026-11-13 (depth 16, MultiPV 5, one thread, 256 MB hash). All
13 curated acceptable moves were within 150 centipawns of the engine's best
line, and no positions were flagged by the configured comparison. The JSON
report is retained as the `tactical-engine-audit` artifact from workflow run
[43403925496](https://github.com/Nomusa990822/AlphaZero-Style-Chess-AI-Self-Play-Reinforcement-Learning-with-MCTS-and-Policy-Networks/actions/runs/43403925496).

This is a first-pass consistency check, not a proof that every motif label is
correct, that every move is uniquely best, or that the corpus is comprehensive.
The audit tolerance is a review aid, not a chess-theoretic correctness rule.


## Tactical-root-filter ablation

The checkpoint evaluator exposes an explicit ablation switch so the tactical
root safeguard can be compared against ordinary visit-based MCTS selection.
Run both configurations against the same checkpoint, corpus, device and
simulation budget:

```bash
python evaluate_tactics.py --checkpoint data/checkpoints/best_model.pt \
  --simulations 100 --device cpu --output reports/tactics-filter-on.json

python evaluate_tactics.py --checkpoint data/checkpoints/best_model.pt \
  --simulations 100 --device cpu --disable-tactical-root-filter \
  --output reports/tactics-filter-off.json
```

The JSON report records `tactical_root_filter` so the configuration is
explicit. Keep every other setting fixed when comparing results. This is an
ablation facility, not a strength claim; run it on a real checkpoint and
review the full per-position failures before drawing conclusions.
