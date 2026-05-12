# CSP-Core v2.1.2 — Deterministic Provenance Primitive

**Status:** Conformance-tested, awaiting independent verification.

CSP-Core provides a two-stage cryptographic seal that binds any digital artifact
to a measured time interval and a deterministic celestial (Light+Saros) anchor.
Verification is offline, registry-free, and requires only the artifact file and
the seal JSON.

## Quick Start

1. Generate test vectors:

```bash
python impl/python/csp_core_v2_1_2.py genvectors ./test-vectors
```

2. Verify all vectors using embedded artifact bytes:

```bash
for f in test-vectors/vector-*.json; do
  python impl/python/csp_core_v2_1_2.py verify --from-vector "$f"
done
```

3. Seal your own file:

```bash
python impl/python/csp_core_v2_1_2.py seal mydoc.txt --t-in 2026-05-11T12:00:00.000Z
```

## Test Vectors

The `test-vectors/` directory contains 10 normative test vectors, including
empty files, Unicode torture, delimiter adversarial strings, binary bytes, line
ending checks, and emoji. Every vector includes exact S1, S2, canonical CSL, and
a BangCheck block.

## Normative Reference

The **normative reference implementation** is:
`impl/python/csp_core_v2_1_2.py`

Its SHA-384 hash is:

```text
a7567639e061a12af0be2bc6bcbe30c20bb8db8b36023279451865d7f04beb8b850ccba7774bd8b2b15e059d6d3afacd
```

All other implementations MUST produce byte-for-byte identical S2 values to this
reference.

## Conformance

See `CONFORMANCE.md` for the open challenge.

## Known Ambiguities

See `KNOWN_AMBIGUITIES.md` for the exhaustive list of decisions that prevent
interoperability drift across languages.

## License

CSP-Core specification: CC BY 4.0
Reference implementation: Apache 2.0
Test vectors: CC0 (public domain)
