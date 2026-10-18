# BloodFlow-Q Branch Change Summary

**Audit date:** 2026-10-18 (Asia/Kolkata)
**Destination checkout:** `C:\Users\HP\OneDrive\Desktop\Afnan\BloodFlow-Q1`
**Destination branch:** `codex/round2-research-hardening`
**Default branch:** `main`
**Linked source repository:** `Beezsy-del/BloodFlow-Q`

## Repository and branch inventory

The directive's repository and the attached local checkout have different owners and names. The checkout remote is `syedafnan7-lab/BloodFlow-Q1`; the linked source is `Beezsy-del/BloodFlow-Q`. Both are public and share the exact `main` commit `50c3b2476042af2227f77997fbd7e0cdd61904b4`. The linked source connection is pull-only. The current Codex checkout is the destination; no remote was changed.

| Repository / branch | Head | Relation to shared base | Findings |
|---|---|---|---|
| `syedafnan7-lab/BloodFlow-Q1` `main` / `origin/main` | `50c3b24` | Shared base | Default branch; includes prior emergency-satisfaction fix and donor/emergency coordination work. |
| `syedafnan7-lab/BloodFlow-Q1` `codex/round2-research-hardening` | `d3ec6d2` | 5 commits ahead of base, 0 behind `main` | Current Codex branch; five research/UI commits are unique to this branch. No conflict with base. |
| `Beezsy-del/BloodFlow-Q` `main` | `50c3b24` | Shared base | Default branch; same commit as destination `main`. |
| `Beezsy-del/BloodFlow-Q` `quantum-optimizer-fix` | `0f13187` | 2 commits ahead of base | Candidate source branch. One commit adds warm-start/XY QAOA; the next adds LP-based initialization and benchmark penalty handling. |

The current branch and the source feature branch diverge from the shared base: `HEAD...FETCH_HEAD` is 5 commits on the Codex branch and 2 on `quantum-optimizer-fix`. No branches were switched, modified, merged, or pushed.

## Codex branch commits beyond `main`

1. `2b4f05b` — reproducible Round 2 benchmark suite: checked-in configurations/results, analysis and tests.
2. `2cf1439` — QAOA initialization comparison: quantum-value protocol/findings, seed-based experiment runner/search methods, results and tests.
3. `e746ca7` — formatting cleanup for the quantum-value report.
4. `da87ef4` — research console polish: experiment reports, charts, tooltip, research metrics and tests.
5. `d3ec6d2` — decision-support dashboard and Quantum Optimization Lab.

Those commits add no back-end or quantum solver changes; the research pages consume saved artifacts and existing APIs. The frontend continues to distinguish live computation from precomputed measurements and avoids claiming quantum advantage.

## Source branch candidates

`quantum-optimizer-fix` changes 15 files. Commit `f059345` adds QAOA warm-start and XY-mixer controls, schemas, UI fields, and smoke tests. Commit `0f13187` adds a continuous LP method to the MILP class, derives QUBO penalties for benchmark calls, adjusts QAOA service responses and pages, adds tests, and writes `AUDIT_REPORT_COMPREHENSIVE.md`.

The current branch already isolates benchmark solver exceptions in `optimization/benchmark.py`, records QAOA failures without fabricated metrics, and has tests for these behaviors. That source-branch behavior is redundant. Its report and raw exception details were not copied. The source branch's warm-start/XY options have execution smoke tests but no comparative result demonstrating improvement. The LP is a transportation-network relaxation with integer capacities and demands; its integral structure makes it equivalent to the MILP baseline for this formulation, while duplicating model construction. Those changes were skipped.

The useful penalty-bound extraction was adapted into `quantum/qubo.py` and benchmark request handling. A local review also found and fixed a direct-QAOA resource issue: the API previously built a dense QUBO before checking the local simulator's qubit cap.

## Working-tree baseline and final state

Before this audit, the current branch already had two uncommitted edits: a toolchain/workflow section in `docs/PRODUCT_WORKFLOW_AND_INTEROPERABILITY.md` and a global reduced-motion rule in `frontend/src/styles.css`. Both were preserved. This audit leaves changes uncommitted and unpushed; see `TEST_RESULTS.md` for checks and `CHANGE_PORTING_REPORT.md` for decisions.
