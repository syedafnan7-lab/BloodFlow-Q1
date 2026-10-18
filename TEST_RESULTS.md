# BloodFlow-Q Test Results

**Run date:** 2026-10-18
**Branch:** `codex/round2-research-hardening`

## Checks after implementation

| Command/check | Result |
|---|---|
| `.venv\Scripts\python.exe -m pytest -q tests/test_qubo_consistency.py tests/test_api.py tests/test_benchmark.py` | Pass — 37 tests in 4.16 seconds |
| `.venv\Scripts\python.exe -m pytest -q` | Pass — 159 tests, 17 subtests, 5.62 seconds |
| `npm test` (from `frontend`) | Pass — 7 tests, 0 failures |
| `$env:VITE_API_BASE_URL='https://bloodflow-q-api.vercel.app'; npm run build` | Pass — Vite production build completed |
| `npm audit --omit=dev` (from `frontend`) | Pass — 0 vulnerabilities |
| `npm audit` (from `frontend`) | Pass — 0 vulnerabilities |
| `git diff --check` | Pass — no whitespace errors; Git noted existing LF-to-CRLF working-copy conversions for the pre-existing workflow doc and stylesheet |
| Limited credential-pattern scan | No matches for private-key headers or common AWS/GitHub/Slack token forms |
| Dashboard preview at `http://127.0.0.1:5173/` with local API on port 8000 | Pass — API connected; synthetic scenario metrics and refreshed responsive dashboard rendered |
| Production build after dashboard visual refresh | Pass — 1,680 modules transformed; Vite build completed with `VITE_API_BASE_URL` set |

The targeted tests cover the new bound helper, automatic benchmark penalties and effective configuration, and rejection of oversized direct-QAOA inputs before QUBO construction.

## Baseline before implementation

Before code changes, the repository passed 156 backend tests, 7 frontend tests, and the frontend production build. The final counts above include three added backend regressions.

## Checks unavailable or not configured

- `pip-audit`, `gitleaks`, `ruff`, and `mypy` are not installed in the local environment. Python dependency auditing and dedicated secret scanning therefore remain unverified.
- `frontend/package.json` has no lint or type-check script; the repository has no `.github/workflows` CI configuration.
- No Playwright/browser end-to-end suite is configured or was run.

No test or build failure remains from the implemented changes.

## Handoff state — 2026-10-18

- `f8c8b91` is the committed QAOA hardening/audit change. It is 1 commit ahead of the remote branch and has not been pushed.
- The cross-route UI refresh in `frontend/src/App.jsx`, `frontend/src/pages/Dashboard.jsx`, and `frontend/src/styles.css` is included in the local branch commit. The pre-existing edit in `docs/PRODUCT_WORKFLOW_AND_INTEROPERABILITY.md` was preserved and left out.
- After the cross-route visual and app-shell updates, the full suites were rerun: 159 backend tests + 17 subtests passed, 7 frontend tests passed, and the production build succeeded. All 14 routes were manually opened in the local browser at a narrow mobile viewport; Network filtering was exercised. See `UI_UX_IMPROVEMENT_REPORT.md` for route notes and browser-review limits.
- Local preview startup commands and exact file/change inventory are in [`BRANCH_CHANGE_SUMMARY.md`](BRANCH_CHANGE_SUMMARY.md).
