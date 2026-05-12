# CSP-Core v2.1.2 Normative Specification

## 1. Scope

CSP-Core defines a deterministic provenance primitive for binding an artifact to
a canonical seal ledger (CSL), a measured UTC time interval, and a deterministic
Light+Saros anchor. The protocol is registry-free: an implementation verifies a
seal using only the artifact bytes and the seal JSON.

## 2. Terms

- **Artifact:** The byte sequence being sealed.
- **CSL:** Canonical seal ledger object containing version, timestamps, label,
  duration, and Light+Saros anchor.
- **S1:** `SHA-384(artifact)` encoded as lower-case hexadecimal.
- **S2:** `SHA-384(canonical_CSL || 0x1f || lower_hex(S1))` encoded as
  lower-case hexadecimal.
- **BangCheck:** Human-readable verification metadata carried in each vector.

## 3. Timestamp Profile

Timestamps MUST be UTC strings in the form `YYYY-MM-DDTHH:MM:SS.mmmZ`. The
fractional component MUST contain exactly three digits. `t_out` MUST be greater
than or equal to `t_in`.

## 4. Canonical JSON Profile

CSP-Core uses a strict RFC 8785-style JSON profile:

1. Strings are normalized to NFC before emission.
2. Objects are serialized without insignificant whitespace.
3. Object keys are sorted by numeric UTF-16 code units.
4. JSON numbers are limited to integers. Fractional quantities are encoded as
   decimal strings.
5. The solidus `/` is not escaped by the canonical emitter.
6. Control characters are escaped using JSON escapes or lower-case `\u00xx`.

## 5. Light+Saros Anchor

The deterministic anchor is computed from the midpoint of `[t_in, t_out]`, using
J2000 UTC (`2000-01-01T00:00:00.000Z`) as the epoch. Let `m` be midpoint seconds
since epoch and `d` be interval seconds.

- `light_phase = (m mod (29.530588853 * 86400)) / (29.530588853 * 86400)`
- `saros_phase = (m mod (6585.321347 * 86400)) / (6585.321347 * 86400)`
- `interval_days = d / 86400`

Each value MUST be rounded with round-half-to-even to exactly six decimal places
and emitted as a string.

## 6. Seal Construction

1. Read the artifact as bytes.
2. Compute `S1 = SHA-384(artifact)`.
3. Build the CSL object.
4. Canonicalize the CSL.
5. Compute `S2 = SHA-384(canonical_CSL || 0x1f || lower_hex(S1))`.

## 7. Verification

A verifier MUST return one of three states:

- **PASS:** S1 and S2 match exactly.
- **FAIL:** Inputs are well-formed but a digest or lower-case-hex requirement
  fails.
- **INDETERMINATE:** Required information is absent or cannot be interpreted.

## 8. Test Vectors

The ten vectors in `test-vectors/` are normative for v2.1.2. Implementations are
conformant only when they reproduce every `s2` value byte-for-byte.
