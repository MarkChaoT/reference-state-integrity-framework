# Reference-State Framework Utilities

This repository contains utility materials associated with the reference-state framework.

## Contents

- `README.md` — repository overview
- `.gitignore` — generic exclusions
- `LICENSE` — MIT License
- `THIRD_PARTY_NOTICE.md` — general third-party notice
- `SHA256SUMS.txt` — file checksums
- `file_stability_capture.py` — file capture utility
- `manifest_verify.py` — checksum manifest verification utility
- `reference_state_compare.py` — reference-state comparison utility
- [`docs/rfc3161-readonly-verification.md`](docs/rfc3161-readonly-verification.md) — RFC 3161 read-only verification guide
- [`examples/rfc3161/`](examples/rfc3161/README.md) — synthetic offline verification example

## Scope

The repository provides supporting utilities and a standalone RFC 3161 example. The example uses a self-signed demonstration trust anchor and **does not establish externally trusted time**. See the [verification guide](docs/rfc3161-readonly-verification.md) for instructions and limitations.
