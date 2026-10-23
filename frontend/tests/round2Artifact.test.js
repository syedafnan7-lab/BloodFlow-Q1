import test from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';

const canonical = JSON.parse(readFileSync(new URL('../../experiments/results/20261007-01.json', import.meta.url), 'utf8'));
const served = JSON.parse(readFileSync(new URL('../public/round2-benchmark-20261007-01.json', import.meta.url), 'utf8'));
const reports = readFileSync(new URL('../src/pages/ExperimentReports.jsx', import.meta.url), 'utf8');
const component = readFileSync(new URL('../src/components/Round2BenchmarkComparison.jsx', import.meta.url), 'utf8');

test('Round 2 selector maps to the canonical served artifact and retains separate provenance', () => {
  assert.deepEqual(served, canonical);
  assert.equal(served.results.length, 15);
  assert.equal(Object.keys(served.configuration.scenarios).length, 5);
  assert.deepEqual([...new Set(served.results.map((row) => row.method))].sort(), ['exact', 'greedy', 'qaoa']);
  assert.match(reports, /useRound2Study/);
  assert.match(reports, /<Round2BenchmarkComparison study=\{round2Study\} error=\{round2Error\} \/>/);
  assert.match(component, /one run per method per case/);
  assert.match(component, /no repeated-seed uncertainty estimate/);
  assert.match(component, /downloadScenarioCsv\(visibleRows\)/);
});
