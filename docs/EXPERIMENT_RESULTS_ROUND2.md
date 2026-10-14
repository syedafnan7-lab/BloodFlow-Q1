# BloodFlow-Q Experiment Results

**Raw data:** [`round2-20261015-r2.json`](../experiments/results/round2-20261015-r2.json)
**Configuration:** [`round2-20261015-r2.json`](../experiments/configurations/round2-20261015-r2.json)

## Methodology

This report is generated from the raw JSON experiment output. It does not alter source measurements. Each method runs on the same fictional scenario with a shared objective. Greedy is the deterministic baseline; MILP uses HiGHS; Exact enumerates bounded allocation states up to its configured limit; QAOA uses the local Qiskit Aer simulator, samples finite-shot bitstrings, decodes them, and runs the shared classical feasibility validator. An infeasible QAOA sample is retained as infeasible and is not repaired. Runtime is measured locally and is environment-dependent.

## Number and size of scenarios

Suite: **round2**; scenarios: **6**. Full inputs and settings are in [`round2-20261015-r2.json`](../experiments/configurations/round2-20261015-r2.json). The Round 2 suite includes a deterministic 2-bank/2-hospital/1-group case with four routes. All values are synthetic. QUBO bit counts are reported per case; local QAOA is capped at 16 variables.

| Scenario | Banks | Hospitals | Groups | Routes | Allocation vars | Inventory units | Demand units | QUBO bits |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| normal_reference | 1 | 1 | 1 | 1 | 1 | 12 | 4 | 10 |
| inventory_shortage | 1 | 1 | 1 | 1 | 1 | 2 | 6 | 7 |
| transport_cost_tradeoff | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 3 |
| emergency_demand_spike | 1 | 1 | 1 | 1 | 1 | 12 | 16 | 13 |
| transport_disruption | 1 | 1 | 1 | 1 | 0 | 5 | 4 | 6 |
| multi_facility_tradeoff | 2 | 2 | 1 | 4 | 4 | 3 | 4 | 13 |

## Parameters

- Objective weights: `{"critical_unmet_weight": 10.0, "secondary_penalty_weight": 0.0, "total_unmet_weight": 5.0, "transportation_cost_weight": 1.0, "transportation_time_weight": 0.1}`
- QAOA: `{"base_seed": 7, "max_iterations": 15, "max_qubits": 16, "optimizer": "COBYLA", "p": 1, "repetitions": 5, "seed_sequence": [7, 8, 9, 10, 11], "shots": 128}`
- QAOA repetitions: `5` independent seeds per scenario; failures remain in raw results.
- QUBO penalty weights: `{"demand_penalty_weight": 10000.0, "inventory_penalty_weight": 10000.0}`
- Exact candidate-state cap: `50,000`
- Software versions: `{"numpy": "2.5.4", "qiskit": "2.5.2", "qiskit-aer": "0.17.2", "scipy": "1.18.1"}`

## Per-scenario results

`Feasible` is the validator result. A QAOA objective is reported only for a feasible decoded allocation; an infeasible measured candidate's raw objective expression is not comparable and is excluded from objective statistics. Approximation gap is `(method objective - reference objective) / abs(reference objective)` and is recorded only when the method and the optimum-capable reference are feasible. Runtime includes solving and the independent validation performed by this runner.

