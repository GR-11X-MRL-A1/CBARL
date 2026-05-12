#!/usr/bin/env python3
"""CSP-Core v2.1.2 normative reference implementation.

This file intentionally has no third-party dependencies. It implements the
CSP-Core two-stage seal, the profile's RFC 8785-style canonical JSON subset,
and the deterministic Light+Saros decimal anchor used by the conformance
vectors in this repository.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
import unicodedata
from datetime import datetime, timezone
from decimal import Decimal, ROUND_HALF_EVEN, getcontext
from pathlib import Path
from typing import Any

VERSION = "2.1.2"
DELIMITER = b"\x1f"
HEX_RE = re.compile(r"^[0-9a-f]+$")
TIMESTAMP_RE = re.compile(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d{3}Z$")
EPOCH = datetime(2000, 1, 1, tzinfo=timezone.utc)
Q6 = Decimal("0.000001")
Q3 = Decimal("0.001")
SYNODIC_MONTH_DAYS = Decimal("29.530588853")
SAROS_DAYS = Decimal("6585.321347")
SECONDS_PER_DAY = Decimal("86400")

# Decimal precision is intentionally larger than the six emitted places so
# implementations can reproduce the final round-half-even quantization.
getcontext().prec = 50
getcontext().rounding = ROUND_HALF_EVEN


class VerificationState:
    PASS = "PASS"
    FAIL = "FAIL"
    INDETERMINATE = "INDETERMINATE"


def parse_timestamp(value: str) -> datetime:
    if not isinstance(value, str) or TIMESTAMP_RE.fullmatch(value) is None:
        raise ValueError("timestamps MUST be UTC with exactly three fractional digits and Z suffix")
    return datetime.strptime(value, "%Y-%m-%dT%H:%M:%S.%fZ").replace(tzinfo=timezone.utc)


def format_timestamp(dt: datetime) -> str:
    if dt.tzinfo is None:
        raise ValueError("timestamp must be timezone-aware")
    dt = dt.astimezone(timezone.utc)
    return dt.strftime("%Y-%m-%dT%H:%M:%S.%f")[:23] + "Z"


def _utf16_units(value: str) -> tuple[int, ...]:
    data = unicodedata.normalize("NFC", value).encode("utf-16-be")
    return tuple((data[i] << 8) | data[i + 1] for i in range(0, len(data), 2))


def _escape_json_string(value: str) -> str:
    value = unicodedata.normalize("NFC", value)
    out: list[str] = ['"']
    for ch in value:
        code = ord(ch)
        if ch == '"':
            out.append('\\"')
        elif ch == "\\":
            out.append('\\\\')
        elif ch == "\b":
            out.append('\\b')
        elif ch == "\f":
            out.append('\\f')
        elif ch == "\n":
            out.append('\\n')
        elif ch == "\r":
            out.append('\\r')
        elif ch == "\t":
            out.append('\\t')
        elif code < 0x20:
            out.append(f"\\u{code:04x}")
        else:
            out.append(ch)
    out.append('"')
    return "".join(out)


def canonical_json(value: Any) -> str:
    """Return the canonical JSON string for the CSP-Core JSON subset."""
    if isinstance(value, str):
        return _escape_json_string(value)
    if value is True:
        return "true"
    if value is False:
        return "false"
    if value is None:
        return "null"
    if isinstance(value, int) and not isinstance(value, bool):
        return str(value)
    if isinstance(value, float):
        raise TypeError("CSL JSON numbers are restricted to integers; use decimal strings for fractions")
    if isinstance(value, list):
        return "[" + ",".join(canonical_json(item) for item in value) + "]"
    if isinstance(value, dict):
        normalized: dict[str, Any] = {}
        for key, item in value.items():
            if not isinstance(key, str):
                raise TypeError("JSON object keys must be strings")
            nkey = unicodedata.normalize("NFC", key)
            if nkey in normalized:
                raise ValueError("duplicate object key after NFC normalization")
            normalized[nkey] = item
        pairs = []
        for key in sorted(normalized, key=_utf16_units):
            pairs.append(_escape_json_string(key) + ":" + canonical_json(normalized[key]))
        return "{" + ",".join(pairs) + "}"
    raise TypeError(f"unsupported JSON value: {type(value).__name__}")


def sha384_bytes(data: bytes) -> str:
    return hashlib.sha384(data).hexdigest()


def _decimal_seconds_since_epoch(dt: datetime) -> Decimal:
    delta = dt - EPOCH
    micros = (delta.days * 86400 + delta.seconds) * 1_000_000 + delta.microseconds
    return Decimal(micros) / Decimal(1_000_000)


def _phase(seconds: Decimal, period_days: Decimal) -> Decimal:
    period_seconds = period_days * SECONDS_PER_DAY
    return (seconds % period_seconds) / period_seconds


def _q6(value: Decimal) -> str:
    return format(value.quantize(Q6, rounding=ROUND_HALF_EVEN), "f")


def light_saros_anchor(t_in: str, t_out: str) -> dict[str, str]:
    """Compute the deterministic Light+Saros decimal anchor.

    The anchor is a reproducible civil-time surrogate for the conformance
    suite: midpoint phases are measured from J2000 UTC over a synodic-light
    period and the Saros period, and the interval is represented as a fraction
    of a day. Final values are rounded half-even to exactly six decimal places.
    """
    start = parse_timestamp(t_in)
    end = parse_timestamp(t_out)
    if end < start:
        raise ValueError("t_out MUST be greater than or equal to t_in")
    start_s = _decimal_seconds_since_epoch(start)
    end_s = _decimal_seconds_since_epoch(end)
    mid_s = (start_s + end_s) / Decimal(2)
    interval_s = end_s - start_s
    return {
        "light_phase": _q6(_phase(mid_s, SYNODIC_MONTH_DAYS)),
        "saros_phase": _q6(_phase(mid_s, SAROS_DAYS)),
        "interval_days": _q6(interval_s / SECONDS_PER_DAY),
    }


def make_csl(t_in: str, t_out: str, label: str) -> dict[str, Any]:
    start = parse_timestamp(t_in)
    end = parse_timestamp(t_out)
    if end < start:
        raise ValueError("t_out MUST be greater than or equal to t_in")
    duration_ms = int(((end - start).total_seconds() * 1000))
    return {
        "csp_version": VERSION,
        "label": unicodedata.normalize("NFC", label),
        "t_in": t_in,
        "t_out": t_out,
        "duration_ms": duration_ms,
        "light_anchor": light_saros_anchor(t_in, t_out),
    }


def seal_bytes(artifact: bytes, t_in: str, t_out: str, label: str) -> dict[str, Any]:
    s1 = sha384_bytes(artifact)
    csl = make_csl(t_in, t_out, label)
    csl_canonical = canonical_json(csl)
    s2 = sha384_bytes(csl_canonical.encode("utf-8") + DELIMITER + s1.encode("ascii"))
    return {
        "protocol": "CSP-Core",
        "version": VERSION,
        "csl": csl,
        "csl_canonical": csl_canonical,
        "s1": s1,
        "s2": s2,
        "bangcheck": {
            "algorithm": "SHA-384",
            "delimiter_hex": "1f",
            "canonicalization": "CSP-Core-v2.1.2-RFC8785-profile",
            "state": VerificationState.PASS,
        },
    }


def verify_bytes(artifact: bytes, vector: dict[str, Any]) -> tuple[str, str]:
    if "s1" not in vector or "s2" not in vector:
        return VerificationState.INDETERMINATE, "vector lacks s1 or s2"
    expected_s1 = vector["s1"]
    expected_s2 = vector["s2"]
    if not isinstance(expected_s1, str) or not isinstance(expected_s2, str):
        return VerificationState.INDETERMINATE, "s1 and s2 must be strings"
    if HEX_RE.fullmatch(expected_s1) is None or HEX_RE.fullmatch(expected_s2) is None:
        return VerificationState.FAIL, "hashes must be lower-case hex"
    actual_s1 = sha384_bytes(artifact)
    if actual_s1 != expected_s1:
        return VerificationState.FAIL, "S1 mismatch"
    csl_text = vector.get("csl_canonical")
    if not isinstance(csl_text, str):
        csl = vector.get("csl")
        if not isinstance(csl, dict):
            return VerificationState.INDETERMINATE, "vector lacks canonical CSL and CSL object"
        csl_text = canonical_json(csl)
    actual_s2 = sha384_bytes(csl_text.encode("utf-8") + DELIMITER + actual_s1.encode("ascii"))
    if actual_s2 != expected_s2:
        return VerificationState.FAIL, "S2 mismatch"
    return VerificationState.PASS, "S1 and S2 match"


VECTOR_CASES = [
    ("vector-01", b"", "empty artifact"),
    ("vector-02", b"hello, CSP-Core\n", "ASCII line"),
    ("vector-03", "Unicode torture: cafe\u0301 / café / 𝄞\n".encode("utf-8"), "Unicode NFC torture"),
    ("vector-04", b"delimiter adversary: alpha\x1fbeta\\u001f\n", "delimiter adversarial string"),
    ("vector-05", "emoji: 🜁🔒🌗\n".encode("utf-8"), "emoji artifact"),
    ("vector-06", bytes(range(32)), "binary prefix bytes"),
    ("vector-07", b"LF only line 1\nLF only line 2\n", "line ending check"),
    ("vector-08", b'{"z":3,"a":[1,2,3],"msg":"canonical"}\n', "JSON-looking artifact"),
    ("vector-09", "combining marks: A\u030a e\u0301 n\u0303\n".encode("utf-8"), "combining marks"),
    ("vector-10", ("CSP-Core v2.1.2 conformance vector 10\n" * 8).encode("utf-8"), "repeated text"),
]


def generate_vectors(directory: Path) -> None:
    directory.mkdir(parents=True, exist_ok=True)
    base_in = "2026-05-12T02:00:00.000Z"
    for idx, (name, artifact, label) in enumerate(VECTOR_CASES, start=1):
        t_out_dt = parse_timestamp(base_in).replace(microsecond=idx * 1000)
        t_out = format_timestamp(t_out_dt)
        sealed = seal_bytes(artifact, base_in, t_out, f"CSP-Core v2.1.2 {label}")
        vector = {
            "id": name,
            "artifact_hex": artifact.hex(),
            "t_in": base_in,
            "t_out": t_out,
            "label": f"CSP-Core v2.1.2 {label}",
            **sealed,
        }
        (directory / f"{name}.json").write_text(json.dumps(vector, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def cmd_seal(args: argparse.Namespace) -> int:
    artifact = Path(args.artifact).read_bytes()
    t_out = args.t_out or format_timestamp(datetime.now(timezone.utc))
    result = seal_bytes(artifact, args.t_in, t_out, args.label)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


def cmd_verify(args: argparse.Namespace) -> int:
    vector = json.loads(Path(args.vector).read_text(encoding="utf-8"))
    if args.from_vector:
        artifact_hex = vector.get("artifact_hex")
        if not isinstance(artifact_hex, str):
            print("INDETERMINATE vector lacks artifact_hex")
            return 2
        artifact = bytes.fromhex(artifact_hex)
    else:
        if args.artifact is None:
            print("INDETERMINATE artifact path is required unless --from-vector is used")
            return 2
        artifact = Path(args.artifact).read_bytes()
    state, message = verify_bytes(artifact, vector)
    print(f"{state} {message}")
    return 0 if state == VerificationState.PASS else 1 if state == VerificationState.FAIL else 2


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="CSP-Core v2.1.2 reference implementation")
    sub = parser.add_subparsers(dest="command", required=True)
    gen = sub.add_parser("genvectors", help="generate normative test vectors")
    gen.add_argument("directory")
    seal = sub.add_parser("seal", help="seal an artifact")
    seal.add_argument("artifact")
    seal.add_argument("--t-in", required=True)
    seal.add_argument("--t-out")
    seal.add_argument("--label", default="CSP-Core sealed artifact")
    verify = sub.add_parser("verify", help="verify artifact against a vector or seal JSON")
    verify.add_argument("artifact", nargs="?", help="artifact path; omit when --from-vector is used")
    verify.add_argument("vector", help="vector or seal JSON path")
    verify.add_argument("--from-vector", action="store_true", help="use embedded artifact_hex from the vector")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    if args.command == "genvectors":
        generate_vectors(Path(args.directory))
        return 0
    if args.command == "seal":
        return cmd_seal(args)
    if args.command == "verify":
        return cmd_verify(args)
    parser.error("unknown command")
    return 2


if __name__ == "__main__":
    sys.exit(main())
