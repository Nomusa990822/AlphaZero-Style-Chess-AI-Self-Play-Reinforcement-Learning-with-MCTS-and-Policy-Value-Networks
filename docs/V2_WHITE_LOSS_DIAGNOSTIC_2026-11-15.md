# Independent confirmation v2 — candidate-as-White loss diagnostic

Date: 2026-11-15

## Scope and evidence

This is a qualitative review of the four v2 evaluation games in which the epoch-10 candidate played White and lost. Source: workflow [43759687103](https://github.com/Nomusa990822/AlphaZero-Style-Chess-AI-Self-Play-Reinforcement-Learning-with-MCTS-and-Policy-Value-Networks/actions/runs/43759687103), artifact [14180972985](https://github.com/Nomusa990822/AlphaZero-Style-Chess-AI-Self-Play-Reinforcement-Learning-with-MCTS-and-Policy-Value-Networks/actions/runs/43759687103/artifacts/14180972985). Downloaded ZIP SHA-256: `3b46237e3bd8c3a83a785d8b7c1bb00f7f2b75f2546cdfd4d9406b15e61d3c8e`.

The four records were selected by candidate_white leg and loss outcome. Their stored PGN scores and UCI move lists were inspected. The artifact as a whole contains 48 records and the UCI-list lengths reconcile with the recorded ply counts, but this diagnostic did not independently replay each move with python-chess and did not run Stockfish on the games. Accordingly, the notes below are descriptive observations from the stored game scores, not engine-confirmed blunder classifications.

## Game-by-game review

### v2-01-sicilian-taimanov — 44 plies

The candidate's king leaves the normal safety of the back rank early: 17.Kf2, 18.Ke3, 23.Kd4, 25.Kc5 and 26.Kd5. White's pieces are not coordinated sufficiently to protect the exposed king. Black finishes with 26...Be6#.

**Observed failure mode:** king safety and development. The decisive feature is the king walking into a mating net rather than securing itself and coordinating the remaining pieces.

### v2-14-kings-indian — 110 plies

White's queen repeatedly changes squares around c3/e3. After 27.Qe3, Black plays 27...Nxe3 and captures the queen on e3. The game continues and ends in checkmate.

**Observed failure mode:** direct tactical oversight / queen left en prise. The move sequence is concrete evidence that the candidate failed to preserve its queen in this position; engine analysis is still needed to determine the earliest avoidable error and whether the capture was forced.

### v2-18-english-reversed — 30 plies

After 7.Be3, Black replies 7...dxe3, capturing White's bishop with the d-pawn. Later Black's queen enters with 17...Qxb1+ and 18...Qxc1#, exploiting White's exposed back rank and queen placement.

**Observed failure mode:** material awareness and king safety. White loses a minor piece early and then permits a short mating sequence involving the back rank.

### v2-21-dutch — 136 plies

White's king moves into the centre early (4.Nh3 Kf7, 7.Kf2 and subsequent king manoeuvres). The rooks then spend many moves shuffling rather than coordinating. On move 69 Black plays 69...gxf4, capturing White's rook on f4; the game ends shortly afterwards with 71...Qd2#.

**Observed failure mode:** king exposure, poor piece coordination and a hanging rook. The final phase combines a material loss with a mating attack.

## Cross-game synthesis

Across these four selected losses, three recurring themes are visible:

1. **King safety is repeatedly compromised.** In the Taimanov and Dutch games especially, the candidate walks its king into the centre while the opponent retains attacking resources.
2. **High-value pieces are not consistently protected.** The King's Indian queen is captured by a knight; the English bishop is taken by a pawn; the Dutch rook is captured by a pawn.
3. **Development and coordination are weak in the critical phases.** Several moves are spent on king or rook manoeuvres while pieces remain poorly coordinated, leaving tactical targets and mating lines available.

These are hypotheses for targeted investigation, not proof that the model has one systematic defect. The four losses are a selected sample of four games, not a representative estimate of all candidate-White decisions. The v2 aggregate remains 1 win, 19 draws and 4 losses as White (35.42%); this qualitative review does not alter the score or promotion decision.

## Limitations

- No Stockfish search was run on these four PGNs; no evaluation swing, centipawn loss, forced-mate distance or best-move claim is reported.
- No independent python-chess replay of every UCI move was completed in this review. The original evaluator checks each selected move against board.legal_moves before pushing it, but the exported JSON does not contain a separate illegal-move count.
- The opening suite is fixed and curated. These four games do not support Elo or general playing-strength conclusions.
- The colour split is a diagnostic signal, not proof of a colour-encoding defect.

## Decision and next step

Keep epoch 0 as incumbent and epoch 10 as an unpromoted candidate. Do not train, write checkpoints or promote based on this review. The next useful diagnostic is a reproducible Stockfish-backed, move-by-move analysis of these four losses and a matched sample of candidate-White draws and the single candidate-White win. That comparison should distinguish opening/development issues from tactical blunders and later endgame failures before any training change is proposed.

## Engine-backed comparison — workflow prepared

A follow-up workflow and runner are now prepared to compare all four losses against four predeclared draw controls and the only candidate-White win. The controls are `v2-02-sicilian-kan`, `v2-13-london`, `v2-17-english-symmetrical`, and `v2-22-pirc`; the win is `v2-23-modern`. The runner will validate the stored FEN/UCI/PGN move sequence and analyse every ply with Stockfish at fixed depth 12. It will report played-move loss, best-move/PV and summaries separately for candidate-White and incumbent-Black moves.

The workflow is manual and has not yet been run. These are the predeclared controls, not findings. The qualitative observations above remain unverified by an engine until the workflow completes. No training, checkpoint mutation or promotion is authorized.


## First engine-review workflow attempt — blocked by PGN/FEN alignment

Workflow [43764823179](https://github.com/Nomusa990822/AlphaZero-Style-Chess-AI-Self-Play-Reinforcement-Learning-with-MCTS-and-Policy-Value-Networks/actions/runs/43764823179) completed with failure before Stockfish analysis or artifact upload. The pinned source artifact and its immutable identifiers passed verification. The replay runner then found that the PGN contains the complete game from the standard opening position, while each record's UCI list begins at its recorded post-opening starting_fen. For the first selected game, this meant 52 PGN SAN moves versus 44 UCI continuation moves; the final SAN and UCI move were consistent, but the runner incorrectly compared the full PGN against the continuation-only UCI list.

This is a replay alignment defect in the review script, not evidence of an illegal move or a model defect. The source artifact has not been modified. The correction must parse and validate the PGN main line, locate the exact recorded starting FEN within that line, and compare only the remaining SAN continuation against the UCI list. The full game must remain legally replayable, and all existing checkpoint, suite, and result integrity checks must remain in force.

No Stockfish scores were produced, no analysis artifact was uploaded, and no training, optimizer update, checkpoint write or promotion occurred. The epoch-0 incumbent remains unchanged and epoch 10 remains unpromoted. The workflow must be rerun after the parser correction is merged.


## Stockfish review run 43765868151 — completed, score aggregation correction required

The repaired review workflow [43765868151](https://github.com/Nomusa990822/AlphaZero-Style-Chess-AI-Self-Play-Reinforcement-Learning-with-MCTS-and-Policy-Value-Networks/actions/runs/43765868151) completed successfully and uploaded artifact [14182093603](https://github.com/Nomusa990822/AlphaZero-Style-Chess-AI-Self-Play-Reinforcement-Learning-with-MCTS-and-Policy-Value-Networks/actions/runs/43765868151/artifacts/14182093603). It replayed the nine preselected games and ran Stockfish 17.1 at depth 12, one thread, 256 MB hash. The full move-level JSON is retained in the artifact.

Post-run inspection found a reporting defect: the runner converts mate scores to the artificial value 100,000 centipawns via `score(mate_score=100_000)`, then includes those sentinel values in centipawn-loss means and maxima. The artifact contains numerous values around 99,000–100,500 CP, including in drawn and won games. Those are mate-score encodings, not meaningful centipawn losses. Consequently the current mean/max CPL aggregates and comparisons by outcome must not be interpreted. The move-level records and principal variations remain available, but the score fields need a corrected representation.

A follow-up correction is being prepared to store centipawn scores and mate distances separately, set CPL to null whenever either compared score is mate, and exclude such rows from finite-CP aggregates while counting them separately. Until a corrected report is generated, no conclusion about whether the four White losses show more engine-measured blunders than the draw controls or White win is warranted. This is a reporting/interpretation issue, not a training or checkpoint change. Epoch 0 remains incumbent; epoch 10 remains unpromoted.


## Mate-score reporting correction merged — PR #52

PR [#52](https://github.com/Nomusa990822/AlphaZero-Style-Chess-AI-Self-Play-Reinforcement-Learning-with-MCTS-and-Policy-Value-Networks/pull/52) is merged at `5181bf316aa20185a0c7669cbd8e287da06f7c5a`. It replaces the artificial 100,000-CP mate sentinel with separate centipawn and mate-distance fields. A move's CPL is null whenever either compared score is mate; finite-CP summaries now exclude those rows and count them separately. Outcome-level White CPL is pooled over finite move comparisons rather than averaging per-game means. The CPU test suite and Stockfish tactical audit both passed. The original artifact 14182093603 remains immutable and its contaminated CPL means/maxima must not be used. A fresh manual dispatch is required to produce the corrected report. No training or checkpoint mutation occurred; epoch 0 remains incumbent and epoch 10 remains unpromoted.
