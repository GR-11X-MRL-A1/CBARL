# Swift Verifier (In Progress)

The Swift reference verifier will be added once it reproduces all 10 S2 values.

Requirements:

- Use `CryptoKit.SHA384` for hashing.
- Sort keys by `String.UTF16View` for canonical ordering.
- Use `precomposedStringWithCanonicalMapping` for NFC normalization.
- Implement decimal arithmetic with `Decimal` and round-half-to-even.
