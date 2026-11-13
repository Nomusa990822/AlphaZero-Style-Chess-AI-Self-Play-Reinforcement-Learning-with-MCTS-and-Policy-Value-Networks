"""Resource-bounded sweep of MCTS tactical-search configurations."""
from __future__ import annotations
import argparse, hashlib, json
from pathlib import Path
from time import perf_counter
import chess, torch
from src.engine.encoder import BoardEncoder
from src.engine.move_encoding import MoveEncoding
from src.mcts.search import MCTS, MCTSConfig
from src.model.inference import ModelInference
from src.model.network import AlphaZeroNet, NetworkConfig
from src.training.checkpoint import load_checkpoint
from src.training.tactical_benchmark import evaluate_tactical_selector, load_tactical_positions


def parse_ints(value: str, option: str) -> list[int]:
    try:
        values = [int(part.strip()) for part in value.split(",")]
    except ValueError as exc:
        raise argparse.ArgumentTypeError(f"{option} must be comma-separated integers") from exc
    if not values or any(v < 1 for v in values) or len(set(values)) != len(values):
        raise argparse.ArgumentTypeError(f"{option} values must be unique positive integers")
    return values


def parse_floats(value: str, option: str) -> list[float]:
    try:
        values = [float(part.strip()) for part in value.split(",")]
    except ValueError as exc:
        raise argparse.ArgumentTypeError(f"{option} must be comma-separated numbers") from exc
    if not values or any(v <= 0 for v in values) or len(set(values)) != len(values):
        raise argparse.ArgumentTypeError(f"{option} values must be unique positive numbers")
    return values


def estimate_simulations(position_count: int, budgets: list[int], cpuct_values: list[float]) -> int:
    """Count planned simulations over all configurations and both filter modes."""
    if position_count < 1 or not budgets or not cpuct_values:
        raise ValueError("positions, simulation budgets and c_puct values must be non-empty")
    return position_count * sum(budgets) * len(cpuct_values) * 2


def resolve_device(requested: str) -> torch.device:
    if requested != "auto":
        device = torch.device(requested)
        if device.type == "cuda" and not torch.cuda.is_available():
            raise RuntimeError("CUDA was requested but is unavailable.")
        if device.type == "mps" and not (hasattr(torch.backends, "mps") and torch.backends.mps.is_available()):
            raise RuntimeError("MPS was requested but is unavailable.")
        return device
    if torch.cuda.is_available(): return torch.device("cuda")
    if hasattr(torch.backends, "mps") and torch.backends.mps.is_available(): return torch.device("mps")
    return torch.device("cpu")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--checkpoint", required=True)
    parser.add_argument("--positions", default="benchmarks/tactical_positions.jsonl")
    parser.add_argument("--simulations", default="25,50")
    parser.add_argument("--c-puct", default="1.0,1.5")
    parser.add_argument("--max-positions", type=int, default=13)
    parser.add_argument("--max-total-simulations", type=int, default=5000)
    parser.add_argument("--device", default="auto")
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    try:
        args.simulations = parse_ints(args.simulations, "--simulations")
        args.c_puct = parse_floats(args.c_puct, "--c-puct")
    except argparse.ArgumentTypeError as exc:
        parser.error(str(exc))
    if args.max_positions < 1 or args.max_total_simulations < 1:
        parser.error("position and simulation caps must be positive")
    return args


def main() -> None:
    args = parse_args()
    checkpoint = Path(args.checkpoint)
    if not checkpoint.is_file(): raise FileNotFoundError(f"Checkpoint not found: {checkpoint}")
    positions = load_tactical_positions(args.positions)[:args.max_positions]
    if not positions: raise ValueError("The selected tactical corpus contains no positions.")
    planned = estimate_simulations(len(positions), args.simulations, args.c_puct)
    if planned > args.max_total_simulations:
        raise ValueError(f"Planned budget {planned} exceeds cap {args.max_total_simulations}; reduce the grid or positions.")
    device = resolve_device(args.device)
    digest = hashlib.sha256(checkpoint.read_bytes()).hexdigest()
    encoding = MoveEncoding()
    network = AlphaZeroNet(action_size=encoding.action_size, config=NetworkConfig(
        input_channels=20, board_size=8, num_filters=64, num_res_blocks=3, value_hidden_size=128))
    payload = load_checkpoint(checkpoint, network, optimizer=None, map_location=device)
    inference = ModelInference(model=network, move_encoding=encoding, encoder=BoardEncoder(), device=device)
    results, all_started = [], perf_counter()
    for simulations in args.simulations:
        for c_puct in args.c_puct:
            for filter_enabled in (True, False):
                search = MCTS(inference=inference, move_encoding=encoding, config=MCTSConfig(
                    num_simulations=simulations, c_puct=c_puct, add_dirichlet_noise=False,
                    temperature=0.0, use_tactical_root_filter=filter_enabled))
                selected, rows, started = {}, [], perf_counter()
                for case in positions:
                    board = chess.Board(case.fen)
                    move = search.select_action(search.run(board.copy(stack=True)), temperature=0.0)
                    selected[case.fen] = move.uci()
                    rows.append({"id": case.position_id, "selected_move": move.uci(),
                                 "correct": move.uci() in case.acceptable_moves})
                elapsed = perf_counter() - started
                score = evaluate_tactical_selector(positions, lambda board, m=selected: m[board.fen()])
                results.append({
                    "simulations_per_position": simulations, "c_puct": c_puct,
                    "tactical_root_filter": filter_enabled, "positions": len(positions),
                    "total_simulations": len(positions) * simulations,
                    "correct": score.correct, "accuracy": score.accuracy, "illegal": score.illegal,
                    "by_motif": score.by_motif, "by_color": score.by_color, "by_phase": score.by_phase,
                    "failures": list(score.failures), "elapsed_seconds": round(elapsed, 6),
                    "selections": rows})
    report = {
        "checkpoint": str(checkpoint), "checkpoint_sha256": digest,
        "checkpoint_epoch": payload.get("epoch"), "corpus": str(args.positions),
        "positions_evaluated": len(positions), "device": str(device),
        "dirichlet_noise": False, "temperature": 0.0,
        "simulation_budgets": args.simulations, "c_puct_values": args.c_puct,
        "planned_total_simulations": planned, "maximum_total_simulations": args.max_total_simulations,
        "elapsed_seconds": round(perf_counter() - all_started, 6), "configurations": results,
        "interpretation_limit": "A small curated tactical corpus is diagnostic only, not an Elo estimate or proof of general playing-strength improvement."}
    rendered = json.dumps(report, indent=2, sort_keys=True)
    print(rendered)
    output = Path(args.output); output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(rendered + "\n", encoding="utf-8")
    print(f"Saved bounded search benchmark: {output}")


if __name__ == "__main__":
    main()
