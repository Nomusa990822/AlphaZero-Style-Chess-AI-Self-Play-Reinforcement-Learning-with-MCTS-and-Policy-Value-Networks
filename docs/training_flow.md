# Training and checkpoint recovery

## Current checkpoint status

The tracked source tree does not contain model weights. The path
`data/checkpoints/` is intentionally excluded by `.gitignore`, and the
checkpoint `data/checkpoints/best_model.pt` is not currently available in
this checkout. Training metrics in `data/logs/training_metrics.jsonl` are
historical measurements, not model weights; they cannot recreate a checkpoint.

The immutable epoch-0 baseline is preserved in the durable prerelease
[fresh-pilot-checkpoint-43497298757-1](https://github.com/Nomusa990822/AlphaZero-Style-Chess-AI-Self-Play-Reinforcement-Learning-with-MCTS-and-Policy-Value-Networks/releases/tag/fresh-pilot-checkpoint-43497298757-1).
The manual resume workflow automatically restores it from that release only
when the checkout has no non-empty best_model.pt, verifies the pinned
SHA-256, and preserves any existing non-empty champion checkpoint. Never
commit binary weights to Git.

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
missing, rather than silently training a fresh random network. The manual GitHub Actions training workflow first restores the immutable
baseline when necessary, verifies its SHA-256, and then checks for a non-empty
checkpoint before installing dependencies or beginning training. Its
confirm_training=YES gate remains mandatory.

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


### CI status and manual dispatch

The pilot workflow is now present on the repository's default branch, `main`,
after PR #1 was merged on 2026-11-13. It is therefore available from the
GitHub Actions tab. To select the code to run, choose the
`chess-strength-training-upgrade` branch in the workflow's **Run workflow**
branch selector. The workflow job itself is restricted to that exact branch
and requires `confirm_fresh_training=YES`; the input defaults to `NO`.

The merge commit is `cb8ddd0ee3ae332dfeda500bbf961fc80451a07f`. The default
branch's post-merge CPU test workflow completed successfully on that exact
commit (run
[43491543336](https://github.com/Nomusa990822/AlphaZero-Style-Chess-AI-Self-Play-Reinforcement-Learning-with-MCTS-and-Policy-Value-Networks/actions/runs/43491543336)).
The pre-merge final PR revision also passed 172 CPU tests and the Stockfish
audit (22 positions, five sequences, nineteen annotated plies; zero flags).

The fresh-start pilot **was executed successfully** on 2026-11-13 (workflow [43497298757](https://github.com/Nomusa990822/AlphaZero-Style-Chess-AI-Self-Play-Reinforcement-Learning-with-MCTS-and-Policy-Value-Networks/actions/runs/43497298757)). It generated an epoch-0 baseline and epoch-1 candidate, replay data and logs. The candidate was not promoted after two drawn evaluation games. This remains a pipeline smoke test, not a meaningful playing-strength or Elo evaluation. The baseline and candidate are backed up in the durable prerelease [fresh-pilot-checkpoint-43497298757-1](https://github.com/Nomusa990822/AlphaZero-Style-Chess-AI-Self-Play-Reinforcement-Learning-with-MCTS-and-Policy-Value-Networks/releases/tag/fresh-pilot-checkpoint-43497298757-1).


## Restore the completed pilot baseline before further training

The successful pilot's selected baseline checkpoint is available as the `best_model.pt` asset in the [durable prerelease](https://github.com/Nomusa990822/AlphaZero-Style-Chess-AI-Self-Play-Reinforcement-Learning-with-MCTS-and-Policy-Value-Networks/releases/tag/fresh-pilot-checkpoint-43497298757-1). Its expected SHA-256 is:

`7a9fdacbd14f6423e34b2edb470d255e15081a12b1e66faf204a5e07e24e4471`

The separate candidate has SHA-256 `3b471702e89659307f11ec95b3f83316ccae7c29a4c7d9d6faa7afaa4f7231a7`; do not substitute it for the baseline. Keep an independent backup of the baseline and manifest. The resume workflow restores only the baseline to `data/checkpoints/best_model.pt` when no non-empty checkpoint is present. Do not commit either binary to Git.

The standard `train-and-backup.yml` workflow remains resume-only, restores and verifies the baseline when needed, and requires `confirm_training=YES`. Its current `train_pipeline.py` configuration is substantially larger than the pilot: 2 iterations, 40 self-play games per iteration, 250-ply cap, 80 self-play MCTS simulations, 100 evaluation simulations, 10 training epochs and 24 candidate-gating games per iteration. This is a potentially long CPU job (workflow timeout: 6 hours); it must not be dispatched until baseline diagnostics are complete and the user explicitly confirms the compute run.


## Automated, hash-verified baseline recovery in the resume workflow

The standard manual training workflow now restores the immutable epoch-0 pilot
baseline from the durable prerelease **only when**
`data/checkpoints/best_model.pt` is absent or empty. It downloads to a temporary
file, verifies SHA-256
`7a9fdacbd14f6423e34b2edb470d255e15081a12b1e66faf204a5e07e24e4471`, and only
then installs it at the expected path. A pre-existing non-empty checkpoint is
never overwritten. If download or verification fails, the job stops before
dependency installation or training.

This recovery step makes the workflow runnable from a clean checkout while
preserving any later trained best checkpoint. It does not itself start training:
the workflow still requires the manual `confirm_training=YES` input. A run
with `NO` does not enter the training job. After an authorised run, the
existing artifact and durable-release backup steps preserve resulting weights
and the generated manifest. Keep an independent local copy of the original
baseline release as well.


## Incumbent-relative model promotion policy

A candidate is evaluated directly against the currently promoted champion. Its
match score is relative to that opponent: win = 1, draw = 0.5, loss = 0.
It is not an absolute model-quality score and must not be compared with scores
from unrelated opponents or separate evaluation protocols.

Promotion has no arbitrary 0.55 cutoff. A candidate is promoted only when **all**
of these checks pass:

1. At least 24 games are completed.
2. Games are colour-balanced (an even number, with each model playing both
   colours equally) and use deterministic MCTS without exploration noise.
3. The candidate's match score is strictly greater than 0.50, meaning it
   outscored the current champion.
4. The one-sided 90% lower confidence bound is also strictly greater than
   0.50, providing evidence that the advantage is not just a small-sample
   fluctuation.
5. Every move returned by either evaluator agent is legal. An illegal move
   aborts evaluation; it is never counted as a win or silently ignored.

If any condition fails, the current champion and its checkpoint are preserved.
The newly trained candidate remains separately available as latest_candidate.
The two-game smoke pilot is therefore never eligible for promotion. Every new
candidate is compared with whichever champion is currently selected at that
iteration, so the standard is relative to the best model already retained.
