#!/usr/bin/env python3
"""
Script: annex_to_repo.py
Purpose: Copy files referenced in an annex ledger into a destination repository.
Usage: python3 annex_to_repo.py --ledger /path/to/ANNEX_LEDGER_2025-10-06.md --dest /path/to/gammaWAVE --pattern "Reichian Home Book"
"""
import argparse
import os
import shutil


def parse_ledger(ledger_path, pattern):
    """Extract matching lines from the annex ledger."""
    matches = []
    with open(ledger_path, 'r', encoding='utf-8') as f:
        for line in f:
            if pattern.lower() in line.lower():
                parts = line.strip().split('·')
                if len(parts) >= 4:
                    sha384 = parts[1].strip()
                    filename = parts[3].strip()
                    matches.append((sha384, filename))
    return matches


def copy_from_annex(sha384, filename, dest_dir):
    """Locate file in Annex (by SHA-384 digest) and copy to destination."""
    annex_dir = os.path.expanduser('~/Annex')  # adjust to your Annex path
    source_path = os.path.join(annex_dir, sha384)
    if os.path.isfile(source_path):
        shutil.copy2(source_path, os.path.join(dest_dir, os.path.basename(filename)))
        print(f"Copied {filename} -> {dest_dir}")
    else:
        print(f"Source file {sha384} not found in annex directory.")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--ledger', required=True, help='Path to the annex ledger file')
    parser.add_argument('--dest', required=True, help='Destination repository path')
    parser.add_argument('--pattern', required=True, help='Search pattern for ledger entries')
    args = parser.parse_args()

    entries = parse_ledger(args.ledger, args.pattern)
    if not entries:
        print("No matching entries found.")
        return
    os.makedirs(args.dest, exist_ok=True)
    for sha384, filename in entries:
        copy_from_annex(sha384, filename, args.dest)


if __name__ == '__main__':
    main()
