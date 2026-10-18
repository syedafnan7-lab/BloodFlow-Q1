# BloodFlow-Q Engineering Audit Report

**Audit date:** 2026-10-18
**Destination branch:** `codex/round2-research-hardening`
**Scope:** current checkout, its tracked feature branch and working-tree edits, the linked repository's accessible branches, API/QAOA/optimization paths, tests, frontend build, dependency audit, and secret-pattern scan.

## Executive findings

Two safe improvements were implemented on the current Codex branch:

1. Benchmark requests that include QAOA can omit penalty weights. The service derives conservative values from the largest objective bound in the request and returns the effective weights, bound, and derivation flag for reproducibility.
2. Direct QAOA requests are rejected against the solver's exact binary-variable limit before the dense QUBO matrix is constructed. This prevents an over-limit scenario from triggering the matrix's quadratic memory allocation first.

No repository-wide defect requiring a broader architecture change was found in the scoped review. Main remaining risks concern deployment controls, not the synthetic local research workflow.

## Verified fixes

### Direct QAOA allocation guard — fixed

`BackendService._quantum_result` previously called `build_qubo` before `QAOASolver.solve` enforced its configured qubit limit. The QUBO builder allocates a dense matrix, so very large user-supplied quantities could cause unnecessary memory growth before the existing guard fired. The API now uses `count_scenario_qubo_variables` first and returns the established `qaoa_instance_too_large` 422 response without calling the builder. A regression test uses very large quantities and asserts the builder is not called.

### Optional benchmark penalties — fixed

The benchmark API returned 422 when `include_qaoa` was true and the caller omitted both QUBO penalty weights. It now computes the conservative non-negative objective bound across requested scenarios and selects `max(100, 1.5 * bound + 10)` for each penalty. The response includes the actual penalty values, the bound, and `penalties_auto_calculated`. Direct `/optimize` and emergency QAOA requests still require explicit weights. Tests verify both the successful benchmark and bound separation.

## Frontend review

- React/Vite build and the existing frontend metric tests pass.
- The UI keeps live and precomputed research results distinct and uses evidence-backed metrics in its research panels.
- The local working-tree reduced-motion rule was preserved. It disables animation/transition duration and scroll animation for users requesting reduced motion.
- The repository has no configured lint or type-check script. Frontend tests exercise research metric utilities, not full browser workflows; no E2E browser suite is configured.

## Backend and API review

- Request models reject unknown fields and constrain enums and nonnegative numeric values.
- API exceptions sanitize unexpected server failures; the linked source branch's suggestion to return raw exception strings was skipped to preserve this behavior.
- Benchmark solvers already fail independently, recording error/skipped states rather than manufacturing results or aborting valid classical rows. Existing regression tests cover this, so the source change was skipped as duplicate.
- The direct QAOA guard now runs before dense matrix creation. The benchmark runner already checks estimated variables before invoking the QAOA adapter.
- No caller-provided file path or shell execution is exposed through reviewed API routes.

## Security and dependency review

- Full `npm audit` and `npm audit --omit=dev` each reported 0 vulnerabilities.
- A limited scan for private-key headers and common AWS, GitHub, and Slack token formats found no matching files. `gitleaks` and `pip-audit` are not installed, so this is not a comprehensive secret or Python dependency scan.
- Production CORS requires explicit HTTPS origins and credentials are disabled. The optimizer API is unauthenticated and accepts synthetic aggregate scenarios only.
- **P1 before any shared/public API exposure:** request-body and scenario collection sizes are not globally bounded, and there is no API authentication or rate limiting. The QAOA guard limits dense matrix allocation for oversized QAOA requests, but it does not replace an HTTP body limit or general workload controls.
- The repository has no `.github/workflows` CI pipeline. Continuous test/build/dependency checks are a recommended P2 improvement.

## Performance and maintainability

- QAOA is explicitly capped to 16 qubits on the local simulator; the bundled full scenario requires 222 binary variables and is skipped before solver execution.
- The linked branch's LP warm-start adds a second copy of the allocation constraint matrix. For this network-flow structure with integer capacities/demands, the LP is integral, so it duplicates the MILP baseline rather than supplying a distinct relaxation. No comparative results were included; this was not carried over.
- The linked branch's XY mixer conserves excitation count, not allocation feasibility. Its tests only establish execution. It was not added absent controlled measurements and explicit constraints-aware evidence.
- No dependencies were added or changed.

## Prioritized recommendations

| Priority | Recommendation | Reason |
|---|---|---|
| P1 before shared deployment | Add request-body/collection limits and workload timeouts; add authentication/rate limits if the optimizer API is reachable beyond a trusted local environment. | Protect the unauthenticated synthetic API from oversized or repeated computational requests. |
| P2 | Add a GitHub Actions workflow for backend tests, frontend tests/build, and dependency scans. | Local verification currently has no automated branch gate. |
| P2 | Add browser-level tests for donor coordination, emergency flows, and the live solver comparison. | Current frontend tests cover metrics and saved-study data rather than user navigation and API error states. |
| P3 research | If warm-start or XY QAOA is revisited, preregister paired seeds and compare feasibility, objective, runtime, and a classical baseline; label mixer limitations in UI. | Avoid treating an ansatz option or smoke test as evidence of improvement. |

## Verification

See [`TEST_RESULTS.md`](TEST_RESULTS.md) for exact commands and outcomes. All 159 backend tests and all 7 frontend tests pass; production build succeeds; `git diff --check` passes. The engineering audit was committed locally as `f8c8b91`; it has not been pushed or deployed. A cross-route UI refresh remains uncommitted, as recorded in [`BRANCH_CHANGE_SUMMARY.md`](BRANCH_CHANGE_SUMMARY.md) and reviewed in [`UI_UX_IMPROVEMENT_REPORT.md`](UI_UX_IMPROVEMENT_REPORT.md).
