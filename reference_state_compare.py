from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


def sha256_file(path: Path, chunk_size: int = 1024 * 1024) -> str:
    """Return the lowercase SHA-256 digest of a file."""
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(chunk_size), b""):
            digest.update(block)
    return digest.hexdigest()


def compare(candidate: Path, reference_digest: str) -> dict:
    """Compare a candidate file digest with a supplied reference digest."""
    candidate = candidate.resolve()
    if not candidate.is_file():
        raise FileNotFoundError(candidate)
    normalized_reference = reference_digest.strip().lower()
    if len(normalized_reference) != 64 or any(ch not in "0123456789abcdef" for ch in normalized_reference):
        raise ValueError("reference digest must be a 64-character hexadecimal SHA-256 value")

    candidate_digest = sha256_file(candidate)
    relation = "EQUAL" if candidate_digest == normalized_reference else "UNEQUAL"
    return {
        "candidate": str(candidate),
        "algorithm": "SHA-256",
        "candidate_digest": candidate_digest,
        "reference_digest": normalized_reference,
        "comparison_relation": relation,
        "verification_state": "CONSISTENT" if relation == "EQUAL" else "MISMATCH",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Compare a file against a supplied SHA-256 reference digest.")
    parser.add_argument("candidate", type=Path)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--reference-digest")
    group.add_argument("--reference-file", type=Path, help="File whose SHA-256 becomes the reference digest.")
    parser.add_argument("--report", type=Path, help="Optional JSON report path.")
    args = parser.parse_args()

    reference = args.reference_digest if args.reference_digest else sha256_file(args.reference_file)
    report = compare(args.candidate, reference)
    payload = json.dumps(report, indent=2, ensure_ascii=False)
    if args.report:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(payload + "\n", encoding="utf-8")
    print(payload)
    return 0 if report["verification_state"] == "CONSISTENT" else 1


if __name__ == "__main__":
    raise SystemExit(main())
