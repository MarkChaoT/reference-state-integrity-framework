# RFC 3161 read-only verification with OpenSSL

This guide shows how to verify an existing RFC 3161 TimeStampResponse (TSR) using OpenSSL. The commands read preserved inputs: they do not request a new timestamp or modify the supplied files.

The [standalone example](../examples/rfc3161/README.md) uses synthetic text and a **locally generated, self-signed demonstration root**. It illustrates the specified cryptographic checks, **not externally trusted time**.

## Prerequisites and inputs

- OpenSSL with `ts -verify` support (`openssl version`). This bundled example was tested on **OpenSSL 3.5.5 (Debian x86_64)**. This package makes no claim about testing on other platforms or OpenSSL versions.
- The **original byte sequence** that was timestamped (in this example, `manifest-sha256.txt`), or the preserved timestamp request (`.tsq`) if checking only the request-response agreement.
- The complete DER-encoded TimeStampResponse (`.tsr`). A DER-encoded token alone requires `-token_in`; it is not interchangeable with a complete TSR.
- A deliberately selected **CA trust anchor** (`-CAfile`). When needed, add non-anchor issuing certificates with `-untrusted`. Additional certificates do not create trust on their own.

Successful cryptographic verification is conditional on the chosen trust inputs and validation options. Do **not** substitute an arbitrary certificate for a missing trusted root just to obtain a passing result.

## Windows PowerShell

Run from the repository root, after downloading the files:

```powershell
Set-Location examples/rfc3161
openssl version
openssl ts -verify -data manifest-sha256.txt -in demo_response.tsr -CAfile demo_root_ca.pem
if ($LASTEXITCODE -ne 0) { throw "RFC 3161 verification failed" }
```

Expected for this deliberately trusted **local demo root**: `Verification: OK` and exit code `0`.

Alternatively, compare the response to the **preserved request**:

```powershell
openssl ts -verify -queryfile demo_request.tsq -in demo_response.tsr -CAfile demo_root_ca.pem
if ($LASTEXITCODE -ne 0) { throw "RFC 3161 request comparison failed" }
```

The request-based route does **not** rehash the original data file. To inspect the response without modifying it:

```powershell
openssl ts -reply -in demo_response.tsr -text
```

## macOS / Linux shell

```sh
cd examples/rfc3161
openssl version
openssl ts -verify -data manifest-sha256.txt -in demo_response.tsr -CAfile demo_root_ca.pem
openssl ts -verify -queryfile demo_request.tsq -in demo_response.tsr -CAfile demo_root_ca.pem
openssl ts -reply -in demo_response.tsr -text
```

Check the exit status of each command. A nonzero `ts -verify` exit status means that invocation did not pass; inspect stderr to diagnose the reason.

## Negative control (modified copy only)

Leave the original sample unchanged. In PowerShell, make a disposable modified copy:

```powershell
Copy-Item manifest-sha256.txt "$env:TEMP\rfc3161-demo-mutated-manifest.txt"
Add-Content "$env:TEMP\rfc3161-demo-mutated-manifest.txt" "deliberate modification"
openssl ts -verify -data "$env:TEMP\rfc3161-demo-mutated-manifest.txt" -in demo_response.tsr -CAfile demo_root_ca.pem
$LASTEXITCODE
```

Expected: `Verification: FAILED` and nonzero exit status (message-imprint mismatch). An unsuccessful comparison does not, by itself, identify the cause or intent of the alteration.

## Manifest-to-data check is separate

The timestamp signs the **manifest's byte sequence**, not every file mentioned inside it. Separately compare the SHA-256 of the example payload with its recorded digest:

```powershell
openssl dgst -sha256 data/demo.txt
Get-Content manifest-sha256.txt
```

A passing timestamp check does **not** automatically verify the files listed by the manifest.

## Interpreting a verification result

| Observation | Supported interpretation | Not established |
| --- | --- | --- |
| `Verification: OK` with `-data` | Signature, trust-chain checks under the supplied options, and message imprint agree with the supplied bytes | Public authority endorsement; correctness of data content; independent accuracy of time; historical non-revocation |
| `Verification: OK` with `-queryfile` | The response agrees with the preserved request, under the supplied trust inputs | That the original data were rehashed in this invocation |
| `Verification: FAILED` or nonzero status | The specified verification attempt did not pass | The cause, timing, or intent of a change |
| Certificate warnings / errors | The trust chain, purpose, validity, or other conditions need examination | Permission to ignore warnings or expand trust indiscriminately |

In this example, the self-signed demo root is **not publicly trusted**. Its explicit use with `-CAfile` is solely a local exercise. Neither a successful result nor the token's recorded timestamp establishes independently trusted chronology or current/historical certificate revocation status.

## Scope and records

The included sample is **synthetic, not operational evidence**. The same verification procedure can be applied to a different preserved record only when its required bytes, certificates, and authorized trust information are available. This example does not establish the validity or availability of any other record.

For traceable verification, keep an independent execution record containing: tool and build version, operating system, execution time, identifiers and checksums of inputs, exact command, stdout, stderr, process exit code, and trust-anchor origin. Preserve the original inputs unchanged. A later verification does not modify an earlier observation.

## References

- [RFC 3161: Time-Stamp Protocol](https://www.rfc-editor.org/rfc/rfc3161)
- [OpenSSL 3.5 `ts`](https://docs.openssl.org/3.5/man1/openssl-ts/)
- [OpenSSL verification options](https://docs.openssl.org/3.5/man1/openssl-verification-options/)
