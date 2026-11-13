"""Run a bounded policy-head-only fine-tuning pilot on curated tactical positions."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import numpy as np
import torch
import torch.nn.functional as F

from src.engine.move_encoding import MoveEncoding
from src.model.network import AlphaZeroNet, NetworkConfig
from src.training.checkpoint import load_checkpoint, save_checkpoint
from src.training.tactical_benchmark import load_tactical_positions
from src.training.tactical_policy import (
    build_tactical_policy_examples,
    configure_policy_head_only,
    policy_metrics,
    set_policy_head_training_mode,
    split_tactical_examples,
    value_drift_metrics,
    value_predictions,
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
    np.random.seed(args.seed)
    torch.set_num_threads(2)
    device = torch.device("cpu")
    checkpoint_path = Path(args.checkpoint)
    if not checkpoint_path.is_file() or checkpoint_path.stat().st_size == 0:
        raise FileNotFoundError(f"Checkpoint missing or empty: {checkpoint_path}")

    encoding = MoveEncoding()
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
    values_before = value_predictions(model, examples)

    trainable_parameters = configure_policy_head_only(model)
    optimizer = torch.optim.Adam(
        trainable_parameters,
        lr=args.learning_rate,
        weight_decay=1e-5,
    )

    history = []
    for epoch in range(1, args.epochs + 1):
        set_policy_head_training_mode(model)
        order = torch.randperm(len(train_examples)).tolist()
        loss_total = 0.0
        batches = 0
        for start in range(0, len(order), args.batch_size):
            batch = [train_examples[i] for i in order[start:start + args.batch_size]]
            states = torch.as_tensor(
                np.stack([x.state for x in batch]), dtype=torch.float32, device=device
            )
            targets = torch.as_tensor(
                np.stack([x.policy_target for x in batch]), dtype=torch.float32, device=device
            )
            optimizer.zero_grad(set_to_none=True)
            logits, _ = model(states)
            loss = -(targets * F.log_softmax(logits, dim=1)).sum(dim=1).mean()
            loss.backward()
            torch.nn.utils.clip_grad_norm_(trainable_parameters, max_norm=1.0)
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
    values_after = value_predictions(model, examples)
    value_drift = value_drift_metrics(values_before, values_after)

    output_checkpoint = Path(args.output_checkpoint)
    save_checkpoint(
        output_checkpoint, model, optimizer=None, epoch=args.epochs,
        extra={
            "experiment": "tactical_policy_head_only_finetuning",
            "source_checkpoint_sha256": sha256(checkpoint_path),
            "training_position_ids": [x.position_id for x in train_examples],
            "validation_position_ids": [x.position_id for x in validation_examples],
            "policy_head_only": True,
            "shared_trunk_frozen": True,
            "value_head_frozen": True,
            "value_targets_used": False,
        },
    )
    report = {
        "schema_version": 2,
        "experiment": "bounded_tactical_policy_head_only_finetuning",
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
            "policy_head_only": True,
            "shared_trunk_frozen": True,
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
        "value_prediction_drift": value_drift,
        "epochs": history,
        "interpretation_limits": [
            "This is a small supervised policy-only experiment, not a general playing-strength evaluation.",
            "Validation positions are held out from optimisation but come from the same curated corpus.",
            "Only policy-head parameters and policy-head BatchNorm statistics are updated; the shared trunk and value head remain in evaluation mode and unchanged.",
            "No tactical value labels are fabricated. Value predictions are expected to remain unchanged, and per-position drift is reported explicitly.",
            "The source checkpoint is never modified and this candidate is not promoted.",
        ],
    }
    report_path = Path(args.output_report)
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
