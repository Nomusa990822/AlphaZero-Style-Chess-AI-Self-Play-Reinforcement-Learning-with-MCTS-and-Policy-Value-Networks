# Checkpoint tactical evaluation

The manual workflow `.github/workflows/checkpoint-tactical-evaluation.yml`
compares the durable fresh-start baseline and candidate checkpoints against
the curated tactical corpora. It is a deterministic CPU evaluation only; it
does not train, modify, or promote either checkpoint.

## Dispatch

1. Open Actions → **Checkpoint tactical evaluation**.
2. Under **Use workflow from**, select **Main**. The dispatch definition is
   intentionally stored on the default branch so GitHub displays its inputs.
3. Keep `confirm_evaluation` at `NO` until ready.
4. Select 100 simulations per move (recommended; 50 is a quicker diagnostic).
5. Set confirmation to `YES` and dispatch only when explicitly authorised.

The workflow runs from `main`, then explicitly checks out
`chess-strength-training-upgrade` for the evaluator scripts and tactical
corpora. Do not select the feature branch in the dispatch dropdown.

## What it measures

Both checkpoints are SHA-256 verified against the immutable prerelease
manifest before loading. Each checkpoint is evaluated with deterministic
MCTS (no Dirichlet noise, temperature zero) on:
- all curated individual tactical positions, scored by acceptable first move;
- all curated tactical sequences, scored by annotated principal-variation
  move agreement and completion.

Reports separate motif, colour and phase where supported by the evaluator.
Sequence results are line-following agreement, not proof that a line is forced.
Position accuracy is agreement with the curated acceptable-move labels, not
general chess strength. The tactical root safeguards are enabled, so scores
include the engine's existing mate-in-one and one-ply mate-safety filters.

The workflow downloads the exact release assets
`best_model.pt`, `latest_candidate.pt`, and
`fresh-pilot-checkpoint-manifest.json`. It uploads four JSON reports plus
the checkpoint manifest for 90-day retention. It does not claim Elo, alter the
durable release, or promote the candidate.
