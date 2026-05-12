# CSP-Core v2.1.2 — Known Ambiguities Eliminated

1. **Character encoding:** Artifact and CSL are UTF-8 only when represented as
   text. No BOM is permitted.
2. **Line endings:** LF (0x0a) only in text fixtures. CR or CRLF are errors.
3. **Hex encoding:** Lower-case only (0-9, a-f). Upper-case hex fails
   verification.
4. **Trailing whitespace:** Not permitted in any CSL string. Trimming is
   prohibited.
5. **Decimal precision:** All `light_anchor` fields are decimal strings with
   exactly 6 digits after the decimal point (for example, `"0.974999"`).
6. **Rounding:** Decimal intermediate calculations are carried at 50 digits;
   final values are rounded with round-half-to-even.
7. **Timezone:** All timestamps are UTC with `Z` suffix. No offsets are
   permitted.
8. **Fractional seconds:** Exactly three digits (millisecond precision) are
   required.
9. **Unicode normalization:** NFC (Normalization Form C) is applied to all
   strings before canonicalization.
10. **Delimiter:** Raw byte `0x1f` (ASCII Unit Separator). Never escaped, never
    changed.
11. **Canonical key ordering:** UTF-16 code unit value order (surrogate pairs per
    Unicode), not locale-sensitive collation.
12. **Number representation:** JSON numbers only for integers. No floating-point
    numbers in CSL. Fractions are stored as fixed-precision decimal strings.
13. **Empty artifact:** A 0-byte file produces a defined, stable S1. It is not an
    error.
14. **Deep nesting:** Canonicalization is recursive and handles arbitrary depth,
    subject to memory limits.
15. **Solidus escaping:** The solidus `/` MAY be escaped as `\/` by parsers, but
    the canonical emitter does not escape it.
16. **Tri-state verification:** Verifiers return PASS, FAIL, or INDETERMINATE.