| Scenario | Method | Rep | Seed | Status | Objective | Critical satisfied | Unmet | Transport cost | Avg travel time | Feasible | Runtime (s) | Gap vs reference |
|---|---|---:|---:|---|---:|---:|---:|---:|---:|:---:|---:|---:|
| normal_reference | greedy | — | — | completed | 25.2 | 100.0% | 0 | 18 | 18 | True | 6.44e-05 | 0 |
| normal_reference | milp | — | — | completed | 25.2 | 100.0% | 0 | 18 | 18 | True | 0.0127332 | — |
| normal_reference | exact | — | — | completed | 25.2 | 100.0% | 0 | 18 | 18 | True | 0.0001411 | — |
| normal_reference | qaoa | 1 | 7 | completed | 82.6 | 50.0% | 2 | 9 | 18 | True | 0.198147 | 2.27778 |
| normal_reference | qaoa | 2 | 8 | completed | 25.2 | 100.0% | 0 | 18 | 18 | True | 0.175046 | 0 |
| normal_reference | qaoa | 3 | 9 | completed | 53.9 | 75.0% | 1 | 13.5 | 18 | True | 0.170571 | 1.13889 |
| normal_reference | qaoa | 4 | 10 | completed | 25.2 | 100.0% | 0 | 18 | 18 | True | 0.162197 | 0 |
| normal_reference | qaoa | 5 | 11 | completed | 25.2 | 100.0% | 0 | 18 | 18 | True | 0.163647 | 0 |
| inventory_shortage | greedy | — | — | completed | 152.6 | 33.3% | 4 | 9 | 18 | True | 0.0001238 | 0 |
| inventory_shortage | milp | — | — | completed | 152.6 | 33.3% | 4 | 9 | 18 | True | 0.0021966 | — |
| inventory_shortage | exact | — | — | completed | 152.6 | 33.3% | 4 | 9 | 18 | True | 0.0001179 | — |
| inventory_shortage | qaoa | 1 | 7 | completed | 152.6 | 33.3% | 4 | 9 | 18 | True | 0.140799 | 0 |
| inventory_shortage | qaoa | 2 | 8 | completed | 181.3 | 16.7% | 5 | 4.5 | 18 | True | 0.140579 | 0.188073 |
| inventory_shortage | qaoa | 3 | 9 | completed | 181.3 | 16.7% | 5 | 4.5 | 18 | True | 0.133263 | 0.188073 |
| inventory_shortage | qaoa | 4 | 10 | completed | 152.6 | 33.3% | 4 | 9 | 18 | True | 0.157403 | 0 |
| inventory_shortage | qaoa | 5 | 11 | completed | 152.6 | 33.3% | 4 | 9 | 18 | True | 0.145056 | 0 |
| transport_cost_tradeoff | greedy | — | — | completed | 41 | — | 0 | 40 | 10 | True | 6.89e-05 | 7.2 |
| transport_cost_tradeoff | milp | — | — | completed | 5 | — | 1 | 0 | — | True | 0.0014167 | — |
| transport_cost_tradeoff | exact | — | — | completed | 5 | — | 1 | 0 | — | True | 7.67e-05 | — |
| transport_cost_tradeoff | qaoa | 1 | 7 | completed | 5 | — | 1 | 0 | — | True | 0.130392 | 0 |
| transport_cost_tradeoff | qaoa | 2 | 8 | completed | 5 | — | 1 | 0 | — | True | 0.122202 | 0 |
| transport_cost_tradeoff | qaoa | 3 | 9 | completed | 5 | — | 1 | 0 | — | True | 0.124954 | 0 |
| transport_cost_tradeoff | qaoa | 4 | 10 | completed | 5 | — | 1 | 0 | — | True | 0.122239 | 0 |
| transport_cost_tradeoff | qaoa | 5 | 11 | completed | 5 | — | 1 | 0 | — | True | 0.135935 | 0 |
| emergency_demand_spike | greedy | — | — | completed | 215.6 | 75.0% | 4 | 54 | 18 | True | 5.81e-05 | 0 |
| emergency_demand_spike | milp | — | — | completed | 215.6 | 75.0% | 4 | 54 | 18 | True | 0.0013363 | — |
| emergency_demand_spike | exact | — | — | completed | 215.6 | 75.0% | 4 | 54 | 18 | True | 0.0003021 | — |
| emergency_demand_spike | qaoa | 1 | 7 | completed | 273 | 62.5% | 6 | 45 | 18 | True | 0.258664 | 0.266234 |
| emergency_demand_spike | qaoa | 2 | 8 | completed | 416.5 | 31.2% | 11 | 22.5 | 18 | True | 0.258229 | 0.931818 |
| emergency_demand_spike | qaoa | 3 | 9 | completed | 387.8 | 37.5% | 10 | 27 | 18 | True | 0.238658 | 0.798701 |
| emergency_demand_spike | qaoa | 4 | 10 | completed | 416.5 | 31.2% | 11 | 22.5 | 18 | True | 0.259129 | 0.931818 |
| emergency_demand_spike | qaoa | 5 | 11 | infeasible | 324.1 | 50.0% | 8 | 31.5 | 18 | False | 0.227376 | — |
| transport_disruption | greedy | — | — | completed | 140 | 0.0% | 4 | 0 | — | True | 6.41e-05 | 0 |
| transport_disruption | milp | — | — | completed | 140 | 0.0% | 4 | 0 | — | True | 0.0021181 | — |
| transport_disruption | exact | — | — | completed | 140 | 0.0% | 4 | 0 | — | True | 4.8e-05 | — |
| transport_disruption | qaoa | 1 | 7 | completed | 140 | 0.0% | 4 | 0 | — | True | 0.135371 | 0 |
| transport_disruption | qaoa | 2 | 8 | completed | 140 | 0.0% | 4 | 0 | — | True | 0.132317 | 0 |
| transport_disruption | qaoa | 3 | 9 | completed | 140 | 0.0% | 4 | 0 | — | True | 0.121043 | 0 |
| transport_disruption | qaoa | 4 | 10 | infeasible | 105 | 25.0% | 3 | 0 | — | False | 0.12631 | — |
| transport_disruption | qaoa | 5 | 11 | completed | 140 | 0.0% | 4 | 0 | — | True | 0.136398 | 0 |
| multi_facility_tradeoff | greedy | — | — | completed | 16.2 | 100.0% | 1 | 7.8 | 11.3333 | True | 7.81e-05 | 0 |
| multi_facility_tradeoff | milp | — | — | completed | 16.2 | 100.0% | 1 | 7.8 | 11.3333 | True | 0.0187184 | — |
| multi_facility_tradeoff | exact | — | — | completed | 16.2 | 100.0% | 1 | 7.8 | 11.3333 | True | 0.0010646 | — |
| multi_facility_tradeoff | qaoa | 1 | 7 | completed | 55.3 | 50.0% | 2 | 11 | 21.5 | True | 0.203214 | 2.41358 |
| multi_facility_tradeoff | qaoa | 2 | 8 | completed | 27 | 100.0% | 2 | 12 | 25 | True | 0.216639 | 0.666667 |
| multi_facility_tradeoff | qaoa | 3 | 9 | infeasible | 37.7 | 50.0% | 1 | 1.8 | 4.5 | False | 0.215583 | — |
| multi_facility_tradeoff | qaoa | 4 | 10 | infeasible | 11.2 | 100.0% | 2 | 0.8 | 4 | False | 0.19943 | — |
| multi_facility_tradeoff | qaoa | 5 | 11 | completed | 39.2 | 50.0% | 1 | 2.8 | 4.66667 | True | 0.216934 | 1.41975 |

