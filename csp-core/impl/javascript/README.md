# JavaScript Verifier (In Progress)

The JavaScript reference verifier will be added once it reproduces all 10 S2
values.

Requirements:

- Use `crypto.subtle.digest('SHA-384', ...)` for hashing.
- Implement strict CSP-Core canonicalization with key sorting by UTF-16 code
  units.
- Use `decimal.js` or equivalent for phase arithmetic with round-half-to-even.
- Apply NFC normalization to all strings before canonicalization.
