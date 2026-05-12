# CSP-Core Conformance Challenge

## Goal

Reproduce the **exact S2 values** of all 10 normative test vectors using an
implementation in a language other than Python.

## Requirements

1. Implement strict RFC 8785 canonical JSON for the CSP-Core subset: NFC string
   normalization, object-key sorting by UTF-16 code units, no insignificant
   whitespace, and integer-only JSON numbers.
2. Implement SHA-384 (FIPS 180-4).
3. Implement the Light+Saros anchor computation using Decimal arithmetic with
   round-half-to-even to six decimal places.
4. For each test vector, compute S1 = SHA-384(artifact), canonicalize the
   provided CSL, then compute S2 = SHA-384(canonical_CSL || 0x1f ||
   lower_hex(S1)).
5. If your S2 matches the reference S2 in the vector file, that vector passes.

## Verification

Submit your implementation (open-source) and output logs. We will run your code
against the vectors and verify byte-for-byte identity.

## Recognition

The first three independent conformant implementations will be listed on the
official CSP repository as verified.
