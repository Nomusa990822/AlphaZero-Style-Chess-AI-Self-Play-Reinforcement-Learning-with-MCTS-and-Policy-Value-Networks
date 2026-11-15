# Independent confirmatory v2 — execution record

- Workflow: [43759687103](https://github.com/Nomusa990822/AlphaZero-Style-Chess-AI-Self-Play-Reinforcement-Learning-with-MCTS-and-Policy-Value-Networks/actions/runs/43759687103)
- Status: completed successfully (workflow execution); **promotion evidence gate failed**
- Source commit: `d84015b8cfe4de536065cbf284d033bbe99e2ca3`
- Artifact: [14180972985](https://github.com/Nomusa990822/AlphaZero-Style-Chess-AI-Self-Play-Reinforcement-Learning-with-MCTS-and-Policy-Value-Networks/actions/runs/43759687103/artifacts/14180972985) (90-day retention)
- Artifact ZIP SHA-256: `3b46237e3bd8c3a83a785d8b7c1bb00f7f2b75f2546cdfd4d9406b15e61d3c8e`
- Suite SHA-256: `69d2582e175bf0a4bfd2867537ea7de4e43f0cfe0a2dfdc5ca6f6d5e0c2fff03`
- RNG seed: `20261116`
- Settings: CPU, 50 MCTS simulations, Dirichlet noise disabled, temperature 0.0, 200-ply cap.
- Checkpoints: epoch-0 incumbent SHA-256 `7a9fdacbd14f6423e34b2edb470d255e15081a12b1e66faf204a5e07e24e4471`; epoch-10 candidate SHA-256 `101294ee17c79fd9e4816b3e2676b8f87487c4932172861f59b96550c345af00`. Both match the previously pinned immutable checkpoints.

## Results

| Measure | Result |
|---|---:|
| Opening pairs / games | 24 / 48 |
| Candidate score / paired mean | 0.4791666667 (47.92%) |
| Paired-score sample SD | 0.2074255585 |
| One-sided 90% Student-t LCB (df=23) | 0.4232999850 |
| Wins / draws / losses | 6 / 34 / 8 |
| Candidate as White | 1W / 19D / 4L; 35.42% |
| Candidate as Black | 5W / 15D / 4L; 52.08% |
| Chess-rule endings | 45 |
| 200-ply cap draws | 3 |
| Promotion evidence eligible | **No** |

The aggregate score is below 0.50 and the paired lower confidence bound is below 0.50. Both primary numerical promotion conditions fail. Candidate-as-White scored below the protocol's 0.40 human-review threshold (35.42%); candidate-as-Black scored 52.08%. The colour split is materially inconsistent with v1, where the candidate scored 58.33% as White and 52.08% as Black.

## Artifact reconciliation

The downloaded report artifact was inspected. It contains 48 game records, 24 unique opening IDs and all 48 expected opening/colour legs. The UCI move-list length equals the recorded ply count for every game. Recomputed pair scores from the raw per-game outcomes reproduce the report's aggregate mean and sample standard deviation. Termination metadata reconciles to 45 chess-rule endings and 3 move-cap draws.

This post-run reconciliation did not independently replay every UCI move in a separate chess library; it checked the report's record structure, move counts, pair-score arithmetic and metadata. The workflow's evaluator is responsible for legal-move enforcement during execution. The JSON report does not expose a separate illegal-move-count field, which is recorded as a reporting limitation for a future tooling improvement.

## Decision

**Do not promote epoch 10.** Keep epoch 0 as incumbent and preserve epoch 10 as an unpromoted candidate. Do not pool v1 and v2 after observing their results: they are separate frozen-suite experiments. v1 passed narrowly (55.21%, LCB 50.78%), while v2 failed (47.92%, LCB 42.33%). The independent result does not replicate the v1 advantage.

No training, optimizer step, checkpoint write, incumbent replacement or promotion occurred in this evaluation. The next work should be diagnostic rather than another immediate promotion test: inspect the v2 White-side losses and full PGNs, investigate the reversal in colour performance, and review the cold-start training/data limitations before designing a new candidate. Any future candidate requires a newly frozen independent suite after development against the existing suites.


## Follow-up: candidate-as-White loss review

A qualitative review of all four candidate-as-White losses is documented in [V2_WHITE_LOSS_DIAGNOSTIC_2026-11-15.md](V2_WHITE_LOSS_DIAGNOSTIC_2026-11-15.md). The recorded games show recurring unsafe king placement/king walks, poor coordination and tactical oversights involving a queen, bishop and rook. This is descriptive only: no Stockfish analysis or independent python-chess replay was completed, and no centipawn-loss claims are made. The four games are not a representative sample of all White-side play. Checkpoint preservation and the no-promotion decision remain unchanged.
