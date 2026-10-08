from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import time
from datetime import datetime, timezone
from pathlib import Path


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="milliseconds").replace("+00:00", "Z")


def sha256_file(path: Path, chunk_size: int = 1024 * 1024) -> str:
    """Return the lowercase SHA-256 digest of a file."""
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(chunk_size), b""):
            digest.update(block)
    return digest.hexdigest()


def snapshot(path: Path) -> dict:
    """Capture size and modification time without modifying the source file."""
    stat = path.stat()
    return {
        "size_bytes": stat.st_size,
        "mtime_ns": stat.st_mtime_ns,
        "observed_at_utc": utc_now(),
    }


def wait_until_stable(path: Path, interval_seconds: float, checks: int) -> list[dict]:
    """Require consecutive identical size/mtime observations before capture."""
    if checks < 2:
        raise ValueError("checks must be at least 2")
    observations = []
    previous = None
    stable_count = 0
    while stable_count < checks:
        current = snapshot(path)
        observations.append(current)
        if previous and (
            current["size_bytes"] == previous["size_bytes"]
            and current["mtime_ns"] == previous["mtime_ns"]
        ):
            stable_count += 1
        else:
            stable_count = 1
        previous = current
        if stable_count < checks:
            time.sleep(interval_seconds)
    return observations


def capture(source: Path, destination: Path, interval_seconds: float, checks: int) -> dict:
    """Copy a stable source file and verify source/copy digest equality."""
    source = source.resolve()
    destination = destination.resolve()
    if not source.is_file():
        raise FileNotFoundError(source)
    if source == destination:
        raise ValueError("source and destination must be different")

    observations = wait_until_stable(source, interval_seconds, checks)
    source_digest_before = sha256_file(source)
    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source, destination)
    source_digest_after = sha256_file(source)
    destination_digest = sha256_file(destination)

    return {
        "source": str(source),
        "destination": str(destination),
        "stability_checks_required": checks,
        "stability_interval_seconds": interval_seconds,
        "observations": observations,
        "source_sha256_before_copy": source_digest_before,
        "source_sha256_after_copy": source_digest_after,
        "destination_sha256": destination_digest,
        "source_unchanged_during_capture": source_digest_before == source_digest_after,
        "copy_matches_source": source_digest_after == destination_digest,
        "captured_at_utc": utc_now(),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Capture a file after repeated stable size/mtime observations.")
    parser.add_argument("source", type=Path)
    parser.add_argument("destination", type=Path)
    parser.add_argument("--interval", type=float, default=1.0, help="Seconds between observations.")
    parser.add_argument("--checks", type=int, default=2, help="Required consecutive stable observations (>=2).")
    parser.add_argument("--report", type=Path, help="Optional JSON report path.")
    args = parser.parse_args()

    report = capture(args.source, args.destination, args.interval, args.checks)
    payload = json.dumps(report, indent=2, ensure_ascii=False)
    if args.report:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(payload + "\n", encoding="utf-8")
    print(payload)
    return 0 if report["source_unchanged_during_capture"] and report["copy_matches_source"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
