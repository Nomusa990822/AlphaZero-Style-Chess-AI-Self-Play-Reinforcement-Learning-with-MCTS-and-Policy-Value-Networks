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


## Candidate lifecycle and diagnostic guardrails after training run 43646981876

The current pipeline uses an incumbent/challenger pattern, but it does not preserve a rejected challenger between outer iterations:

1. Self-play is generated using the current `best_model` (the incumbent).
2. `_build_candidate_model()` copies the incumbent state into a newly constructed model.
3. A new `AlphaZeroTrainer` and Adam optimizer are constructed for that candidate.
4. The candidate trains on the entire accumulated replay buffer.
5. If promotion fails, the incumbent remains unchanged. The next iteration repeats from the same incumbent weights with another fresh optimizer; only the replay buffer has grown.

This exactly explains why iteration 2 of run 43646981876 did not continue from iteration 1's rejected candidate. It also means the replay data in that run was generated by the epoch-0 incumbent, not by the trained candidate. This may be a deliberate conservative champion/challenger design, but it is not a continuously advancing self-play learner. Do not change it until a separate challenger-lineage design has been specified and tested. Any revised design must preserve the incumbent checkpoint, candidate checkpoint, optimizer-state provenance and the existing promotion gate.

The current trainer computes and logs losses on the training samples only; it does not create a held-out validation split. Raw value predictions on the curated tactical positions have no independent game-outcome labels and must not be described as calibrated. A proper value-calibration study requires a separately held-out, game-level dataset with side-to-move outcome labels; train/validation separation must be by complete self-play game, not by randomly splitting adjacent positions from the same game.

The manual read-only workflow [checkpoint-colour-symmetry-audit.yml](../.github/workflows/checkpoint-colour-symmetry-audit.yml) is intended to run before any training changes. It checks each saved checkpoint against colour-swapped mirrored tactical positions and runs each checkpoint against itself on the fixed 12-opening mirrored suite. It reports policy-distribution divergence, policy/MCTS move equivariance, raw-value symmetry and self-play colour outcomes. It verifies source checkpoint hashes and does not train, modify or promote models.


## Colour-symmetry audit results — workflow 43745391998

