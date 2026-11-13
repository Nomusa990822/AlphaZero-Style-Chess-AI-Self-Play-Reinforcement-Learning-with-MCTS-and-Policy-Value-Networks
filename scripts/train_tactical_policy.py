"""Run a bounded policy-only fine-tuning pilot on curated tactical positions."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import hashlib

import torch
import torch.nn.functional as F

from src.engine.move_encoding import MoveEncoding
from src.model.network import AlphaZeroNet, NetworkConfig
from src.training.checkpoint import load_checkpoint, save_checkpoint
from src.training.tactical_benchmark import load_tactical_positions
from src.training.tactical_policy import (
    build_tactical_policy_examples,
    policy_metrics,
    split_tactical_examples,
)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def parse_args():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--checkpoint", required=True)
    parser.add_argument("--positions", default="benchmarks/tactical_positions.jsonl")
    parser.add_argument("--output-checkpoint", required=True)
    parser.add_argument("--output-report", required=True)
    parser.add_argument("--epochs", type=int, default=8)
    parser.add_argument("--batch-size", type=int, default=8)
    parser.add_argument("--learning-rate", type=float, default=0.00001)
    parser.add_argument("--validation-fraction", type=float, default=0.2)
    parser.add_argument("--seed", type=int, default=20261113)
    args = parser.parse_args()
    if args.epochs < 1 or args.batch_size < 1 or args.learning_rate <= 0:
        parser.error("epochs, batch-size and learning-rate must be positive")
    return args


def main():
    args = parse_args()
    torch.manual_seed(args.seed)
    torch.set_num_threads(2)
    device = torch.device("cpu")
    checkpoint_path = Path(args.checkpoint)
    if not checkpoint_path.is_file() or checkpoint_path.stat().st_size == 0:
        raise FileNotFoundError(f"Checkpoint missing or empty: {checkpoint_path}")

    encoding = MoveEncoding()
    # Matches the immutable architecture used to load and inspect the pilot checkpoints.
    config = NetworkConfig(
        input_channels=20, board_size=8, num_filters=64,
        num_res_blocks=3, value_hidden_size=128,
    )
    model = AlphaZeroNet(action_size=encoding.action_size, config=config).to(device)
    payload = load_checkpoint(checkpoint_path, model, optimizer=None, map_location=device)
    model.eval()

    positions = load_tactical_positions(args.positions)
    examples = build_tactical_policy_examples(positions, move_encoding=encoding)
    train_examples, validation_examples = split_tactical_examples(
        examples, args.validation_fraction, args.seed
    )
    before_train = policy_metrics(model, train_examples)
    before_validation = policy_metrics(model, validation_examples)
    before_all = policy_metrics(model, examples)

    # The value head receives no gradients and no synthetic tactical value labels.
    for parameter in model.value_head.parameters():
        parameter.requires_grad_(False)
    optimizer = torch.optim.Adam(
        [parameter for parameter in model.parameters() if parameter.requires_grad],
        lr=args.learning_rate,
        weight_decay=1e-5,
    )

    history = []
    for epoch in range(1, args.epochs + 1):
        model.train()
        # Keep the frozen value head in eval mode; the shared trunk still learns
        # tactical policy features, while no value-head parameters are optimised.
        model.value_head.eval()
        order = torch.randperm(len(train_examples)).tolist()
        loss_total = 0.0
        batches = 0
        for start in range(0, len(order), args.batch_size):
            batch = [train_examples[i] for i in order[start:start + args.batch_size]]
            states = torch.as_tensor(
                __import__("numpy").stack([x.state for x in batch]),
                dtype=torch.float32, device=device,
            )
            targets = torch.as_tensor(
                __import__("numpy").stack([x.policy_target for x in batch]),
                dtype=torch.float32, device=device,
            )
            optimizer.zero_grad(set_to_none=True)
            logits, _ = model(states)
            loss = -(targets * F.log_softmax(logits, dim=1)).sum(dim=1).mean()
            loss.backward()
            torch.nn.utils.clip_grad_norm_(
                [p for p in model.parameters() if p.requires_grad], max_norm=1.0
            )
            optimizer.step()
            loss_total += float(loss.detach().item())
            batches += 1
        validation = policy_metrics(model, validation_examples)
        history.append({
            "epoch": epoch,
            "training_policy_loss": loss_total / max(1, batches),
            "validation_policy_cross_entropy": validation["policy_cross_entropy"],
            "validation_top1_accuracy": validation["top1_accuracy"],
            "validation_acceptable_probability_mass": validation["mean_acceptable_probability_mass"],
        })

    after_train = policy_metrics(model, train_examples)
    after_validation = policy_metrics(model, validation_examples)
    after_all = policy_metrics(model, examples)

    output_checkpoint = Path(args.output_checkpoint)
    save_checkpoint(
        output_checkpoint, model, optimizer=None, epoch=args.epochs,
        extra={
            "experiment": "tactical_policy_only_finetuning",
            "source_checkpoint_sha256": sha256(checkpoint_path),
            "training_position_ids": [x.position_id for x in train_examples],
            "validation_position_ids": [x.position_id for x in validation_examples],
            "value_head_frozen": True,
            "value_targets_used": False,
        },
    )
    report = {
        "schema_version": 1,
        "experiment": "bounded_tactical_policy_only_finetuning",
        "source_checkpoint": {
            "path": checkpoint_path.name,
            "sha256": sha256(checkpoint_path),
            "epoch": payload.get("epoch"),
        },
        "candidate_checkpoint": {
            "path": output_checkpoint.name,
            "sha256": sha256(output_checkpoint),
            "size_bytes": output_checkpoint.stat().st_size,
        },
        "settings": {
            "epochs": args.epochs,
            "batch_size": args.batch_size,
            "learning_rate": args.learning_rate,
            "validation_fraction": args.validation_fraction,
            "seed": args.seed,
            "device": "cpu",
            "architecture": {
                "input_channels": 20, "num_filters": 64,
                "num_res_blocks": 3, "value_hidden_size": 128,
            },
            "value_head_frozen": True,
            "synthetic_value_targets": False,
        },
        "split": {
            "training_ids": [x.position_id for x in train_examples],
            "validation_ids": [x.position_id for x in validation_examples],
        },
        "before": {
            "training": before_train,
            "validation": before_validation,
            "all_positions": before_all,
        },
        "after": {
            "training": after_train,
            "validation": after_validation,
            "all_positions": after_all,
        },
        "epochs": history,
        "interpretation_limits": [
            "This is a small supervised policy-only experiment, not a general playing-strength evaluation.",
            "Validation positions are held out from optimisation but come from the same curated corpus.",
            "The value head is frozen and no tactical value labels are fabricated; shared trunk updates can still change value predictions.",
            "The source checkpoint is never modified and this candidate is not promoted.",
        ],
    }
    report_path = Path(args.output_report)
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
