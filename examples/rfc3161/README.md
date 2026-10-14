# RFC 3161 offline example

**Synthetic demonstration only. NOT externally trusted timestamp evidence.**

This directory contains a standalone example for verifying a previously generated RFC 3161 response. The timestamps and certificates are demonstration fixtures, not an assertion of independently trusted time or validation of other data.

| Path | Purpose |
| --- | --- |
| `data/demo.txt` | Illustrative text payload |
| `manifest-sha256.txt` | SHA-256 digest of `data/demo.txt`; the manifest bytes were timestamped |
| `demo_request.tsq` | Preserved DER RFC 3161 request for the manifest |
| `demo_response.tsr` | Complete DER RFC 3161 response signed by a local demo TSA |
| `demo_tsa_cert.pem` | Public signing certificate, also embedded in the response |
| `demo_root_ca.pem` | Self-signed, **not independently trusted** demonstration root, passed explicitly as `-CAfile` |

No signing or root **private keys** are included. Do **not** import the demo root into your system trust store.

## Run the example

From `examples/rfc3161/`:

```sh
openssl ts -verify -data manifest-sha256.txt -in demo_response.tsr -CAfile demo_root_ca.pem
```

Expected for this explicitly selected local root: `Verification: OK` and process exit code `0`.

To compare against the preserved request instead:

```sh
openssl ts -verify -queryfile demo_request.tsq -in demo_response.tsr -CAfile demo_root_ca.pem
```

This request-based check does not independently rehash the original input. The [verification guide](../../docs/rfc3161-readonly-verification.md) describes interpretation, a modified-copy negative control, and separate payload-checksum comparison.

## Example QA scope — 2026-10-14 (UTC)

On **OpenSSL 3.5.5, Debian x86_64**:

- Input-data verification: `Verification: OK`, exit `0`.
- Preserved-request verification: `Verification: OK`, exit `0`.
- Deliberately modified copy of the manifest: `Verification: FAILED`, exit `1`.

No Windows execution or additional version/platform coverage is claimed for **this example**.
