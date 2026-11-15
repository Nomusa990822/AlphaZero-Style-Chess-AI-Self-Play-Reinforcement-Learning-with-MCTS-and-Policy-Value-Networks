# Independent confirmatory checkpoint evaluation — 2026-11-15

## Scope and checkpoint identities

This record tracks the first frozen confirmatory comparison and the follow-up independent opening suite. Both evaluations are read-only CPU inference comparisons of the same preserved checkpoints; neither workflow trains, writes checkpoints, changes the incumbent, or promotes a candidate.

| Role | Checkpoint | SHA-256 |
|---|---|---|
| Incumbent | epoch-0 `best_model.pt` | `7a9fdacbd14f6423e34b2edb470d255e15081a12b1e66faf204a5e07e24e4471` |
| Candidate | epoch-10 `latest_candidate.pt` | `101294ee17c79fd9e4816b3e2676b8f87487c4932172861f59b96550c345af00` |

The incumbent is explicitly identified in checkpoint metadata as a random-initialisation baseline. The candidate is epoch 10, iteration 2. This comparison therefore measures the candidate relative to that preserved baseline, not against a strong external opponent.

## Confirmatory v1 — completed

- Workflow: [43755129081](https://github.com/Nomusa990822/AlphaZero-Style-Chess-AI-Self-Play-Reinforcement-Learning-with-MCTS-and-Policy-Value-Networks/actions/runs/43755129081)
- Source commit: `727639e75b7defcad5a915473258b1f13bf94389`
- Artifact: [14179310181](https://github.com/Nomusa990822/AlphaZero-Style-Chess-AI-Self-Play-Reinforcement-Learning-with-MCTS-and-Policy-Value-Networks/actions/runs/43755129081/artifacts/14179310181)
- Artifact ZIP SHA-256: `c87d5af9486a30545e3a246823bd54ee5533d7e86bd44aebb38ec00695f8ce61`
- Opening suite: `benchmarks/evaluation_openings_confirmatory_v1.jsonl`
- Opening-suite SHA-256: `896c7a09997b18d848f1e4452da75dec151c3a4960fac780ad379694859813ca`
- Protocol: 24 opening pairs / 48 games; candidate played each colour once per pair; CPU; 50 MCTS simulations; no Dirichlet noise; temperature 0.0; 200-ply cap.

### Results

| Measure | Result |
|---|---:|
| Candidate score | 0.5520833333 (55.21%) |
| Paired-score mean | 0.5520833333 |
| Paired-score sample SD | 0.1645013325 |
| One-sided 90% Student-t LCB (df=23) | 0.5077775899 |
| Wins / draws / losses | 7 / 39 / 2 |
| Games / opening pairs | 48 / 24 |
| Move-cap draws | 0 |
| Chess-rule endings | 48 |

| Candidate colour | Wins | Draws | Losses | Score |
|---|---:|---:|---:|---:|
| White | 4 | 20 | 0 | 0.5833 |
| Black | 3 | 19 | 2 | 0.5208 |

Both the aggregate score and paired lower confidence bound exceeded 0.50. The workflow completed all 48 game records; an illegal move would have aborted the run. Both pinned checkpoint digests were verified before evaluation. The workflow and report were successful.

### Interpretation and decision

The run passes the numerical promotion-evidence threshold for this frozen suite. The margin is narrow: the lower bound is approximately 0.78 percentage points above 0.50. The suite is curated, not a random sample of chess positions; this is not an Elo estimate, an external-strength measurement, or a value-calibration study. White's score was higher than Black's, so colour-specific outcomes must remain visible in any decision.

**Decision: do not promote yet.** Preserve epoch 0 as incumbent and epoch 10 as candidate. Obtain an independent second opening-suite result before making a promotion decision.

## Independent suite v2 — merged, ready for manual dispatch

- Suite: `benchmarks/evaluation_openings_independent_v2.jsonl`
- Version: `independent_v2`
- SHA-256: `69d2582e175bf0a4bfd2867537ea7de4e43f0cfe0a2dfdc5ca6f6d5e0c2fff03`
- 24 opening positions across 9 labelled families; maximum 4 positions per family.
- The loader validates legal UCI replay, non-terminal valid positions, unique IDs/FENs, family constraints, and disjointness from the development suite, tactical corpus, and confirmatory v1.
- Uses the same fixed checkpoints and match settings as v1, so only the opening sample changes. NumPy, Python and PyTorch RNGs are seeded with `20261116`; the workflow checks the exact suite SHA-256 before model loading and records the seed/runtime metadata in the report.
- Workflow: `.github/workflows/independent-confirmation-v2.yml`; manual dispatch only, main branch only, explicit YES, CPU inference-only, hash-pinned checkpoints, 90-day report artifact.

PR #46 merged at `cbf96a41089efbbb2f23a51d1b1c12a05e72657d`. Required checks passed: [CPU suite 43759061879](${repoUrl}/actions/runs/43759061879) completed with **221 tests passed**; [Stockfish audit 43759061894](${repoUrl}/actions/runs/43759061894) supported **35/35 positions and 11/11 sequences with zero flagged entries** (artifact [14179282087](${repoUrl}/actions/runs/43759061894/artifacts/14179282087)). The v2 workflow is now available on `main` and awaits manual dispatch with `confirm_evaluation=YES`. It pins suite SHA-256 `69d2582e175bf0a4bfd2867537ea7de4e43f0cfe0a2dfdc5ca6f6d5e0c2fff03` and uses RNG seed `20261116`. The v2 workflow has not yet been run. The second result will be reported alongside v1, not pooled with it as if the two suites were one predeclared 48-pair sample. Any future promotion decision requires human review of both reports and the colour splits. No training or checkpoint mutation is part of this work.
