"""Create a SHA-256 inventory for locally generated model checkpoints."""
from __future__ import annotations
import argparse, hashlib, json
from datetime import datetime, timezone
from pathlib import Path

def build_manifest(checkpoint_dir: Path) -> dict:
    """Describe checkpoint files without loading model payloads."""
    files = sorted(p for p in checkpoint_dir.glob("*.pt") if p.is_file() and not p.is_symlink())
    entries = []
    for path in files:
        digest = hashlib.sha256()
        size = 0
        with path.open("rb") as handle:
            for chunk in iter(lambda: handle.read(1024 * 1024), b""):
                size += len(chunk)
                digest.update(chunk)
        entries.append({"filename": path.name, "size_bytes": size, "sha256": digest.hexdigest()})
    return {"schema_version": 1, "created_utc": datetime.now(timezone.utc).isoformat(),
            "checkpoint_count": len(entries), "checkpoints": entries}

def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--checkpoint-dir", type=Path, default=Path("data/checkpoints"))
    parser.add_argument("--output", type=Path, default=Path("reports/checkpoint-manifest.json"))
    args = parser.parse_args()
    manifest = build_manifest(args.checkpoint_dir)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(manifest, indent=2))

if __name__ == "__main__":
    main()
