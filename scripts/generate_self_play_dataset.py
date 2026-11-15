"""Generate a self-play dataset from one immutable checkpoint (inference only)."""
from __future__ import annotations

import argparse
import hashlib
import json
import random
import time
from pathlib import Path

import numpy as np
import torch

from src.engine.encoder import BoardEncoder
from src.engine.move_encoding import MoveEncoding
from src.mcts.search import MCTSConfig
from src.model.inference import ModelInference
from src.model.network import AlphaZeroNet, NetworkConfig
from src.training.checkpoint import load_checkpoint
from src.training.metrics import MetricsLogger
from src.training.self_play import SelfPlayGenerator


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--checkpoint", required=True)
    parser.add_argument("--label", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--games", type=int, default=8)
    parser.add_argument("--simulations", type=int, default=40)
    parser.add_argument("--max-moves", type=int, default=120)
    parser.add_argument("--seed", type=int, default=20261115)
    args = parser.parse_args()

    if args.games < 1 or args.simulations < 1 or args.max_moves < 1:
        parser.error("games, simulations and max-moves must all be positive")

    checkpoint = Path(args.checkpoint)
    if not checkpoint.is_file() or checkpoint.stat().st_size == 0:
        parser.error(f"checkpoint is missing or empty: {checkpoint}")

    random.seed(args.seed)
    np.random.seed(args.seed)
    torch.manual_seed(args.seed)
    torch.set_num_threads(1)

    encoding = MoveEncoding()
    encoder = BoardEncoder()
    model = AlphaZeroNet(
        action_size=encoding.action_size,
        config=NetworkConfig(
            input_channels=20,
            board_size=8,
            num_filters=64,
            num_res_blocks=3,
            value_hidden_size=128,
        ),
    )
    checkpoint_metadata = load_checkpoint(checkpoint, model, map_location="cpu")
    model.eval()
    inference = ModelInference(model, encoding, encoder=encoder, device="cpu")
    generator = SelfPlayGenerator(
        inference=inference,
        move_encoding=encoding,
        encoder=encoder,
        mcts_config=MCTSConfig(
            num_simulations=args.simulations,
            c_puct=1.5,
            dirichlet_alpha=0.5,
            dirichlet_epsilon=0.30,
            add_dirichlet_noise=True,
            temperature=1.0,
        ),
        max_moves=args.max_moves,
        opening_temperature_moves=30,
        opening_temperature=1.3,
        late_temperature=0.5,
        resign_threshold=None,
        adjudicate_on_max_moves=True,
    )

    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    metadata_path = output.with_suffix(".metadata.json")
    logger = MetricsLogger(output.parent)
    # Use a fresh output file: never append to or overwrite an existing archive.
    if output.exists() or metadata_path.exists():
        raise FileExistsError(f"Refusing to overwrite existing dataset or metadata: {output}")

    checkpoint_hash = sha256_file(checkpoint)
    started = time.perf_counter()
    games = generator.generate_games(args.games)
    for index, game in enumerate(games, start=1):
        logger.append_self_play_game(
            iteration=0,
            game_number=index,
            result=game.result,
            moves=game.moves,
            samples=game.num_positions,
            elapsed_seconds=0.0,
            ended_by_resignation=game.ended_by_resignation,
            ended_by_adjudication=game.ended_by_adjudication,
            ended_by_move_limit=game.ended_by_move_limit,
            filename=output.name,
            value_targets=[sample.value_target for sample in game.samples],
        )

    metadata = {
        "label": args.label,
        "checkpoint_sha256": checkpoint_hash,
        "checkpoint_epoch": checkpoint_metadata.get("epoch"),
        "seed": args.seed,
        "games": args.games,
        "simulations": args.simulations,
        "max_moves": args.max_moves,
        "device": "cpu",
        "dirichlet_noise": True,
        "dirichlet_alpha": 0.5,
        "dirichlet_epsilon": 0.30,
        "opening_temperature_moves": 30,
        "opening_temperature": 1.3,
        "late_temperature": 0.5,
        "positions": sum(game.num_positions for game in games),
    }
    metadata_path.write_text(json.dumps(metadata, indent=2) + "\\n", encoding="utf-8")

    print({
        "label": args.label,
        "checkpoint": str(checkpoint),
        "checkpoint_sha256": checkpoint_hash,
        "checkpoint_epoch": checkpoint_metadata.get("epoch"),
        "seed": args.seed,
        "games": args.games,
        "simulations": args.simulations,
        "max_moves": args.max_moves,
        "positions": sum(game.num_positions for game in games),
        "elapsed_seconds": round(time.perf_counter() - started, 2),
        "output": str(output),
        "metadata": str(metadata_path),
    })


if __name__ == "__main__":
    main()
