#!/usr/bin/env python3
"""Compute the SHA-384 seal for a canonicalized CSL JSON payload.

The utility mirrors the snippet used in CBARL verification tooling. It loads a
JSON document, canonicalizes it (sorting keys and removing extra whitespace),
concatenates the resulting bytes with the S1 seed, and prints the SHA-384
hex digest.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Optional
import hashlib


def _load_json_bytes(path: Path) -> bytes:
    try:
        with path.open("r", encoding="utf-8") as fh:
            data = json.load(fh)
    except FileNotFoundError:
        raise SystemExit(f"JSON file not found: {path}")
    except json.JSONDecodeError as exc:
        raise SystemExit(f"Invalid JSON in {path}: {exc}")

    canonical = json.dumps(data, separators=(",", ":"), sort_keys=True)
    return canonical.encode("utf-8")


def _load_s1_bytes(hex_value: Optional[str], hex_file: Optional[Path]) -> bytes:
    if hex_value and hex_file:
        raise SystemExit("Provide either --salt-hex or --salt-file, not both.")

    if hex_file:
        try:
            text = hex_file.read_text(encoding="utf-8")
        except FileNotFoundError:
            raise SystemExit(f"Salt file not found: {hex_file}")
        hex_value = "".join(text.split())

    if not hex_value:
        raise SystemExit("An S1 salt must be provided via --salt-hex or --salt-file.")

    try:
        return bytes.fromhex(hex_value)
    except ValueError as exc:
        raise SystemExit(f"S1 salt is not valid hex: {exc}")


def compute_seal(json_path: Path, salt_hex: Optional[str], salt_file: Optional[Path]) -> str:
    json_bytes = _load_json_bytes(json_path)
    salt_bytes = _load_s1_bytes(salt_hex, salt_file)
    digest = hashlib.sha384(json_bytes + salt_bytes).hexdigest()
    return digest


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Compute the CBARL CSL SHA-384 seal.")
    parser.add_argument(
        "json_path",
        nargs="?",
        type=Path,
        default=Path("csl.json"),
        help="Path to the CSL JSON payload (default: ./csl.json)",
    )
    parser.add_argument("--salt-hex", help="S1 seed as a hexadecimal string.")
    parser.add_argument(
        "--salt-file",
        type=Path,
        help="Path to a file containing the S1 seed in hexadecimal form.",
    )
    parser.add_argument(
        "--write-digest",
        type=Path,
        help="Optional path to write the resulting digest (instead of only printing).",
    )
    return parser


def main(argv: Optional[list[str]] = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    digest = compute_seal(args.json_path, args.salt_hex, args.salt_file)
    print(digest)

    if args.write_digest:
        try:
            args.write_digest.write_text(digest + "\n", encoding="utf-8")
        except OSError as exc:
            raise SystemExit(f"Unable to write digest to {args.write_digest}: {exc}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
