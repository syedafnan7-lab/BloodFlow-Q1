# Round 2 benchmark reproducibility

This page reports the historical single-run Round 2 comparison as a separate exploratory study. It is not the repeated confirmatory benchmark or the LP warm-start paired experiment.

- Browser artifact: [`round2-benchmark-20261007-01.json`](../round2-benchmark-20261007-01.json)
- Canonical result: `experiments/results/20261007-01.json`
- Matching analysis: `experiments/results/20261007-01-analysis.json`
- Matching run configuration: embedded in the canonical result artifact.
- Shared reproduction notes: [`REPRODUCIBILITY.md`](https://github.com/syedafnan7-lab/BloodFlow-Q1/blob/codex/warm-qaoa-integration/docs/REPRODUCIBILITY.md)

The artifact has one run per method per synthetic scenario, so it does not support paired confidence intervals. Exact is a classical small-instance reference. QAOA measurements use local simulation, not quantum hardware.
