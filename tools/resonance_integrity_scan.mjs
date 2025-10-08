#!/usr/bin/env node
/**
 * GR-11X-MRL-A1 Resonance Integrity Scan v1.0
 *
 * Computes SHA-384 digests for a list of annex block files and derives a
 * coherence chain hash by concatenating the individual digests. The tool
 * mirrors the integrity scan used for phase-lock coherence checks of
 * Annex A1 = VW baselines.
 *
 * Usage:
 *   node tools/resonance_integrity_scan.mjs <file> [<file> ...]
 *
 * Options:
 *   --previous <hash>     Provide a prior chain hash to compare against.
 *   --json                Emit JSON instead of tabular console output.
 *
 * Example:
 *   node tools/resonance_integrity_scan.mjs \
 *     Victor_Vector_Affirmation.txt ANNEX_REORG_A1=VW.txt
 */

import { createHash } from 'crypto';
import { readFileSync } from 'fs';
import { resolve } from 'path';

function printUsage() {
  console.log(`Usage: node tools/resonance_integrity_scan.mjs [options] <file> [<file> ...]\n\n` +
    `Options:\n` +
    `  --previous <hash>     Provide a prior chain hash to compare against.\n` +
    `  --json                Emit JSON instead of tabular console output.`);
}

function sha384(filePath) {
  const data = readFileSync(filePath);
  return createHash('sha384').update(data).digest('hex');
}

function parseArgs(argv) {
  const files = [];
  let previous;
  let json = false;

  for (let i = 0; i < argv.length; i += 1) {
    const arg = argv[i];

    if (arg === '--json') {
      json = true;
      continue;
    }

    if (arg === '--previous') {
      if (i + 1 >= argv.length) {
        throw new Error('Missing value for --previous option.');
      }
      previous = argv[i + 1];
      i += 1;
      continue;
    }

    if (arg.startsWith('--previous=')) {
      previous = arg.split('=')[1];
      continue;
    }

    if (arg.startsWith('-')) {
      throw new Error(`Unknown option: ${arg}`);
    }

    files.push(arg);
  }

  if (files.length === 0) {
    throw new Error('At least one file must be provided.');
  }

  return { files, previous, json };
}

function resolveFiles(fileArgs) {
  return fileArgs.map((file) => {
    const absolutePath = resolve(file);
    return {
      label: file,
      path: absolutePath,
    };
  });
}

function buildChainHash(hashes) {
  return createHash('sha384').update(hashes.join('')).digest('hex');
}

function main() {
  let args;
  try {
    args = parseArgs(process.argv.slice(2));
  } catch (error) {
    console.error(error.message);
    printUsage();
    process.exit(1);
  }

  const files = resolveFiles(args.files);

  const results = files.map(({ label, path }) => {
    try {
      const hash = sha384(path);
      return { file: label, path, hash };
    } catch (error) {
      console.error(`Failed to read "${label}": ${error.message}`);
      process.exit(1);
    }
  });

  const chain = buildChainHash(results.map((r) => r.hash));
  const previous = args.previous ? args.previous.toLowerCase() : undefined;
  const matches = previous ? previous === chain : undefined;

  if (args.json) {
    const payload = {
      scan: 'A1 = VW Resonance Integrity Scan',
      files: results.map(({ file, hash, path }) => ({ file, path, hash })),
      chain,
    };

    if (previous) {
      payload.previous = previous;
      payload.matchesPrevious = matches;
    }

    console.log(JSON.stringify(payload, null, 2));
    return;
  }

  console.log('A1 = VW Resonance Integrity Scan');
  console.table(
    results.map(({ file, hash }) => ({ File: file, SHA384: hash })),
  );
  console.log('Chain Coherence SHA-384:', chain);

  if (previous) {
    console.log(
      matches
        ? 'Chain matches provided prior hash.'
        : 'Chain does not match the provided prior hash.',
    );
  }
}

main();
