

## 2026-11-15 — First full two-iteration CPU training run (workflow 43646981876)

- **Workflow:** [Train and preserve model checkpoints run 43646981876](https://github.com/Nomusa990822/AlphaZero-Style-Chess-AI-Self-Play-Reinforcement-Learning-with-MCTS-and-Policy-Value-Networks/actions/runs/43646981876), dispatched from `main` at source revision `43999a6cdaa57777a9a02f25967a9cdb42eced16`; completed successfully on 2026-11-15. All job steps, including training, manifest generation, artifact upload and durable release publication, succeeded.
- **Configuration/execution:** CPU; 2 iterations; 40 self-play games per iteration (80 total); 250-move cap; 80 self-play MCTS simulations; 10 training epochs per iteration (20 total); 24 deterministic, colour-balanced incumbent evaluation games per iteration (48 total). Replay buffer contained 5,352 positions after iteration 1 and 9,516 after iteration 2.
- **Training losses:** iteration 1 final total/policy/value losses were 4.0278 / 3.9777 / 0.0501 (168 batches); iteration 2 final total/policy/value losses were 3.8015 / 3.7330 / 0.0686 (298 batches). Falling training loss documents optimisation on generated data; it is not a playing-strength measure.
- **Candidate evaluation:** iteration 1: W=0, L=12, D=12; score 0.250; one-sided 90% lower confidence bound 0.164. Iteration 2: W=0, L=24, D=0; score 0.000; lower confidence bound 0.000. Both candidates were rejected because neither exceeded the incumbent's 0.50 score nor passed the confidence-bound gate. The second candidate lost all 24 evaluation games.
- **Checkpoint decision:** the incumbent `best_model.pt` was retained unchanged: 3,404,943 bytes; SHA-256 `7a9fdacbd14f6423e34b2edb470d255e15081a12b1e66faf204a5e07e24e4471`. The final `latest_candidate.pt` was preserved separately: 10,193,391 bytes; SHA-256 `101294ee17c79fd9e4816b3e2676b8f87487c4932172861f59b96550c345af00`.
- **Preservation:** Actions artifact [chess-model-checkpoints-43646981876-1](https://github.com/Nomusa990822/AlphaZero-Style-Chess-AI-Self-Play-Reinforcement-Learning-with-MCTS-and-Policy-Value-Networks/actions/runs/43646981876/artifacts/14139456844), artifact ID `14139456844`, 12,556,936 bytes, SHA-256 `da93ad30491960412c38f23970ed1a6f930e7192aef6c15b396872522c1abf70`; durable prerelease [model-checkpoint-43646981876-1](https://github.com/Nomusa990822/AlphaZero-Style-Chess-AI-Self-Play-Reinforcement-Learning-with-MCTS-and-Policy-Value-Networks/releases/tag/model-checkpoint-43646981876-1) contains both checkpoints and `checkpoint-manifest.json`.
- **Interpretation:** This is the first completed full configured training run and confirms that self-play, optimisation, incumbent comparison, rejection, checkpoint integrity manifest and backup publication all execute successfully. Neither candidate demonstrated an improvement over the retained epoch-0 incumbent. No Elo or general playing-strength claim is made. The immutable baseline remains the selected checkpoint.
- **Next:** keep the epoch-0 baseline as incumbent; investigate why candidates underperform before increasing training volume. Use controlled diagnostics and preserve each candidate separately. Do not weaken the promotion gate or promote either candidate.

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



### 2026-11-13 — Fresh-start CPU pipeline pilot (run 43497298757)

- Purpose: validate fresh random initialisation, one bounded self-play/training iteration, candidate evaluation, checkpoint persistence and backup. This is a pipeline smoke test, not a playing-strength experiment.
- Code revision: dbba702569372370a3488a02a4d84024f63e2aac on chess-strength-training-upgrade. [Workflow run](https://github.com/Nomusa990822/AlphaZero-Style-Chess-AI-Self-Play-Reinforcement-Learning-with-MCTS-and-Policy-Value-Networks/actions/runs/43497298757) completed successfully.
- Device: GitHub-hosted Ubuntu runner, CPU PyTorch.
- Configuration: 1 iteration; 4 self-play games; 80-move cap; 8 MCTS simulations; 1 training epoch; batch size 32; 2 colour-swapped candidate evaluation games.
- Self-play: 274 positions; average game length 68.5 moves; results were 1 White win and 3 draws (one move-cap draw, three other games ended by chess rules).
- Training: final total loss 8.0741975; policy loss 7.8813077; value loss 0.1928899. One epoch only.
- Candidate evaluation: 0 wins, 0 losses, 2 draws; score 0.50; 90% lower confidence bound 0.50. Candidate NOT promoted. Two games are far too few to establish strength or Elo.
- Baseline checkpoint best_model.pt: 3,404,943 bytes; SHA-256 7a9fdacbd14f6423e34b2edb470d255e15081a12b1e66faf204a5e07e24e4471.
- Candidate checkpoint latest_candidate.pt: 10,193,391 bytes; SHA-256 3b471702e89659307f11ec95b3f83316ccae7c29a4c7d9d6faa7afaa4f7231a7.
- Artifacts: Actions artifact [14071428532](https://github.com/Nomusa990822/AlphaZero-Style-Chess-AI-Self-Play-Reinforcement-Learning-with-MCTS-and-Policy-Value-Networks/actions/runs/43497298757) (12,562,511 bytes; contains checkpoints, replay buffer, logs and manifest). Durable prerelease [fresh-pilot-checkpoint-43497298757-1](https://github.com/Nomusa990822/AlphaZero-Style-Chess-AI-Self-Play-Reinforcement-Learning-with-MCTS-and-Policy-Value-Networks/releases/tag/fresh-pilot-checkpoint-43497298757-1) contains both checkpoints and manifest.
- Interpretation: fresh-start pipeline, training, evaluation, manifest, artifact upload and prerelease backup all completed. Baseline was retained because the candidate did not pass the promotion gate. This run is not evidence of competent chess play.
- Next: preserve the backup; inspect checkpoint metadata and replay data, then design longer staged training with fixed opponents and substantially larger paired-game evaluation. Do not infer Elo from this pilot.


### 2026-11-13 — Baseline/candidate tactical checkpoint evaluation (run 43503135826)

- **Purpose:** Compare the fresh-start pilot's epoch-0 baseline and epoch-1 candidate on the individual tactical-position corpus and combined tactical-sequence corpus. This is a tactical diagnostic, not a playing-strength match.
- **Workflow/code revision:** [GitHub Actions run 43503135826](https://github.com/Nomusa990822/AlphaZero-Style-Chess-AI-Self-Play-Reinforcement-Learning-with-MCTS-and-Policy-Value-Networks/actions/runs/43503135826), dispatched from `main` at `43a68cebd39271c687adf068859f29ca69462882`; evaluator code and corpora checked out from `chess-strength-training-upgrade`.
- **Execution:** GitHub-hosted Ubuntu CPU; CPU-only PyTorch; deterministic evaluation; 100 MCTS simulations; tactical root filter enabled. Workflow completed successfully and both checkpoint hashes were verified against the release manifest before evaluation.
- **Checkpoint identities:** baseline `best_model.pt`, epoch 0, SHA-256 `7a9fdacbd14f6423e34b2edb470d255e15081a12b1e66faf204a5e07e24e4471`; candidate `latest_candidate.pt`, epoch 1, SHA-256 `3b471702e89659307f11ec95b3f83316ccae7c29a4c7d9d6faa7afaa4f7231a7`.
- **Individual positions (22 total):** baseline 4 correct / 22 = **18.18%**; candidate 5 / 22 = **22.73%**. Both had 0 illegal moves. Baseline by colour: White 2/12, Black 2/10. Candidate by colour: White 2/12, Black 3/10. Candidate's additional correct result is on a small curated corpus; motif-level counts are too small for broad conclusions.
- **Combined sequences (5 total, 7 annotated plies):** both checkpoints matched 3/7 plies = **42.86%**, completed 1/5 sequences = **20%**, and had 0 illegal moves. Both completed the same three-ply removal-of-defender/mating-net sequence; neither completed the other four sequences.
- **Raw report paths in uploaded artifact:** `reports/checkpoint_tactical_evaluation/baseline_positions.json`, `candidate_positions.json`, `baseline_sequences.json`, and `candidate_sequences.json`. Artifact: [checkpoint-tactical-evaluation-43503135826](https://github.com/Nomusa990822/AlphaZero-Style-Chess-AI-Self-Play-Reinforcement-Learning-with-MCTS-and-Policy-Value-Networks/actions/runs/43503135826), ID `14074627894`, 4,597 bytes, expiry 2027-02-11. The original immutable checkpoint release remains [fresh-pilot-checkpoint-43497298757-1](https://github.com/Nomusa990822/AlphaZero-Style-Chess-AI-Self-Play-Reinforcement-Learning-with-MCTS-and-Policy-Value-Networks/releases/tag/fresh-pilot-checkpoint-43497298757-1).
- **Interpretation:** The candidate was one position better on the individual benchmark but tied the baseline on combined-sequence performance. The individual benchmark measures agreement with an annotated acceptable move, not tactical outcome across every defence. The sequence benchmark follows the curated principal variation; opponent replies are prescribed and alternative defences are not exhaustively searched. Twenty-two positions and five sequences are a small diagnostic sample. These scores do not establish overall playing strength or Elo.
- **Checkpoint decision:** No training, checkpoint modification, or promotion occurred. Keep the baseline as the selected checkpoint and retain the candidate separately; do not promote based on this small benchmark difference.
- **Next:** Expand the independently reviewed tactical corpus and add a larger fixed-opponent, colour-balanced match evaluation before making any playing-strength decision.


## Postmortem note — first full-run evaluation protocol

The original 24-game comparison in workflow [43646981876](https://github.com/Nomusa990822/AlphaZero-Style-Chess-AI-Self-Play-Reinforcement-Learning-with-MCTS-and-Policy-Value-Networks/actions/runs/43646981876) used deterministic MCTS from the same standard starting position on every game. Because the models, search, move selection and starting board were unchanged, it replayed the same path for each colour assignment. The 0-24 aggregate therefore represents losses in the two standard-start colour assignments repeated, not 24 distinct opening trials. The result is retained as observed, but its game-level confidence bound must not be interpreted as 24 independent observations or as a general strength estimate.

PR #30 introduces a fixed suite of 12 distinct opening positions and mirrored colour-swapped games. The revised promotion bound is calculated over the 12 opening-pair scores and remains an approximate gate on this fixed suite. The new postmortem workflow can re-evaluate the preserved run-43646981876 checkpoints without training or modifying them. The earlier result is not retroactively re-scored because per-game PGNs and colour-split outcomes were not recorded.


### Additional self-play diagnostic from workflow 43646981876

The 80 self-play games produced 15 White wins, 32 Black wins and 33 draws; four draws ended at the 250-ply cap. Iteration 1 was White 8 / Black 16 / Draw 16 (three move-cap draws); iteration 2 was White 7 / Black 16 / Draw 17 (one move-cap draw). This pronounced colour imbalance is a diagnostic signal to investigate, not proof of an encoder or search bug: only 80 games were played and every game began from the standard position. The previous evaluator did not preserve individual PGNs or per-colour match results, so its 0-24 candidate score cannot be decomposed beyond the two repeated standard-start colour assignments.


## 2026-11-15 — Read-only postmortem of full training run 43646981876 (diagnostic run 43662614909)

- **Workflow:** [Checkpoint run postmortem 43662614909](https://github.com/Nomusa990822/AlphaZero-Style-Chess-AI-Self-Play-Reinforcement-Learning-with-MCTS-and-Policy-Value-Networks/actions/runs/43662614909) completed successfully on main revision 6074fd1c7656dfe6ed223bf9bde5675b39b5fdb4. All steps succeeded, including checkpoint download/hash verification, 24-game paired-opening evaluation, policy/value/MCTS diagnostics, fixed tactical benchmarks and artifact upload. The workflow is read-only: no training, checkpoint write, or promotion occurred.
- **Preserved report artifact:** [checkpoint-run-postmortem-43646981876-43662614909](https://github.com/Nomusa990822/AlphaZero-Style-Chess-AI-Self-Play-Reinforcement-Learning-with-MCTS-and-Policy-Value-Networks/actions/runs/43662614909/artifacts/14141986519), artifact ID 14141986519, 23,281 bytes; SHA-256 03a211d6465bc026a681e4ed42352c29f33539bce75b8cb973050a8ba3d246ec. It contains paired-match, behaviour, baseline/candidate tactical-position and baseline/candidate tactical-sequence JSON reports.
- **Checkpoint identity verified:** epoch-0 baseline best_model.pt, SHA-256 7a9fdacbd14f6423e34b2edb470d255e15081a12b1e66faf204a5e07e24e4471; epoch-10 candidate latest_candidate.pt, SHA-256 101294ee17c79fd9e4816b3e2676b8f87487c4932172861f59b96550c345af00.
- **Corrected paired-opening match:** 24 games across 12 distinct mirrored opening pairs; candidate score **0.500** (1 win, 1 loss, 22 draws); one-sided 90% paired lower confidence bound **0.4494**. Candidate as White: 0 wins, 0 losses, 12 draws. Candidate as Black: 1 win, 1 loss, 10 draws. All 12 opening pairs were scored. Candidate did **not** exceed 0.50 and the lower bound did not exceed 0.50; promotion correctly rejected. This is a fixed-suite result against this exact opponent/search/opening configuration, not an Elo estimate.
- **Policy/value/MCTS diagnostic (35 positions, 25 simulations):** baseline policy top-1 1/35 (2.86%) and MCTS 6/35 (17.14%); candidate policy top-1 3/35 (8.57%) and MCTS 8/35 (22.86%). Both produced zero illegal moves. Candidate MCTS gains were modest (+2 positions overall), with no Black-to-move MCTS gain (both 3/16); White-to-move improved from 3/19 to 5/19. Candidate endgame tactical-position accuracy increased 1/7 to 3/7, while middlegame remained 5/28. These small curated counts are diagnostic only.
- **Annotated sequences (11 sequences, 13 attempted plies):** baseline and candidate both matched 3/13 plies (23.08%) and completed 1/11 sequences (9.09%); zero illegal moves. The candidate did not improve this sequence-following metric. It measures agreement with one annotated line, not proof that a line is forced.
- **Interpretation:** There is a small positive signal on the individual tactical-position benchmark and policy top-1 agreement, but no improvement on sequence completion and no demonstrated head-to-head advantage over the incumbent. The evidence does not justify checkpoint promotion, an Elo/strength claim, or another full training run yet. The epoch-0 checkpoint remains incumbent; the epoch-10 candidate remains an unpromoted artifact.
- **Next diagnostic focus:** inspect colour/asymmetric self-play and evaluation behaviour, tactical-search selection, policy/value calibration and the cold-start iteration design. In particular, the candidate's White tactical-position score improved while Black did not; investigate this with targeted paired tests rather than changing the promotion gate. Keep the next training run on hold until the diagnosis and a controlled corrective plan are documented.
