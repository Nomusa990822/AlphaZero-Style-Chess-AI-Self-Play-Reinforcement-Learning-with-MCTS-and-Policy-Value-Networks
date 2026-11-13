# Training and checkpoint recovery

## Current checkpoint status

The tracked source tree does not contain model weights. The path
`data/checkpoints/` is intentionally excluded by `.gitignore`, and the
checkpoint `data/checkpoints/best_model.pt` is not currently available in
this checkout. Training metrics in `data/logs/training_metrics.jsonl` are
historical measurements, not model weights; they cannot recreate a checkpoint.

Before training, first look for an original `.pt` backup in the user's local
downloads, previous machine backups, or a previously downloaded GitHub Actions
artifact / model-checkpoint release. The repository's release list currently
has no published checkpoint release. If a backup is recovered, do not commit
the binary weights to Git.

## Restore a recovered checkpoint

1. Confirm the file is the project's AlphaZero policy/value model checkpoint,
   not a replay-buffer pickle, a training log, or an unrelated PyTorch file.
2. Place it at `data/checkpoints/best_model.pt` in the working checkout.
3. Generate an inventory and SHA-256 hash:
   `python scripts/create_checkpoint_manifest.py`.
4. Preserve the checkpoint and manifest outside the ephemeral Codespace. Use a
   durable GitHub Actions artifact and model-checkpoint release for a future
   authorised training run.
5. Run the CPU test suite and the two tactical evaluation scripts against the
   restored checkpoint before considering any training.

The checkpoint loader supports the documented 19-input-plane to 20-input-plane
encoder migration. Other tensor-shape mismatches are rejected. Optimizer state
is reset for that specific encoder migration.

## Safety gate

The configured training entry point sets `resume_best_model=True`. The
pipeline now refuses to start if its configured best-model checkpoint is
missing, rather than silently training a fresh random network. The manual
GitHub Actions training workflow also checks for a non-empty checkpoint before
installing dependencies or beginning any training work.

Fresh-from-random training remains a separate, explicit decision: it requires
changing the configuration to `resume_best_model=False` and deliberately
authorising the training workflow. Do not make that change merely to bypass a
missing backup.

## Tactical evaluation after recovery

Once a compatible checkpoint is present, run the evaluation scripts (not the
training pipeline):

```bash
python evaluate_tactics.py \
  --checkpoint data/checkpoints/best_model.pt \
  --simulations 100 \
  --device cpu \
  --output reports/tactical-benchmark.json

python evaluate_tactical_sequences.py \
  --checkpoint data/checkpoints/best_model.pt \
  --simulations 100 \
  --device cpu \
  --output reports/tactical-sequence-benchmark.json
```

These evaluations use deterministic MCTS settings and report motif, colour,
phase and sequence results. Sequence scoring follows annotated principal
variations; it does not prove that each line is forced against every defence.
A benchmark score is not an Elo estimate.


## Fresh-start smoke pilot (prepared, not launched)

The original training entry point remains in resume mode and still refuses to run
without a compatible checkpoint. For an explicitly authorised fresh start, use
the separate `fresh_start_pilot.py` entry point. It creates a random-initialised
baseline checkpoint with metadata marking it as untrained, then starts the
pipeline in resume mode. It refuses to overwrite an existing pilot baseline.

The bounded pilot uses one iteration, four self-play games, an 80-ply cap,
eight MCTS simulations for both self-play and candidate evaluation, one training
epoch, and two colour-swapped candidate-evaluation games. Outputs are isolated
under `data/checkpoints/fresh_pilot/`, `data/replay_buffer/fresh_pilot/`,
and `data/logs/fresh_pilot/`.

The separate manual GitHub Actions workflow is restricted to the feature branch
and requires an explicit `YES`; it defaults to `NO`. It uploads pilot outputs
for 90 days and publishes a checkpoint prerelease with SHA-256 manifest on
success. Do not dispatch it until the user explicitly authorises the compute
run. The pilot validates the training pipeline and backup path; its small game
sample is not a meaningful playing-strength or Elo evaluation.


### CI status and manual-dispatch limitation

The fresh-start pilot code and configuration test passed in CPU CI (172 tests),
and the Stockfish corpus audit passed for all 22 positions, five sequences and
19 annotated plies with no flags. The training pilot itself has not run.

GitHub's manual `workflow_dispatch` event requires the workflow definition to
exist on the repository's default branch. This new workflow is currently only
on the feature branch. Keeping `main` unchanged means it is not dispatchable
yet; do not merge the PR merely to enable training. Any future decision to make
the workflow available on the default branch must be explicit.
