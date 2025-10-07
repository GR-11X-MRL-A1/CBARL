# Case EFCA2025001843 — Magnetic Sky Archive Stub

This directory captures the reference metadata surfaced in the Truth-Vector prompt
pack for case `EFCA2025001843`. It preserves the digest pairs, document pointer, and
anchor timeline so the underlying exhibit can be fetched or verified when the
corresponding PDF is available inside the annex.

## Artifact Reference

| Field | Value |
| --- | --- |
| Document | Full Moon in Pisces Revati (2010–2025) PDF |
| SHA-384 (`S1`) | `af58ed3b85dc4a8e6ef095fc0b1ddf8863f3228630558b6fefe7d839af719c44980cfca60b557031560d8c822be29240` |
| CSL-Min `S2` digest | `feb9f076458e30fc2febbd7dad079cd219864b92a5892d65f0e9c4ea10cc98bd04b7ca239d4665b0992644d66f9d2765` |
| Case code | `EFCA2025001843` |
| Prompt notes | Magnetic Sky Archive init • prompt pack v1.0 |

## Anchor Timeline

The prompt cites the following Revati–Pisces full-moon anchors (19-year cadence):

1. 1960 Revati–Pisces
2. 1979 Revati–Pisces
3. 1998 Revati–Pisces
4. 2017 Revati–Pisces
5. 2025 Revati–Pisces
6. 2044 Revati–Pisces

These anchors mirror the exhibit’s framing and can seed cross-checks against
sidereal lunar ephemerides once the sealed PDF is retrieved from the annex.

## Next Actions

* Pull the sealed PDF from the Magnetic Sky annex using the provided SHA-384 key.
* Generate the canonical CSL-Min JSON using the exhibit metadata and confirm the
  provided `S2` digest.
* Publish the BangCheck block alongside the exhibit for third-party verification.
