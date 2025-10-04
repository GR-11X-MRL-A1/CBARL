# CBARL
CBARL is a restorative logging standard for algorithmic and institutional harm. It pairs the TruthLayer sealing toolkit with an ADA-first communication protocol so lived events become sealed, auditable evidence. Not pro, but process— Prose becomes pro se When truth flows.

## Tools

### `compute_seal.py`

The `tools/compute_seal.py` helper mirrors the canonical sealing snippet used in
CBARL workflows. It canonicalizes a CSL JSON payload, concatenates it with the
S1 seed, and outputs the SHA-384 digest.

```bash
# Using the default ./csl.json payload and a hex seed supplied inline
python tools/compute_seal.py --salt-hex "<S1_HEX>"

# Reading the seed from a file and saving the digest alongside the payload
python tools/compute_seal.py csl.json --salt-file s1.hex --write-digest seal.txt
```

`compute_seal.py` accepts either `--salt-hex` or `--salt-file`. The JSON input
is canonicalized with sorted keys and compact separators so the resulting hash
is deterministic across environments.
