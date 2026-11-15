"""Run the frozen 24-pair confirmatory comparison in inference-only mode."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

from src.engine.encoder import BoardEncoder
from src.engine.move_encoding import MoveEncoding
from src.model.inference import ModelInference
from src.model.network import AlphaZeroNet, NetworkConfig
from src.training.checkpoint import load_checkpoint
from src.training.confirmatory_evaluator import ConfirmatoryPairedEvaluator


def digest(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def load_agent(path: Path, encoding: MoveEncoding, encoder: BoardEncoder):
    model = AlphaZeroNet(
        action_size=encoding.action_size,
        config=NetworkConfig(input_channels=20, board_size=8, num_filters=64, num_res_blocks=3, value_hidden_size=128),
    )
    payload = load_checkpoint(path, model, optimizer=None, map_location="cpu")
    model.eval()
    return ModelInference(model, encoding, encoder, device="cpu"), {
        "filename": path.name,
        "size_bytes": path.stat().st_size,
        "sha256": digest(path),
        "epoch": payload.get("epoch"),
        "extra": payload.get("extra", {}),
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--baseline", type=Path, required=True)
    parser.add_argument("--candidate", type=Path, required=True)
    parser.add_argument("--expected-baseline-sha256", required=True)
    parser.add_argument("--expected-candidate-sha256", required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--opening-suite", type=Path, default=Path("benchmarks/evaluation_openings_confirmatory_v1.jsonl"))
    parser.add_argument("--suite-version", default="confirmatory_v1")
    args = parser.parse_args()
    for path in (args.baseline, args.candidate):
        if not path.is_file() or path.stat().st_size == 0:
            raise FileNotFoundError(f"checkpoint missing or empty: {path}")
    baseline_hash, candidate_hash = digest(args.baseline), digest(args.candidate)
    if baseline_hash != args.expected_baseline_sha256:
        raise RuntimeError(f"baseline SHA-256 mismatch: {baseline_hash}")
    if candidate_hash != args.expected_candidate_sha256:
        raise RuntimeError(f"candidate SHA-256 mismatch: {candidate_hash}")

    encoding, encoder = MoveEncoding(), BoardEncoder()
    incumbent, incumbent_meta = load_agent(args.baseline, encoding, encoder)
    candidate, candidate_meta = load_agent(args.candidate, encoding, encoder)
    evaluator = ConfirmatoryPairedEvaluator(encoding, suite_path=args.opening_suite, suite_version=args.suite_version)
    report = evaluator.compare(candidate, incumbent)
    report["checkpoints"] = {"incumbent": incumbent_meta, "candidate": candidate_meta}
    report["suite_version"] = args.suite_version
    report["opening_suite_path"] = str(args.opening_suite)
    report["opening_suite_sha256"] = digest(args.opening_suite)
    report["source_commit"] = __import__("os").environ.get("GITHUB_SHA")
    report["execution_mode"] = "cpu_inference_only"
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
