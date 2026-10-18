# Change Porting Report

**Destination checkout:** `C:\Users\HP\OneDrive\Desktop\Afnan\BloodFlow-Q1`
**Destination branch:** `codex/round2-research-hardening`
**Source repository from the directive:** `Beezsy-del/BloodFlow-Q`
**Source branch reviewed:** `quantum-optimizer-fix` (two commits beyond `main`)
**Comparison base:** shared commit `50c3b2476042af2227f77997fbd7e0cdd61904b4`

The active checkout is a separate repository (`syedafnan7-lab/BloodFlow-Q1`) but shares the exact base commit with the linked source repository. The current Codex branch is treated as the destination; implementation stays on that branch. The linked source repository is readable but its GitHub permission is pull-only. The adapted QUBO hardening work was committed locally as `f8c8b91`; no push, merge, or change to another branch was performed. Cross-route UI work remains uncommitted; see `BRANCH_CHANGE_SUMMARY.md` and `UI_UX_IMPROVEMENT_REPORT.md` for current state and route review. A fresh fetch confirmed `origin/main` at `50c3b24`, an ancestor of the current branch; there are no main-only changes to port.

## Selective porting matrix

| Candidate change | Source branch | Already in destination? | Value | Risk | Decision |
|---|---|---|---|---|---|
| Warm-start QAOA initialized from the continuous relaxation | `quantum-optimizer-fix` commit `f059345` | No; current QAOA uses uniform Hadamards and X mixer | Research comparison, but no measured benefit supplied | High: new ansatz and classical initialization need comparative evidence | SKIP; retain current default until a controlled experiment justifies another |
| XY mixer option | `quantum-optimizer-fix` commit `f059345` | No | Adds an alternative QAOA mixer | Medium: preserves excitation number, not BloodFlow feasibility; source only includes execution smoke tests | SKIP; no demonstrated gain or feasibility-preserving property |
| Continuous LP relaxation for warm-start | `quantum-optimizer-fix` commit `0f13187` | No; destination has integer MILP solver | This is a bipartite transportation network with integral capacities/demands; an LP optimum can be integral and duplicates the MILP baseline | Medium: duplicates constraint-matrix construction and has no comparison results | SKIP; no distinct benefit for this formulation |
| Derive conservative QUBO penalties when benchmark QAOA omits them | `quantum-optimizer-fix` commit `0f13187` | No; destination rejected missing benchmark weights | Removes an avoidable 422 while retaining a justified conservative bound | Low/Medium: actual values must remain inspectable | ADAPT; report effective weights and retain explicit requirements for direct QAOA calls |
| Per-solver benchmark failure isolation | `quantum-optimizer-fix` commit `0f13187` | Yes; `optimization/benchmark.py` already records each solver failure, with tests | Resilience | Low | SKIP as duplicate |
| Expose raw backend exception text in API errors | `quantum-optimizer-fix` commit `0f13187` | No | Limited diagnostic value | Medium: can disclose internal details; destination sanitizes server errors | SKIP; preserve safe client errors |
| Source branch's `AUDIT_REPORT_COMPREHENSIVE.md` | `quantum-optimizer-fix` commit `0f13187` | No | Some topics overlap existing project evidence | Claims require independent verification; duplicative report | SKIP; use reports based on this audit's verified evidence |
| Extract QUBO bound into reusable helper | `quantum-optimizer-fix` commit `0f13187` | No | Reusable calculation for safe benchmark configuration and tests | Low | ADAPT as part of automatic penalty handling |
| Reject oversized direct QAOA before dense QUBO construction | Destination-side review | No; prior check occurred inside the solver after construction | Avoids quadratic matrix allocation for requests that cannot run | Low | Implemented with regression test |

## Changes implemented

- Added `compute_conservative_objective_bound` and refactored `build_qubo` to use it. A numeric regression test checks the bound.
- Benchmark requests derive `max(100, 1.5 * maximum_scenario_bound + 10)` when QAOA penalties are omitted. Effective weights, the bound, and an auto-derived flag are included in experiment configuration.
- Direct `/optimize` and emergency QAOA calls still require explicit penalty weights.
- Direct API QAOA estimates the exact binary-variable count and rejects over-limit inputs before dense matrix construction.
- Updated API, benchmarking, security, and audit documentation.

## Verification

- Targeted backend tests: 37 passed.
- Full backend suite: 159 tests and 17 subtests passed.
- Frontend tests: 7 passed; production build passed.
- Full and production-only `npm audit`: zero vulnerabilities.
- See [`TEST_RESULTS.md`](TEST_RESULTS.md) and [`ENGINEERING_AUDIT_REPORT.md`](ENGINEERING_AUDIT_REPORT.md) for details.
