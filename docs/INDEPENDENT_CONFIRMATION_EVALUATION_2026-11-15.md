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

## Independent suite v2 — completed; promotion gate failed

Workflow [43759687103](https://github.com/Nomusa990822/AlphaZero-Style-Chess-AI-Self-Play-Reinforcement-Learning-with-MCTS-and-Policy-Value-Networks/actions/runs/43759687103) completed successfully on source commit `d84015b8cfe4de536065cbf284d033bbe99e2ca3`. The raw report artifact is [14180972985](https://github.com/Nomusa990822/AlphaZero-Style-Chess-AI-Self-Play-Reinforcement-Learning-with-MCTS-and-Policy-Value-Networks/actions/runs/43759687103/artifacts/14180972985), ZIP SHA-256 `3b46237e3bd8c3a83a785d8b7c1bb00f7f2b75f2546cdfd4d9406b15e61d3c8e`. The frozen suite hash was verified as `69d2582e175bf0a4bfd2867537ea7de4e43f0cfe0a2dfdc5ca6f6d5e0c2fff03`; seed `20261116`; same pinned checkpoint hashes and match settings as v1.

| Measure | v2 result |
|---|---:|
| Candidate score / paired mean | 47.92% |
| Paired-score SD | 0.2074255585 |
| One-sided 90% Student-t LCB | 42.33% |
| Wins / draws / losses | 6 / 34 / 8 |
| Candidate as White | 1W / 19D / 4L (35.42%) |
| Candidate as Black | 5W / 15D / 4L (52.08%) |
| Chess-rule endings / 200-ply cap draws | 45 / 3 |
| Promotion evidence eligible | No |

Both primary numerical promotion conditions fail: the aggregate score and lower confidence bound are below 0.50. The White score is below the protocol's 0.40 human-review threshold. This colour split reverses v1's White result (58.33%); it requires diagnosis rather than averaging away. Do not pool v1 and v2 post hoc. The independent v2 artifact was reconciled: 48 records, 24 unique openings, all 48 colour legs, UCI counts matching ply counts, and recomputed pair-score mean/SD matching the report. This reconciliation did not independently replay all UCI moves in a separate chess library; the report also lacks an explicit illegal-move-count field. See [the detailed v2 execution record](../docs/INDEPENDENT_CONFIRMATION_V2_RESULTS_2026-11-15.md).

**Decision: do not promote.** Epoch 0 remains incumbent; epoch 10 remains unpromoted. No training or checkpoint mutation occurred. Next work is diagnostic review of the v2 White-side losses, full PGNs, colour-performance reversal and cold-start data/training limitations.