## QAOA repeated-run summary by scenario

Objective statistics below use feasible measured candidates only. Feasibility rate uses all attempted seeds, including errors.

| Scenario | Attempts | Measured | Feasible | Feasibility rate | Mean feasible objective | Median | Population SD | Mean runtime (s) |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| normal_reference | 5 | 5 | 5 | 1 | 42.42 | 25.2 | 22.96 | 0.173922 |
| inventory_shortage | 5 | 5 | 5 | 1 | 164.08 | 152.6 | 14.0601 | 0.14342 |
| transport_cost_tradeoff | 5 | 5 | 5 | 1 | 5 | 5 | 0 | 0.127145 |
| emergency_demand_spike | 5 | 5 | 4 | 0.8 | 373.45 | 402.15 | 59.1666 | 0.248411 |
| transport_disruption | 5 | 5 | 4 | 0.8 | 140 | 140 | 0 | 0.130288 |
| multi_facility_tradeoff | 5 | 5 | 3 | 0.6 | 40.5 | 39.2 | 11.5899 | 0.21036 |

## Summary statistics

Mean, median, minimum, maximum, and population standard deviation are calculated across available measurements only. No missing or failed run is converted to zero. Objective summaries use feasible results only; the remaining metrics use actual completed outputs, including infeasible QAOA samples. Critical satisfaction is summarized as a fraction from 0 to 1 (the scenario table shows percentages).

### Greedy

Attempts: `6`; completed: `6`; feasible: `6`; infeasible: `0`; feasible/attempted: `1.0`; statuses: `{'completed': 6}`.

| Metric | n | Mean | Median | Min | Max | Std. dev. (population) |
|---|---:|---:|---:|---:|---:|---:|
| Objective | 6 | 98.4333 | 90.5 | 16.2 | 215.6 | 75.0709 |
| Critical satisfaction rate | 5 | 0.616667 | 0.75 | 0 | 1 | 0.392994 |
| Total unmet demand | 6 | 2.16667 | 2.5 | 0 | 4 | 1.86339 |
| Transport cost | 6 | 21.4667 | 13.5 | 0 | 54 | 19.2221 |
| Average travel time | 5 | 15.0667 | 18 | 10 | 18 | 3.61724 |
| Runtime (seconds) | 6 | 7.62333e-05 | 6.665e-05 | 5.81e-05 | 0.0001238 | 2.21206e-05 |
| Approximation gap vs Exact | 6 | 1.2 | 0 | 0 | 7.2 | 2.68328 |

### Milp

