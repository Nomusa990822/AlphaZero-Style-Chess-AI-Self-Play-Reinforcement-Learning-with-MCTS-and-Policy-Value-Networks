"""Evaluate two preserved checkpoints with paired, colour-swapped opening matches."""
from __future__ import annotations
import argparse
import hashlib
import json
import sys
from pathlib import Path

# Running a script from scripts/ puts that directory, not the repository root,
# at sys.path[0]. Add the project root so src.* imports work in clean CI jobs.
PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))
from src.engine.encoder import BoardEncoder
from src.engine.move_encoding import MoveEncoding
from src.mcts.search import MCTSConfig
from src.model.inference import ModelInference
from src.model.network import AlphaZeroNet, NetworkConfig
from src.training.checkpoint import load_checkpoint
from src.training.evaluator import NetworkEvaluator


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def load_inference(path: Path, encoding: MoveEncoding):
    model = AlphaZeroNet(
        action_size=encoding.action_size,
        config=NetworkConfig(input_channels=20, board_size=8, num_filters=64, num_res_blocks=3, value_hidden_size=128),
    )
    payload = load_checkpoint(path, model, optimizer=None, map_location="cpu")
    model.eval()
    metadata = {"filename": path.name, "size_bytes": path.stat().st_size, "sha256": sha256_file(path), "epoch": payload.get("epoch"), "extra": payload.get("extra", {})}
    return ModelInference(model, encoding, BoardEncoder(), device="cpu"), metadata


def parse_args():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--baseline", required=True, type=Path)
    parser.add_argument("--candidate", required=True, type=Path)
    parser.add_argument("--simulations", type=int, default=100)
    parser.add_argument("--games", type=int, default=24)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    if args.simulations < 1:
        parser.error("simulations must be positive")
    if args.games < 2 or args.games % 2:
        parser.error("games must be an even number of at least 2")
    return args


def main():
    args = parse_args()
    for path in (args.baseline, args.candidate):
        if not path.is_file() or path.stat().st_size == 0:
            raise FileNotFoundError(f"Checkpoint missing or empty: {path}")
    encoding = MoveEncoding()
    baseline, baseline_metadata = load_inference(args.baseline, encoding)
    candidate, candidate_metadata = load_inference(args.candidate, encoding)
    evaluator = NetworkEvaluator(encoding, MCTSConfig(num_simulations=args.simulations, add_dirichlet_noise=False, temperature=0.0))
    promoted, result = evaluator.should_promote_candidate(candidate, baseline, num_games=args.games)
    report = {
        "schema_version": 1,
        "evaluation": "paired_opening_checkpoint_match",
        "settings": {
            "device": "cpu",
            "simulations_per_move": args.simulations,
            "games": args.games,
            "opening_pairs": len(result.opening_pair_scores),
            "max_plies_per_game": 200,
            "dirichlet_noise": False,
            "move_temperature": 0.0,
            "opening_suite": "benchmarks/evaluation_openings.jsonl",
            "opening_suite_ids": list(result.opening_ids),
            "paired_protocol": "each opening played twice; candidate as White, then as Black from mirrored position",
        },
        "baseline": baseline_metadata,
        "candidate": candidate_metadata,
        "result": {
            "wins": result.wins, "losses": result.losses, "draws": result.draws,
            "games_played": result.games_played, "score": result.score,
            "one_sided_90_percent_lower_confidence_bound": result.lower_confidence_bound,
            "candidate_colour_breakdown": result.colour_breakdown,
            "opening_pair_scores": list(result.opening_pair_scores),
            "opening_pair_results": list(result.opening_pair_results),
        },
        "promotion_eligible": promoted,
        "promotion_rejection_reasons": evaluator.promotion_rejection_reasons(result),
        "interpretation_limits": [
            "This is a fixed 12-opening paired comparison, not an Elo rating.",
            "The lower-bound estimate reflects variation across the 12 distinct opening-pair scores; it is an approximate gate on this fixed suite, not a population-strength estimate.",
            "The result is relative to this exact opponent, search configuration and opening suite.",
        ],
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2, sort_keys=True))
    print(f"Saved paired-opening evaluation: {args.output}")


if __name__ == "__main__":
    main()
