import hashlib
from scripts.create_checkpoint_manifest import build_manifest

def test_manifest_hashes_checkpoint_files(tmp_path):
    checkpoint = tmp_path / "best_model.pt"
    payload = b"trained-weights-placeholder"
    checkpoint.write_bytes(payload)
    manifest = build_manifest(tmp_path)
    assert manifest["checkpoint_count"] == 1
    assert manifest["checkpoints"] == [{"filename":"best_model.pt","size_bytes":len(payload),"sha256":hashlib.sha256(payload).hexdigest()}]
    assert manifest["schema_version"] == 1

def test_manifest_is_empty_when_no_checkpoint_exists(tmp_path):
    manifest = build_manifest(tmp_path)
    assert manifest["checkpoint_count"] == 0
    assert manifest["checkpoints"] == []

def test_manifest_ignores_nested_files_and_symlinks(tmp_path):
    (tmp_path / "nested").mkdir()
    (tmp_path / "nested" / "ignored.pt").write_bytes(b"nested")
    (tmp_path / "notes.txt").write_text("not a checkpoint")
    target = tmp_path / "target.pt"
    target.write_bytes(b"target")
    (tmp_path / "linked.pt").symlink_to(target)
    manifest = build_manifest(tmp_path)
    assert [item["filename"] for item in manifest["checkpoints"]] == ["target.pt"]