Attempts: `6`; completed: `6`; feasible: `6`; infeasible: `0`; feasible/attempted: `1.0`; statuses: `{'completed': 6}`.

| Metric | n | Mean | Median | Min | Max | Std. dev. (population) |
|---|---:|---:|---:|---:|---:|---:|
| Objective | 6 | 92.4333 | 82.6 | 5 | 215.6 | 80.6526 |
| Critical satisfaction rate | 5 | 0.616667 | 0.75 | 0 | 1 | 0.392994 |
| Total unmet demand | 6 | 2.33333 | 2.5 | 0 | 4 | 1.69967 |
| Transport cost | 6 | 14.8 | 8.4 | 0 | 54 | 18.5634 |
| Average travel time | 4 | 16.3333 | 18 | 11.3333 | 18 | 2.88675 |
| Runtime (seconds) | 6 | 0.00641988 | 0.00215735 | 0.0013363 | 0.0187184 | 0.00681087 |
| Approximation gap vs Exact | 0 | — | — | — | — | — |

### Exact

Attempts: `6`; completed: `6`; feasible: `6`; infeasible: `0`; feasible/attempted: `1.0`; statuses: `{'completed': 6}`.

| Metric | n | Mean | Median | Min | Max | Std. dev. (population) |
|---|---:|---:|---:|---:|---:|---:|
| Objective | 6 | 92.4333 | 82.6 | 5 | 215.6 | 80.6526 |
| Critical satisfaction rate | 5 | 0.616667 | 0.75 | 0 | 1 | 0.392994 |
| Total unmet demand | 6 | 2.33333 | 2.5 | 0 | 4 | 1.69967 |
| Transport cost | 6 | 14.8 | 8.4 | 0 | 54 | 18.5634 |
| Average travel time | 4 | 16.3333 | 18 | 11.3333 | 18 | 2.88675 |
| Runtime (seconds) | 6 | 0.000291733 | 0.0001295 | 4.8e-05 | 0.0010646 | 0.000354961 |
| Approximation gap vs Exact | 0 | — | — | — | — | — |

### Qaoa

Attempts: `30`; completed: `30`; feasible: `26`; infeasible: `4`; feasible/attempted: `0.8666666666666667`; statuses: `{'completed': 26, 'infeasible': 4}`.

| Metric | n | Mean | Median | Min | Max | Std. dev. (population) |
|---|---:|---:|---:|---:|---:|---:|
| Objective | 26 | 124.338 | 111.3 | 5 | 416.5 | 124.187 |
| Critical satisfaction rate | 25 | 0.458333 | 0.375 | 0 | 1 | 0.330981 |
| Total unmet demand | 30 | 3.43333 | 2.5 | 0 | 11 | 3.07336 |
| Transport cost | 30 | 9.64667 | 6.75 | 0 | 45 | 11.1989 |
| Average travel time | 20 | 16.4833 | 18 | 4 | 25 | 5.34449 |
| Runtime (seconds) | 30 | 0.172258 | 0.1598 | 0.121043 | 0.259129 | 0.0454657 |
| Approximation gap vs Exact | 26 | 0.431592 | 0 | 0 | 2.41358 | 0.691818 |

## Interpretation

These measurements describe only this small synthetic instance set and this local software environment. Greedy, MILP, and Exact outputs can be compared on the same objective. Exact is an exhaustive reference only for cases solved within its cap; MILP is an optimum reference only when HiGHS reports success. Repeated QAOA seeds are descriptive observations, not formal statistical evidence. QAOA uses a hybrid classical optimizer and local simulator, so its runtime includes classical optimization and simulator work. Finite shots can yield infeasible samples; those remain visible. The sample is too small and the execution setup too limited to support broad performance claims.

## Limitations

- Cases remain small synthetic research instances; the two-bank/two-hospital case is not representative of an operational network.
- Compatibility is a simplified prototype assumption, not a complete clinical compatibility model.
- Local simulator results and wall-clock timings depend on package versions, machine load, and platform.
- The QAOA candidate is a measured sample, not an optimality proof. Infeasible samples are not repaired.
- The fixed seed supports repeatability but does not guarantee bit-identical results across environments.

## Quantum advantage statement

**These results do not demonstrate quantum advantage.** They are small, local simulator experiments with a hybrid classical-quantum workflow. No comparison establishes an advantage over classical optimization in runtime, quality, scale, or energy use.

## Data integrity

Raw result values are preserved in the linked JSON output. This report contains derived descriptive statistics only; it does not overwrite or edit raw results.