The manual read-only audit [43745391998](https://github.com/Nomusa990822/AlphaZero-Style-Chess-AI-Self-Play-Reinforcement-Learning-with-MCTS-and-Policy-Value-Networks/actions/runs/43745391998) completed successfully. It verified the preserved baseline and candidate hashes, evaluated 35 tactical positions and their `python-chess Board.mirror()` colour-swapped counterparts at 25 MCTS simulations, then ran 24 same-checkpoint games across 12 mirrored opening pairs at 50 simulations. Report artifact: [14174652293](https://github.com/Nomusa990822/AlphaZero-Style-Chess-AI-Self-Play-Reinforcement-Learning-with-MCTS-and-Policy-Value-Networks/actions/runs/43745391998/artifacts/14174652293). No training or checkpoint mutation occurred.

The key contract is that training values are stored from the **side-to-move perspective**. For two otherwise equivalent positions related by colour swap and vertical reflection, the expected value is therefore approximately invariant (not sign-inverted). Baseline mean absolute value difference was 0.07374; candidate was 0.79301. Candidate policy top-1 mirror agreement was 1/35 versus baseline 4/35; candidate MCTS move agreement was 6/35 versus baseline 8/35; mean legal-policy JSD was 0.40171 versus baseline 0.31119 nats.

Same-checkpoint self-play produced baseline 1 win / 0 losses / 23 draws and candidate 8 wins / 5 losses / 11 draws. Candidate as White: 2 wins / 3 losses / 7 draws; as Black: 6 wins / 2 losses / 4 draws. These are colour-consistency observations from a small 12-opening suite, not strength estimates.

**Decision:** retain the epoch-0 baseline and keep the epoch-10 candidate unpromoted. Do not start another full training run yet. First trace the side-to-move value contract end-to-end, test mirrored encoder planes and policy action mapping independently, and add known-label mirror-pair tests. Root cause remains undetermined.


## Side-to-move value contract review

The value target is defined from the perspective of the player to move at each stored position. The source path is:

1. SelfPlayGenerator._result_to_white_value() converts the final game result to a White-relative value.
2. SelfPlayGenerator._value_for_player() returns that value for White-to-move samples and negates it for Black-to-move samples.
3. AlphaZeroDataset preserves the scalar; alphazero_loss() compares it directly with the network value using MSE.
4. ModelInference.predict() returns the value head output without changing its sign.
5. MCTS terminal values are side-to-move-relative; backup flips sign at each parent edge; PUCT negates the child Q value when selecting from the parent's perspective.

The source review found no obvious sign inversion across these stages. This does not explain why the epoch-10 candidate's predictions are much less symmetric than the baseline. The encoder uses separate colour planes and absolute board coordinates, while Black move deltas are rotated 180 degrees in the action encoder. The network is not architecturally mirror-equivariant and the inspected training path does not apply mirror augmentation. Those design choices leave symmetry to be learned from data; they are not, on their own, proof of an implementation bug.

The test-only module tests/test_colour_symmetry_contract.py adds regression coverage for mirrored encoder planes, mirrored legal move encoding/decoding, side-to-move outcome-label invariance, MCTS backup sign alternation and terminal-value mirror invariance. It intentionally does not require neural predictions to be exactly mirror-equivariant. No training, checkpoint or promotion behaviour is changed by these tests.


## Self-play dataset capture and comparison

New self-play game records include the complete PGN and a `position_targets`
array. Each entry stores the exact pre-move FEN, zero-based ply, side to move and
final game outcome target from that side's perspective. The logger validates
the target against the final result before persisting it. Existing records
created before this change contain PGNs but no position targets and are
intentionally rejected by the strict comparison tool.

The training workflow artifact now preserves the self-play JSONL log and replay
snapshot/journal as well as model checkpoints. To compare two archived logs:

```bash
python scripts/audit_self_play_datasets.py \
  --baseline path/to/baseline/self_play_games.jsonl \
  --candidate path/to/candidate/self_play_games.jsonl \
  --baseline-label epoch-0-baseline \
  --candidate-label epoch-10-candidate \
  --output reports/self-play-dataset-audit.json
```

The report includes checkpoint SHA-256/configuration metadata, game outcomes
and termination types, total positions, White-to-move and Black-to-move counts,
mean target by side, and target frequencies. It validates PGN legality and consistency between every PGN ply,
FEN, side-to-move label and value target. It is read-only and makes no model
changes. The two inputs must come from separately collected self-play datasets for the
named checkpoints. The manual workflow below generates these inputs from the
preserved checkpoint pair. Historical run artifacts without self-play records
cannot be backfilled from checkpoint weights alone. Split future validation by
complete games, never by individual positions from the same game.


### Generate a matched baseline/candidate diagnostic dataset

The manual workflow
`.github/workflows/self-play-dataset-audit.yml` downloads the immutable
baseline and epoch-10 candidate from preserved training artifact
[43646981876](https://github.com/Nomusa990822/AlphaZero-Style-Chess-AI-Self-Play-Reinforcement-Learning-with-MCTS-and-Policy-Value-Networks/actions/runs/43646981876).
It runs `scripts/generate_self_play_dataset.py` once per checkpoint using the
same seed, CPU device, exploration settings, MCTS simulations and game cap,
then validates and compares the resulting JSONL logs.

The default is eight games per checkpoint, 40 MCTS simulations and a 120-ply
cap. These are intentionally bounded diagnostic settings, not a training run
or a strength evaluation. The workflow is manually dispatched from GitHub
Actions and uploads both raw PGN/position-target datasets and the summary
report for 90 days. The generator loads checkpoints for inference only; it
does not instantiate an optimizer, train weights, overwrite checkpoints or
invoke promotion. Because the sample is small, its outcome counts are
descriptive only. Use the report to inspect data distribution and label
integrity, not to infer Elo or general playing strength.


### Checkpoint integrity gate correction

The first dispatch of the read-only dataset workflow, run 43749569356, failed
at the candidate SHA-256 check. The exact original artifact was downloaded and
both checkpoint files were re-hashed. The baseline digest was correct; the
candidate digest is
`101294ee17c79fd9e4816b3e2676b8f87487c4932172861f59b96550c345af00`.
The workflow pin has been corrected. No inference or dataset generation took
place in the failed run. Re-dispatch the workflow after the fix is merged.


## Self-play dataset audit: standalone script import-path repair

The first post-digest-correction dispatch, [43750026398](https://github.com/Nomusa990822/AlphaZero-Style-Chess-AI-Self-Play-Reinforcement-Learning-with-MCTS-and-Policy-Value-Networks/actions/runs/43750026398), verified both checkpoint hashes but failed when the dataset generator attempted to import the project's `src` package. A script executed from `scripts/` does not automatically receive the repository root on `sys.path`. The generator now derives and inserts the repository root before importing project modules. This is an import/bootstrap-only change; it does not alter inference settings, checkpoints, model weights, training, or promotion. Re-run the manual dataset audit workflow after this repair is merged.
