# Quantum value experiment protocol

## Research question

On the current small synthetic BloodFlow-Q allocation suite, does a best-measured
QAOA candidate improve the result of a bounded classical local search compared
with the same local search initialized conventionally? The hypothesis is
unresolved; a classical win or tie is an expected valid outcome.

## Scope and success criteria

The primary endpoint is the original weighted allocation objective on an
independently validated feasible allocation. A positive paired improvement is
defined as `classical_multistart objective - hybrid objective`; positive favors
the QAOA-initialized hybrid. Compare only shared seeds where both candidates are
feasible. Report raw QAOA separately and count every attempt, including errors
and infeasible samples.

An outcome is considered a *promising signal for further study* only if, on at
least one scenario, the hybrid has at least 5% lower mean objective than the
classical multistart method, the descriptive paired 95% bootstrap interval is
entirely above zero, and the hybrid feasibility rate is no lower. This is a
screening rule, not a significance claim. A tie, worse outcome, or unmet rule
means this experiment does not support a quantum contribution. No result from
this protocol can establish quantum advantage.

## Compared methods

1. Greedy, MILP/HiGHS, and bounded Exact provide existing baselines and an
   optimum-capable reference when the latter two agree.
2. `classical_multistart` runs the same feasible one-unit add/remove/transfer
   best-improvement search from one Greedy result and three seed-controlled
   random feasible allocations. Its total objective evaluation budget is 100.
3. `qaoa` reports only the lowest-QUBO-energy measured bitstring from the local
   Qiskit Aer run, decoded and rescored under the original objective. The raw
   candidate and validator status are preserved.
4. `hybrid_qaoa_local_search` applies the same local search, with the same
   100-objective-evaluation cap, to that exact raw QAOA candidate. If the
   measured candidate is infeasible, refinement is not run and the result is
   marked `skipped_infeasible_qaoa_seed`. There is no repair or postselection.

The QAOA candidate's optimizer and simulator resources are additional work,
not free initialization. Report end-to-end time, QAOA-pipeline time, and search
time separately. Classical search uses objective-evaluation count as its
explicit bounded budget; it is not claimed to equal quantum shots or QAOA
statevector evaluations. Runtime comparisons are local measurements and do not
establish speedup.

## Scenario suite and fixed configuration

The six-case Round 2 suite is unchanged: normal reference, inventory shortage,
transport-cost trade-off, emergency demand spike, route disruption, and a
2-bank/2-hospital/1-group/4-route scenario. All data are synthetic. MILP and
Exact objectives are checked for agreement before either is used as the
reference or for the predefined target. The target is 5% above that objective.

The confirmatory run uses ten paired seeds, QAOA depth `p=1`, 128 shots,
COBYLA, 15 optimizer iterations, and both QUBO penalties at 10,000. These fixed
settings isolate the initialization question rather than launch a parameter
sweep. No depth, shot, penalty, or initialization sweep is part of this run.

## Timing and uncertainty

- `runtime_seconds` is the method's end-to-end runner timing, including model
  preparation, decoding, and independent feasibility validation where relevant.
- `qaoa_runtime_seconds` covers QUBO creation through QAOA sample decoding and
  validation for the hybrid path.
- `search_runtime_seconds` covers the local-improvement stage.
- Classical multistart begins by producing and validating a Greedy seed, so its
  time to first feasible includes the Greedy initialization time.
- Hybrid time to first feasible includes QAOA candidate production and
  validation. Time to target is end-to-end from the method start and targets
  5% above the verified optimum reference.
- Report paired differences by scenario and a deterministic 5,000-resample
  percentile bootstrap interval over seed pairs. Seeds are repeated runs of
  the same six instances, not independent scenario designs; intervals do not
  describe generalization to other allocation networks.

## Run provenance

The seed-101 and seed-201 runs were exploratory implementation checks and are
excluded from the confirmatory findings. This protocol and the analysis code
were finalized before the confirmatory run using seeds 301–310. The raw JSON stores per-run candidates,
allocations, validation reports, runtime fields, and the full configuration;
the matching configuration and source hashes accompany it. The generated
report is derived from, and does not modify, the raw JSON.

## Limitations

The local Aer simulator executes on classical hardware. These instances are
tiny and tractable for classical methods. The local search is a bounded
research baseline, not an exhaustive or state-of-the-art search. The protocol
tests one QAOA configuration and one neighborhood; it cannot rule out every
possible hybrid design. Simplified compatibility and route assumptions are
synthetic and are not clinical rules or operational delivery advice.
