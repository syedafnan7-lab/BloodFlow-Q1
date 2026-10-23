import test from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { summarizeWarmQAOARuns } from '../src/utils/warmQAOAMetrics.js';
import { readFileSync as readSync } from 'node:fs';

const studyArtifact = JSON.parse(readFileSync(new URL('../public/warm-qaoa-paired-20261022.json', import.meta.url), 'utf8'));
const comparisonSource = readFileSync(new URL('../src/components/WarmQAOAComparison.jsx', import.meta.url), 'utf8');
const reportsSource = readFileSync(new URL('../src/pages/ExperimentReports.jsx', import.meta.url), 'utf8');
const canonicalWarmArtifact = JSON.parse(readSync(new URL('../../experiments/results/warm-qaoa-paired-20261022.json', import.meta.url), 'utf8'));
const canonicalWarmConfig = JSON.parse(readSync(new URL('../../experiments/configurations/warm-qaoa-paired-20261022.json', import.meta.url), 'utf8'));
const publicWarmConfig = JSON.parse(readSync(new URL('../public/warm-qaoa-paired-20261022-configuration.json', import.meta.url), 'utf8'));

test('reports prominently connect the paired experiment to its recorded artifact', () => {
  assert.match(comparisonSource, /LP warm-start QAOA/);
  assert.match(reportsSource, /useWarmQAOAStudy/);
  assert.match(comparisonSource, /study\.summary\.run_count/);
  assert.match(comparisonSource, /paired_completed_seeds/);
  assert.equal(studyArtifact.summary.run_count, 120);
  assert.equal(studyArtifact.summary.completed_runs, 120);
  assert.equal(studyArtifact.summary.scenario_count, 6);
  assert.equal(studyArtifact.summary.paired_seed_count, 10);
  assert.equal(studyArtifact.summary.paired_scenario_summary.reduce((count, scenario) => count + scenario.paired_completed_seeds, 0), 60);
  assert.match(reportsSource, /<WarmQAOAComparison study=\{warmStudy\} error=\{warmError\} \/>/);
  assert.ok(reportsSource.indexOf('studyId === \'warm-start\' && <WarmQAOAComparison') < reportsSource.indexOf('LEGACY CONFIRMATORY BENCHMARK'));
});

test('the legacy benchmark retains its original method labels and separate-study label', () => {
  assert.match(reportsSource, /qaoa: 'Raw QAOA'/);
  assert.match(reportsSource, /hybrid_qaoa_local_search: 'Hybrid refinement'/);
  assert.match(reportsSource, /LEGACY CONFIRMATORY BENCHMARK · SEPARATE STUDY/);
  assert.match(comparisonSource, /\/warm-qaoa-paired-20261022\.json/);
  assert.match(comparisonSource, /warm-qaoa-study-report\.md/);
  assert.match(comparisonSource, /warm-qaoa-reproducibility\.md/);
});

test('study switcher keeps the two persisted research studies distinct and links their guides', () => {
  assert.match(reportsSource, /value="warm-start"/);
  assert.match(reportsSource, /value="round2"/);
  assert.match(reportsSource, /value="confirmatory"/);
  assert.match(reportsSource, /warm-qaoa-reproducibility\.md/);
  assert.match(reportsSource, /quantum-value-reproducibility\.md/);
  assert.match(reportsSource, /round2-benchmark-reproducibility\.md/);
  assert.match(reportsSource, /studyId === 'warm-start'/);
  assert.match(reportsSource, /studyId === 'confirmatory'/);
  assert.match(reportsSource, /useWarmQAOAStudy/);
  assert.deepEqual(publicWarmConfig, canonicalWarmConfig);
  assert.deepEqual(studyArtifact, canonicalWarmArtifact);
});

test('warm study comparison exposes actual paired uncertainty, filters, run inspection and filtered CSV export', () => {
  assert.match(comparisonSource, /paired_difference_bootstrap_95_percentile_ci/);
  assert.match(comparisonSource, /warm-measure/);
  assert.match(comparisonSource, /aria-pressed/);
  assert.match(comparisonSource, /setSelectedSeed/);
  assert.match(comparisonSource, /downloadCsv\(runs, selected\)/);
  assert.match(comparisonSource, /seed_preprocessing_seconds/);
  assert.match(comparisonSource, /Methods, provenance & limitations/);
  assert.equal(studyArtifact.summary.paired_scenario_summary.filter((item) => item.paired_difference_bootstrap_95_percentile_ci[0] > 0).length, 5);
});

test('feasible shot rate retains infeasible shots in its denominator', () => {
  const summary = summarizeWarmQAOARuns([
    { variant: 'standard', status: 'completed', shots: 64, feasible_shots: 16, feasible_shot_rate: 0.25, best_feasible_objective: 12 },
    { variant: 'standard', status: 'completed', shots: 64, feasible_shots: 0, feasible_shot_rate: 0, best_feasible_objective: null },
  ]);
  assert.equal(summary[0].meanFeasibleShotRate, 0.125);
  assert.equal(summary[0].measuredShots, 128);
  assert.equal(summary[0].feasibleShots, 16);
  assert.equal(summary[0].feasibleRuns, 1);
});

test('failed and unsupported attempts remain visible but do not gain fabricated metrics', () => {
  const summary = summarizeWarmQAOARuns([
    { variant: 'lp_warm_start', status: 'error', shots: 64, runtime_seconds: 0.2, feasible_shot_rate: null },
    { variant: 'lp_warm_start', status: 'skipped_too_large', shots: 64, feasible_shot_rate: null },
  ]);
  assert.equal(summary[1].attempts, 2);
  assert.equal(summary[1].completed, 0);
  assert.equal(summary[1].failures, 2);
  assert.equal(summary[1].meanFeasibleShotRate, null);
  assert.equal(summary[1].meanRuntimeSeconds, 0.2);
  assert.equal(summary[1].measuredShots, 0);
});

test('empty data yields unavailable values rather than zero-valued success', () => {
  const summary = summarizeWarmQAOARuns([]);
  assert.deepEqual(summary.map((row) => row.meanFeasibleShotRate), [null, null]);
  assert.deepEqual(summary.map((row) => row.medianBestFeasibleObjective), [null, null]);
});

test('runtime summaries use the conventional even-sample median', () => {
  const summary = summarizeWarmQAOARuns([
    { variant: 'standard', status: 'completed', runtime_seconds: 0.1, feasible_shot_rate: 0.2 },
    { variant: 'standard', status: 'completed', runtime_seconds: 0.3, feasible_shot_rate: 0.4 },
  ]);
  assert.equal(summary[0].medianRuntimeSeconds, 0.2);
});
