from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path, PurePosixPath


def sha256_file(path: Path, chunk_size: int = 1024 * 1024) -> str:
    """Return the lowercase SHA-256 digest of a file."""
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(chunk_size), b""):
            digest.update(block)
    return digest.hexdigest()


def parse_manifest(manifest: Path) -> list[tuple[str, str]]:
    """Parse standard 'digest<two spaces>relative/path' SHA-256 manifest lines."""
    entries = []
    for line_number, raw in enumerate(manifest.read_text(encoding="utf-8").splitlines(), start=1):
        line = raw.strip()
        if not line:
            continue
        if "  " not in line:
            raise ValueError(f"invalid manifest line {line_number}")
        digest, relative_path = line.split("  ", 1)
        digest = digest.strip().lower()
        relative_path = relative_path.strip().lstrip("*")
        if len(digest) != 64 or any(ch not in "0123456789abcdef" for ch in digest):
            raise ValueError(f"invalid SHA-256 digest on line {line_number}")
        posix_path = PurePosixPath(relative_path)
        if posix_path.is_absolute() or ".." in posix_path.parts or not posix_path.parts:
            raise ValueError(f"unsafe relative path on line {line_number}")
        entries.append((digest, posix_path.as_posix()))
    return entries


def verify(manifest: Path, root: Path) -> dict:
    """Verify every manifest entry against files below a caller-supplied root directory."""
    manifest = manifest.resolve()
    root = root.resolve()
    if not manifest.is_file():
        raise FileNotFoundError(manifest)
    if not root.is_dir():
        raise NotADirectoryError(root)

    results = []
    for expected, relative_path in parse_manifest(manifest):
        target = root.joinpath(*PurePosixPath(relative_path).parts)
        exists = target.is_file()
        actual = sha256_file(target) if exists else None
        match = bool(exists and actual == expected)
        results.append({
            "relative_path": relative_path,
            "exists": exists,
            "expected_sha256": expected,
            "actual_sha256": actual,
            "match": match,
        })

    matched = sum(1 for item in results if item["match"])
    return {
        "algorithm": "SHA-256",
        "manifest": str(manifest),
        "root": str(root),
        "entry_count": len(results),
        "matched_count": matched,
        "mismatch_count": len(results) - matched,
        "verification_state": "CONSISTENT" if matched == len(results) else "MISMATCH",
        "entries": results,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Verify files against a SHA-256 manifest.")
    parser.add_argument("manifest", type=Path)
    parser.add_argument("--root", type=Path, default=Path("."), help="Root directory for manifest-relative paths.")
    parser.add_argument("--report", type=Path, help="Optional JSON report path.")
    args = parser.parse_args()

    report = verify(args.manifest, args.root)
    payload = json.dumps(report, indent=2, ensure_ascii=False)
    if args.report:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(payload + "\n", encoding="utf-8")
    print(payload)
    return 0 if report["verification_state"] == "CONSISTENT" else 1


if __name__ == "__main__":
    raise SystemExit(main())
