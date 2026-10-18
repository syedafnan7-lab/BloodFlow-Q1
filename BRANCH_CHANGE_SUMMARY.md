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
| `syedafnan7-lab/BloodFlow-Q1` `codex/round2-research-hardening` | `f8c8b91` | 6 commits ahead of base, 0 behind `main`; 1 commit ahead of origin | Current Codex branch; QAOA hardening audit committed locally. Dashboard refresh and earlier user edits were present in the working tree at audit handoff. |
| `Beezsy-del/BloodFlow-Q` `main` | `50c3b24` | Shared base | Default branch; same commit as destination `main`. |
| `Beezsy-del/BloodFlow-Q` `quantum-optimizer-fix` | `0f13187` | 2 commits ahead of base | Candidate source branch. One commit adds warm-start/XY QAOA; the next adds LP-based initialization and benchmark penalty handling. |

The current branch and the source feature branch diverge from the shared base: `HEAD...FETCH_HEAD` is 6 commits on the Codex branch and 2 on `quantum-optimizer-fix`. No branches were switched, merged, or pushed.

The latest fetched `origin/main` is `50c3b24`, an ancestor of current HEAD. This branch is 6 commits ahead and 0 behind; no main-only features need porting.

## Codex branch commits beyond `main`

1. `2b4f05b` — reproducible Round 2 benchmark suite: checked-in configurations/results, analysis and tests.
2. `2cf1439` — QAOA initialization comparison: quantum-value protocol/findings, seed-based experiment runner/search methods, results and tests.
3. `e746ca7` — formatting cleanup for the quantum-value report.
4. `da87ef4` — research console polish: experiment reports, charts, tooltip, research metrics and tests.
5. `d3ec6d2` — decision-support dashboard and Quantum Optimization Lab.
6. `f8c8b91` — conservative QUBO benchmark penalties and early QAOA size guard, with regressions and audit documentation.

The first five commits add the research pages and consume saved artifacts and existing APIs. The sixth adds backend/QUBO hardening. The frontend continues to distinguish live computation from precomputed measurements and avoids claiming quantum advantage.

## Source branch candidates

`quantum-optimizer-fix` changes 15 files. Commit `f059345` adds QAOA warm-start and XY-mixer controls, schemas, UI fields, and smoke tests. Commit `0f13187` adds a continuous LP method to the MILP class, derives QUBO penalties for benchmark calls, adjusts QAOA service responses and pages, adds tests, and writes `AUDIT_REPORT_COMPREHENSIVE.md`.

The current branch already isolates benchmark solver exceptions in `optimization/benchmark.py`, records QAOA failures without fabricated metrics, and has tests for these behaviors. That source-branch behavior is redundant. Its report and raw exception details were not copied. The source branch's warm-start/XY options have execution smoke tests but no comparative result demonstrating improvement. The LP is a transportation-network relaxation with integer capacities and demands; its integral structure makes it equivalent to the MILP baseline for this formulation, while duplicating model construction. Those changes were skipped.

The useful penalty-bound extraction was adapted into `quantum/qubo.py` and benchmark request handling. A local review also found and fixed a direct-QAOA resource issue: the API previously built a dense QUBO before checking the local simulator's qubit cap.

## Working-tree baseline and final state

The QAOA hardening audit was committed locally as `f8c8b91`; it has not been pushed. At audit handoff, the working tree had nine modified tracked files plus the new UI report. The user authorized committing the UI/audit set locally; the pre-existing workflow document was excluded.

- `docs/PRODUCT_WORKFLOW_AND_INTEROPERABILITY.md`: 51-line toolchain/workflow review that predated the audit.
- `frontend/src/styles.css`: pre-existing reduced-motion work, dashboard refresh, and shared cross-route styling for navigation, headers, panels, tables, metrics, forms, buttons, and responsive layouts.
- `frontend/src/pages/Dashboard.jsx`: operations-focused heading, synthetic network illustration, and scenario metric-grid updates.
- `frontend/src/App.jsx`: workspace-selector accessibility labeling and keyed page-entry transitions.
- `BRANCH_CHANGE_SUMMARY.md`, `CHANGELOG_AUDIT.md`, `CHANGE_PORTING_REPORT.md`, `ENGINEERING_AUDIT_REPORT.md`, and `TEST_RESULTS.md`: audit and handoff records.

All 14 routes were opened in the local browser; layouts, representative content, and route controls rendered, and Network filtering was exercised. Detailed findings are in `UI_UX_IMPROVEMENT_REPORT.md`. Backend and frontend tests and the production build passed after the cross-route refresh. For a local preview, run the backend with `.venv\\Scripts\\python.exe -m uvicorn backend.main:app --host 127.0.0.1 --port 8000`, then in `frontend` set `$env:VITE_API_BASE_URL='http://127.0.0.1:8000'` and run `npm run dev -- --host 127.0.0.1 --port 5173`. The in-app preview is `http://127.0.0.1:5173/`. See `TEST_RESULTS.md`, `UI_UX_IMPROVEMENT_REPORT.md`, and `CHANGE_PORTING_REPORT.md` for verification and decisions.
