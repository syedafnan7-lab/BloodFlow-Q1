# BloodFlow-Q Experiment Results

**Raw data:** [`quantum-value-confirmatory-seed301-20261015.json`](../experiments/results/quantum-value-confirmatory-seed301-20261015.json)  
**Configuration:** [`quantum-value-confirmatory-seed301-20261015.json`](../experiments/configurations/quantum-value-confirmatory-seed301-20261015.json)
**Protocol:** [Quantum value experiment protocol](QUANTUM_VALUE_PROTOCOL.md)

## Methodology

This report is generated from the raw JSON experiment output. It does not alter source measurements. Each method runs on the same fictional scenario with a shared objective. Greedy is the deterministic baseline; MILP uses HiGHS; Exact enumerates bounded allocation states up to its configured limit; QAOA uses the local Qiskit Aer simulator, samples finite-shot bitstrings, decodes them, and runs the shared classical feasibility validator. An infeasible QAOA sample is retained as infeasible and is not repaired. The classical multistart and hybrid methods use the same bounded feasible one-unit add/remove/transfer local search. Classical starts come from greedy plus seeded feasible random allocations; hybrid starts only from a feasible raw QAOA candidate. A raw infeasible QAOA candidate is never repaired or used to initialize the hybrid. Search-stage time and end-to-end time are reported separately. Runtime is measured locally and is environment-dependent.

## Number and size of scenarios

Suite: **round2**; scenarios: **6**. Full inputs and settings are in [`quantum-value-confirmatory-seed301-20261015.json`](../experiments/configurations/quantum-value-confirmatory-seed301-20261015.json). The Round 2 suite includes a deterministic 2-bank/2-hospital/1-group case with four routes. All values are synthetic. QUBO bit counts are reported per case; local QAOA is capped at 16 variables.

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
- QAOA: `{"base_seed": 301, "max_iterations": 15, "max_qubits": 16, "optimizer": "COBYLA", "p": 1, "repetitions": 10, "seed_sequence": [301, 302, 303, 304, 305, 306, 307, 308, 309, 310], "shots": 128}`
- QAOA repetitions: `10` independent seeds per scenario; failures remain in raw results.
- Classical search: `{"neighborhood": "one-unit add/remove/transfer; best-improvement", "objective_evaluation_budget_per_run": 100, "random_starts": 3, "repetitions": 10, "seed_sequence": [301, 302, 303, 304, 305, 306, 307, 308, 309, 310]}`
- Hybrid search: `{"initialization": "best measured QAOA bitstring; infeasible raw candidates are not repaired", "objective_evaluation_budget_per_run": 100, "repetitions": 10, "seed_sequence": [301, 302, 303, 304, 305, 306, 307, 308, 309, 310]}`
- QUBO penalty weights: `{"demand_penalty_weight": 10000.0, "inventory_penalty_weight": 10000.0}`
- Exact candidate-state cap: `50,000`
- Software versions: `{"numpy": "2.5.4", "qiskit": "2.5.2", "qiskit-aer": "0.17.2", "scipy": "1.18.1"}`

## Per-scenario results

`Feasible` is the validator result. A QAOA objective is reported only for a feasible decoded allocation; an infeasible measured candidate's raw objective expression is not comparable and is excluded from objective statistics. Approximation gap is `(method objective - reference objective) / abs(reference objective)` and is recorded only when the method and the optimum-capable reference are feasible. Runtime includes solving and the independent validation performed by this runner.

| Scenario | Method | Rep | Seed | Status | Objective | Critical satisfied | Unmet | Transport cost | Avg travel time | Feasible | Runtime (s) | Gap vs reference |
|---|---|---:|---:|---|---:|---:|---:|---:|---:|:---:|---:|---:|
| normal_reference | greedy | — | — | completed | 25.2 | 100.0% | 0 | 18 | 18 | True | 8.06e-05 | 0 |
| normal_reference | milp | — | — | completed | 25.2 | 100.0% | 0 | 18 | 18 | True | 0.0028749 | — |
| normal_reference | exact | — | — | completed | 25.2 | 100.0% | 0 | 18 | 18 | True | 0.000125 | — |
| normal_reference | classical_multistart | 1 | 301 | completed | 25.2 | 100.0% | 0 | 18 | 18 | True | 0.0004199 | 0 |
| normal_reference | classical_multistart | 2 | 302 | completed | 25.2 | 100.0% | 0 | 18 | 18 | True | 0.0002241 | 0 |
| normal_reference | classical_multistart | 3 | 303 | completed | 25.2 | 100.0% | 0 | 18 | 18 | True | 0.0005565 | 0 |
| normal_reference | classical_multistart | 4 | 304 | completed | 25.2 | 100.0% | 0 | 18 | 18 | True | 0.0004487 | 0 |
| normal_reference | classical_multistart | 5 | 305 | completed | 25.2 | 100.0% | 0 | 18 | 18 | True | 0.000308 | 0 |
| normal_reference | classical_multistart | 6 | 306 | completed | 25.2 | 100.0% | 0 | 18 | 18 | True | 0.0003377 | 0 |
| normal_reference | classical_multistart | 7 | 307 | completed | 25.2 | 100.0% | 0 | 18 | 18 | True | 0.0003332 | 0 |
| normal_reference | classical_multistart | 8 | 308 | completed | 25.2 | 100.0% | 0 | 18 | 18 | True | 0.0004228 | 0 |
| normal_reference | classical_multistart | 9 | 309 | completed | 25.2 | 100.0% | 0 | 18 | 18 | True | 0.0004972 | 0 |
| normal_reference | classical_multistart | 10 | 310 | completed | 25.2 | 100.0% | 0 | 18 | 18 | True | 0.0004085 | 0 |
| normal_reference | qaoa | 1 | 301 | completed | 82.6 | 50.0% | 2 | 9 | 18 | True | 0.137669 | 2.27778 |
| normal_reference | qaoa | 2 | 302 | completed | 25.2 | 100.0% | 0 | 18 | 18 | True | 0.132059 | 0 |
| normal_reference | qaoa | 3 | 303 | infeasible | 47.6 | 75.0% | 1 | 9 | 18 | False | 0.131213 | — |
| normal_reference | qaoa | 4 | 304 | completed | 53.9 | 75.0% | 1 | 13.5 | 18 | True | 0.13021 | 1.13889 |
| normal_reference | qaoa | 5 | 305 | completed | 111.3 | 25.0% | 3 | 4.5 | 18 | True | 0.130469 | 3.41667 |
| normal_reference | qaoa | 6 | 306 | completed | 25.2 | 100.0% | 0 | 18 | 18 | True | 0.133261 | 0 |
| normal_reference | qaoa | 7 | 307 | completed | 140 | 0.0% | 4 | 0 | — | True | 0.125552 | 4.55556 |
| normal_reference | qaoa | 8 | 308 | completed | 82.6 | 50.0% | 2 | 9 | 18 | True | 0.128566 | 2.27778 |
| normal_reference | qaoa | 9 | 309 | completed | 25.2 | 100.0% | 0 | 18 | 18 | True | 0.129607 | 0 |
| normal_reference | qaoa | 10 | 310 | completed | 82.6 | 50.0% | 2 | 9 | 18 | True | 0.131476 | 2.27778 |
| normal_reference | hybrid_qaoa_local_search | 1 | 301 | completed | 25.2 | 100.0% | 0 | 18 | 18 | True | 0.137925 | 0 |
| normal_reference | hybrid_qaoa_local_search | 2 | 302 | completed | 25.2 | 100.0% | 0 | 18 | 18 | True | 0.132192 | 0 |
| normal_reference | hybrid_qaoa_local_search | 3 | 303 | skipped_infeasible_qaoa_seed | — | — | — | — | — | False | 0.131213 | — |
| normal_reference | hybrid_qaoa_local_search | 4 | 304 | completed | 25.2 | 100.0% | 0 | 18 | 18 | True | 0.130407 | 0 |
| normal_reference | hybrid_qaoa_local_search | 5 | 305 | completed | 25.2 | 100.0% | 0 | 18 | 18 | True | 0.130734 | 0 |
| normal_reference | hybrid_qaoa_local_search | 6 | 306 | completed | 25.2 | 100.0% | 0 | 18 | 18 | True | 0.13339 | 0 |
| normal_reference | hybrid_qaoa_local_search | 7 | 307 | completed | 25.2 | 100.0% | 0 | 18 | 18 | True | 0.125884 | 0 |
| normal_reference | hybrid_qaoa_local_search | 8 | 308 | completed | 25.2 | 100.0% | 0 | 18 | 18 | True | 0.128797 | 0 |
| normal_reference | hybrid_qaoa_local_search | 9 | 309 | completed | 25.2 | 100.0% | 0 | 18 | 18 | True | 0.129716 | 0 |
| normal_reference | hybrid_qaoa_local_search | 10 | 310 | completed | 25.2 | 100.0% | 0 | 18 | 18 | True | 0.131676 | 0 |
| inventory_shortage | greedy | — | — | completed | 152.6 | 33.3% | 4 | 9 | 18 | True | 4.15e-05 | 0 |
| inventory_shortage | milp | — | — | completed | 152.6 | 33.3% | 4 | 9 | 18 | True | 0.001225 | — |
| inventory_shortage | exact | — | — | completed | 152.6 | 33.3% | 4 | 9 | 18 | True | 7.67e-05 | — |
| inventory_shortage | classical_multistart | 1 | 301 | completed | 152.6 | 33.3% | 4 | 9 | 18 | True | 0.0003502 | 0 |
| inventory_shortage | classical_multistart | 2 | 302 | completed | 152.6 | 33.3% | 4 | 9 | 18 | True | 0.0002523 | 0 |
| inventory_shortage | classical_multistart | 3 | 303 | completed | 152.6 | 33.3% | 4 | 9 | 18 | True | 0.0003444 | 0 |
| inventory_shortage | classical_multistart | 4 | 304 | completed | 152.6 | 33.3% | 4 | 9 | 18 | True | 0.0003675 | 0 |
| inventory_shortage | classical_multistart | 5 | 305 | completed | 152.6 | 33.3% | 4 | 9 | 18 | True | 0.0002771 | 0 |
| inventory_shortage | classical_multistart | 6 | 306 | completed | 152.6 | 33.3% | 4 | 9 | 18 | True | 0.0003086 | 0 |
| inventory_shortage | classical_multistart | 7 | 307 | completed | 152.6 | 33.3% | 4 | 9 | 18 | True | 0.0002629 | 0 |
| inventory_shortage | classical_multistart | 8 | 308 | completed | 152.6 | 33.3% | 4 | 9 | 18 | True | 0.0004945 | 0 |
| inventory_shortage | classical_multistart | 9 | 309 | completed | 152.6 | 33.3% | 4 | 9 | 18 | True | 0.0004096 | 0 |
| inventory_shortage | classical_multistart | 10 | 310 | completed | 152.6 | 33.3% | 4 | 9 | 18 | True | 0.00034 | 0 |
| inventory_shortage | qaoa | 1 | 301 | completed | 152.6 | 33.3% | 4 | 9 | 18 | True | 0.1043 | 0 |
| inventory_shortage | qaoa | 2 | 302 | completed | 152.6 | 33.3% | 4 | 9 | 18 | True | 0.114314 | 0 |
| inventory_shortage | qaoa | 3 | 303 | completed | 152.6 | 33.3% | 4 | 9 | 18 | True | 0.115859 | 0 |
| inventory_shortage | qaoa | 4 | 304 | completed | 152.6 | 33.3% | 4 | 9 | 18 | True | 0.108225 | 0 |
| inventory_shortage | qaoa | 5 | 305 | completed | 152.6 | 33.3% | 4 | 9 | 18 | True | 0.113095 | 0 |
| inventory_shortage | qaoa | 6 | 306 | completed | 152.6 | 33.3% | 4 | 9 | 18 | True | 0.115777 | 0 |
| inventory_shortage | qaoa | 7 | 307 | completed | 152.6 | 33.3% | 4 | 9 | 18 | True | 0.112458 | 0 |
| inventory_shortage | qaoa | 8 | 308 | completed | 181.3 | 16.7% | 5 | 4.5 | 18 | True | 0.114149 | 0.188073 |
| inventory_shortage | qaoa | 9 | 309 | completed | 181.3 | 16.7% | 5 | 4.5 | 18 | True | 0.117044 | 0.188073 |
| inventory_shortage | qaoa | 10 | 310 | completed | 152.6 | 33.3% | 4 | 9 | 18 | True | 0.116769 | 0 |
| inventory_shortage | hybrid_qaoa_local_search | 1 | 301 | completed | 152.6 | 33.3% | 4 | 9 | 18 | True | 0.104424 | 0 |
| inventory_shortage | hybrid_qaoa_local_search | 2 | 302 | completed | 152.6 | 33.3% | 4 | 9 | 18 | True | 0.11444 | 0 |
| inventory_shortage | hybrid_qaoa_local_search | 3 | 303 | completed | 152.6 | 33.3% | 4 | 9 | 18 | True | 0.115969 | 0 |
| inventory_shortage | hybrid_qaoa_local_search | 4 | 304 | completed | 152.6 | 33.3% | 4 | 9 | 18 | True | 0.108358 | 0 |
| inventory_shortage | hybrid_qaoa_local_search | 5 | 305 | completed | 152.6 | 33.3% | 4 | 9 | 18 | True | 0.113214 | 0 |
| inventory_shortage | hybrid_qaoa_local_search | 6 | 306 | completed | 152.6 | 33.3% | 4 | 9 | 18 | True | 0.11589 | 0 |
| inventory_shortage | hybrid_qaoa_local_search | 7 | 307 | completed | 152.6 | 33.3% | 4 | 9 | 18 | True | 0.112616 | 0 |
| inventory_shortage | hybrid_qaoa_local_search | 8 | 308 | completed | 152.6 | 33.3% | 4 | 9 | 18 | True | 0.11431 | 0 |
| inventory_shortage | hybrid_qaoa_local_search | 9 | 309 | completed | 152.6 | 33.3% | 4 | 9 | 18 | True | 0.11721 | 0 |
| inventory_shortage | hybrid_qaoa_local_search | 10 | 310 | completed | 152.6 | 33.3% | 4 | 9 | 18 | True | 0.116885 | 0 |
| transport_cost_tradeoff | greedy | — | — | completed | 41 | — | 0 | 40 | 10 | True | 4.48e-05 | 7.2 |
| transport_cost_tradeoff | milp | — | — | completed | 5 | — | 1 | 0 | — | True | 0.0011968 | — |
| transport_cost_tradeoff | exact | — | — | completed | 5 | — | 1 | 0 | — | True | 6.1e-05 | — |
| transport_cost_tradeoff | classical_multistart | 1 | 301 | completed | 5 | — | 1 | 0 | — | True | 0.0003858 | 0 |
| transport_cost_tradeoff | classical_multistart | 2 | 302 | completed | 5 | — | 1 | 0 | — | True | 0.0003165 | 0 |
| transport_cost_tradeoff | classical_multistart | 3 | 303 | completed | 5 | — | 1 | 0 | — | True | 0.0002477 | 0 |
| transport_cost_tradeoff | classical_multistart | 4 | 304 | completed | 5 | — | 1 | 0 | — | True | 0.0002746 | 0 |
| transport_cost_tradeoff | classical_multistart | 5 | 305 | completed | 5 | — | 1 | 0 | — | True | 0.0003079 | 0 |
| transport_cost_tradeoff | classical_multistart | 6 | 306 | completed | 5 | — | 1 | 0 | — | True | 0.000307 | 0 |
| transport_cost_tradeoff | classical_multistart | 7 | 307 | completed | 5 | — | 1 | 0 | — | True | 0.0003161 | 0 |
| transport_cost_tradeoff | classical_multistart | 8 | 308 | completed | 5 | — | 1 | 0 | — | True | 0.0002668 | 0 |
| transport_cost_tradeoff | classical_multistart | 9 | 309 | completed | 5 | — | 1 | 0 | — | True | 0.0002783 | 0 |
| transport_cost_tradeoff | classical_multistart | 10 | 310 | completed | 5 | — | 1 | 0 | — | True | 0.0003308 | 0 |
| transport_cost_tradeoff | qaoa | 1 | 301 | completed | 5 | — | 1 | 0 | — | True | 0.0968321 | 0 |
| transport_cost_tradeoff | qaoa | 2 | 302 | completed | 5 | — | 1 | 0 | — | True | 0.107296 | 0 |
| transport_cost_tradeoff | qaoa | 3 | 303 | completed | 5 | — | 1 | 0 | — | True | 0.103129 | 0 |
| transport_cost_tradeoff | qaoa | 4 | 304 | completed | 5 | — | 1 | 0 | — | True | 0.100427 | 0 |
| transport_cost_tradeoff | qaoa | 5 | 305 | completed | 5 | — | 1 | 0 | — | True | 0.109301 | 0 |
| transport_cost_tradeoff | qaoa | 6 | 306 | completed | 5 | — | 1 | 0 | — | True | 0.10163 | 0 |
| transport_cost_tradeoff | qaoa | 7 | 307 | completed | 5 | — | 1 | 0 | — | True | 0.104915 | 0 |
| transport_cost_tradeoff | qaoa | 8 | 308 | completed | 5 | — | 1 | 0 | — | True | 0.101284 | 0 |
| transport_cost_tradeoff | qaoa | 9 | 309 | completed | 5 | — | 1 | 0 | — | True | 0.0959849 | 0 |
| transport_cost_tradeoff | qaoa | 10 | 310 | completed | 41 | — | 0 | 40 | 10 | True | 0.10412 | 7.2 |
| transport_cost_tradeoff | hybrid_qaoa_local_search | 1 | 301 | completed | 5 | — | 1 | 0 | — | True | 0.0969396 | 0 |
| transport_cost_tradeoff | hybrid_qaoa_local_search | 2 | 302 | completed | 5 | — | 1 | 0 | — | True | 0.107413 | 0 |
| transport_cost_tradeoff | hybrid_qaoa_local_search | 3 | 303 | completed | 5 | — | 1 | 0 | — | True | 0.103246 | 0 |
| transport_cost_tradeoff | hybrid_qaoa_local_search | 4 | 304 | completed | 5 | — | 1 | 0 | — | True | 0.100581 | 0 |
| transport_cost_tradeoff | hybrid_qaoa_local_search | 5 | 305 | completed | 5 | — | 1 | 0 | — | True | 0.109447 | 0 |
| transport_cost_tradeoff | hybrid_qaoa_local_search | 6 | 306 | completed | 5 | — | 1 | 0 | — | True | 0.101796 | 0 |
| transport_cost_tradeoff | hybrid_qaoa_local_search | 7 | 307 | completed | 5 | — | 1 | 0 | — | True | 0.105027 | 0 |
| transport_cost_tradeoff | hybrid_qaoa_local_search | 8 | 308 | completed | 5 | — | 1 | 0 | — | True | 0.10139 | 0 |
| transport_cost_tradeoff | hybrid_qaoa_local_search | 9 | 309 | completed | 5 | — | 1 | 0 | — | True | 0.0961006 | 0 |
| transport_cost_tradeoff | hybrid_qaoa_local_search | 10 | 310 | completed | 5 | — | 1 | 0 | — | True | 0.104255 | 0 |
| emergency_demand_spike | greedy | — | — | completed | 215.6 | 75.0% | 4 | 54 | 18 | True | 4.51e-05 | 0 |
| emergency_demand_spike | milp | — | — | completed | 215.6 | 75.0% | 4 | 54 | 18 | True | 0.0012604 | — |
| emergency_demand_spike | exact | — | — | completed | 215.6 | 75.0% | 4 | 54 | 18 | True | 0.0002755 | — |
| emergency_demand_spike | classical_multistart | 1 | 301 | completed | 215.6 | 75.0% | 4 | 54 | 18 | True | 0.0006461 | 0 |
| emergency_demand_spike | classical_multistart | 2 | 302 | completed | 215.6 | 75.0% | 4 | 54 | 18 | True | 0.0007831 | 0 |
| emergency_demand_spike | classical_multistart | 3 | 303 | completed | 215.6 | 75.0% | 4 | 54 | 18 | True | 0.0011408 | 0 |
| emergency_demand_spike | classical_multistart | 4 | 304 | completed | 215.6 | 75.0% | 4 | 54 | 18 | True | 0.0013028 | 0 |
| emergency_demand_spike | classical_multistart | 5 | 305 | completed | 215.6 | 75.0% | 4 | 54 | 18 | True | 0.0009163 | 0 |
| emergency_demand_spike | classical_multistart | 6 | 306 | completed | 215.6 | 75.0% | 4 | 54 | 18 | True | 0.0006601 | 0 |
| emergency_demand_spike | classical_multistart | 7 | 307 | completed | 215.6 | 75.0% | 4 | 54 | 18 | True | 0.0008227 | 0 |
| emergency_demand_spike | classical_multistart | 8 | 308 | completed | 215.6 | 75.0% | 4 | 54 | 18 | True | 0.001841 | 0 |
| emergency_demand_spike | classical_multistart | 9 | 309 | completed | 215.6 | 75.0% | 4 | 54 | 18 | True | 0.0016097 | 0 |
| emergency_demand_spike | classical_multistart | 10 | 310 | completed | 215.6 | 75.0% | 4 | 54 | 18 | True | 0.0012523 | 0 |
| emergency_demand_spike | qaoa | 1 | 301 | completed | 416.5 | 31.2% | 11 | 22.5 | 18 | True | 0.194723 | 0.931818 |
| emergency_demand_spike | qaoa | 2 | 302 | infeasible | 438.9 | 25.0% | 12 | 13.5 | 18 | False | 0.199602 | — |
| emergency_demand_spike | qaoa | 3 | 303 | completed | 301.7 | 56.2% | 7 | 40.5 | 18 | True | 0.208562 | 0.399351 |
| emergency_demand_spike | qaoa | 4 | 304 | completed | 502.6 | 12.5% | 14 | 9 | 18 | True | 0.227069 | 1.33117 |
| emergency_demand_spike | qaoa | 5 | 305 | completed | 330.4 | 50.0% | 8 | 36 | 18 | True | 0.207803 | 0.532468 |
| emergency_demand_spike | qaoa | 6 | 306 | infeasible | 525 | 6.2% | 15 | 0 | — | False | 0.209576 | — |
| emergency_demand_spike | qaoa | 7 | 307 | completed | 531.3 | 6.2% | 15 | 4.5 | 18 | True | 0.20445 | 1.46429 |
| emergency_demand_spike | qaoa | 8 | 308 | completed | 387.8 | 37.5% | 10 | 27 | 18 | True | 0.201672 | 0.798701 |
| emergency_demand_spike | qaoa | 9 | 309 | completed | 387.8 | 37.5% | 10 | 27 | 18 | True | 0.195895 | 0.798701 |
| emergency_demand_spike | qaoa | 10 | 310 | completed | 215.6 | 75.0% | 4 | 54 | 18 | True | 0.194669 | 0 |
| emergency_demand_spike | hybrid_qaoa_local_search | 1 | 301 | completed | 215.6 | 75.0% | 4 | 54 | 18 | True | 0.195142 | 0 |
| emergency_demand_spike | hybrid_qaoa_local_search | 2 | 302 | skipped_infeasible_qaoa_seed | — | — | — | — | — | False | 0.199602 | — |
| emergency_demand_spike | hybrid_qaoa_local_search | 3 | 303 | completed | 215.6 | 75.0% | 4 | 54 | 18 | True | 0.208902 | 0 |
| emergency_demand_spike | hybrid_qaoa_local_search | 4 | 304 | completed | 215.6 | 75.0% | 4 | 54 | 18 | True | 0.227731 | 0 |
| emergency_demand_spike | hybrid_qaoa_local_search | 5 | 305 | completed | 215.6 | 75.0% | 4 | 54 | 18 | True | 0.208159 | 0 |
| emergency_demand_spike | hybrid_qaoa_local_search | 6 | 306 | skipped_infeasible_qaoa_seed | — | — | — | — | — | False | 0.209576 | — |
| emergency_demand_spike | hybrid_qaoa_local_search | 7 | 307 | completed | 215.6 | 75.0% | 4 | 54 | 18 | True | 0.205157 | 0 |
| emergency_demand_spike | hybrid_qaoa_local_search | 8 | 308 | completed | 215.6 | 75.0% | 4 | 54 | 18 | True | 0.202029 | 0 |
| emergency_demand_spike | hybrid_qaoa_local_search | 9 | 309 | completed | 215.6 | 75.0% | 4 | 54 | 18 | True | 0.196289 | 0 |
| emergency_demand_spike | hybrid_qaoa_local_search | 10 | 310 | completed | 215.6 | 75.0% | 4 | 54 | 18 | True | 0.194781 | 0 |
| transport_disruption | greedy | — | — | completed | 140 | 0.0% | 4 | 0 | — | True | 3.27e-05 | 0 |
| transport_disruption | milp | — | — | completed | 140 | 0.0% | 4 | 0 | — | True | 0.0011531 | — |
| transport_disruption | exact | — | — | completed | 140 | 0.0% | 4 | 0 | — | True | 3.13e-05 | — |
| transport_disruption | classical_multistart | 1 | 301 | completed | 140 | 0.0% | 4 | 0 | — | True | 0.0001247 | 0 |
| transport_disruption | classical_multistart | 2 | 302 | completed | 140 | 0.0% | 4 | 0 | — | True | 0.0001011 | 0 |
| transport_disruption | classical_multistart | 3 | 303 | completed | 140 | 0.0% | 4 | 0 | — | True | 9.11e-05 | 0 |
| transport_disruption | classical_multistart | 4 | 304 | completed | 140 | 0.0% | 4 | 0 | — | True | 8.8e-05 | 0 |
| transport_disruption | classical_multistart | 5 | 305 | completed | 140 | 0.0% | 4 | 0 | — | True | 9.02e-05 | 0 |
| transport_disruption | classical_multistart | 6 | 306 | completed | 140 | 0.0% | 4 | 0 | — | True | 8.87e-05 | 0 |
| transport_disruption | classical_multistart | 7 | 307 | completed | 140 | 0.0% | 4 | 0 | — | True | 8.71e-05 | 0 |
| transport_disruption | classical_multistart | 8 | 308 | completed | 140 | 0.0% | 4 | 0 | — | True | 8.74e-05 | 0 |
| transport_disruption | classical_multistart | 9 | 309 | completed | 140 | 0.0% | 4 | 0 | — | True | 8.61e-05 | 0 |
| transport_disruption | classical_multistart | 10 | 310 | completed | 140 | 0.0% | 4 | 0 | — | True | 8.73e-05 | 0 |
| transport_disruption | qaoa | 1 | 301 | completed | 140 | 0.0% | 4 | 0 | — | True | 0.106885 | 0 |
| transport_disruption | qaoa | 2 | 302 | completed | 140 | 0.0% | 4 | 0 | — | True | 0.108885 | 0 |
| transport_disruption | qaoa | 3 | 303 | completed | 140 | 0.0% | 4 | 0 | — | True | 0.106632 | 0 |
| transport_disruption | qaoa | 4 | 304 | completed | 140 | 0.0% | 4 | 0 | — | True | 0.112891 | 0 |
| transport_disruption | qaoa | 5 | 305 | completed | 140 | 0.0% | 4 | 0 | — | True | 0.101931 | 0 |
| transport_disruption | qaoa | 6 | 306 | completed | 140 | 0.0% | 4 | 0 | — | True | 0.113096 | 0 |
| transport_disruption | qaoa | 7 | 307 | infeasible | 105 | 25.0% | 3 | 0 | — | False | 0.105777 | — |
| transport_disruption | qaoa | 8 | 308 | completed | 140 | 0.0% | 4 | 0 | — | True | 0.110619 | 0 |
| transport_disruption | qaoa | 9 | 309 | infeasible | 105 | 25.0% | 3 | 0 | — | False | 0.115103 | — |
| transport_disruption | qaoa | 10 | 310 | completed | 140 | 0.0% | 4 | 0 | — | True | 0.10808 | 0 |
| transport_disruption | hybrid_qaoa_local_search | 1 | 301 | completed | 140 | 0.0% | 4 | 0 | — | True | 0.106949 | 0 |
| transport_disruption | hybrid_qaoa_local_search | 2 | 302 | completed | 140 | 0.0% | 4 | 0 | — | True | 0.108947 | 0 |
| transport_disruption | hybrid_qaoa_local_search | 3 | 303 | completed | 140 | 0.0% | 4 | 0 | — | True | 0.106698 | 0 |
| transport_disruption | hybrid_qaoa_local_search | 4 | 304 | completed | 140 | 0.0% | 4 | 0 | — | True | 0.112956 | 0 |
| transport_disruption | hybrid_qaoa_local_search | 5 | 305 | completed | 140 | 0.0% | 4 | 0 | — | True | 0.101997 | 0 |
| transport_disruption | hybrid_qaoa_local_search | 6 | 306 | completed | 140 | 0.0% | 4 | 0 | — | True | 0.113166 | 0 |
| transport_disruption | hybrid_qaoa_local_search | 7 | 307 | skipped_infeasible_qaoa_seed | — | — | — | — | — | False | 0.105777 | — |
| transport_disruption | hybrid_qaoa_local_search | 8 | 308 | completed | 140 | 0.0% | 4 | 0 | — | True | 0.110679 | 0 |
| transport_disruption | hybrid_qaoa_local_search | 9 | 309 | skipped_infeasible_qaoa_seed | — | — | — | — | — | False | 0.115103 | — |
| transport_disruption | hybrid_qaoa_local_search | 10 | 310 | completed | 140 | 0.0% | 4 | 0 | — | True | 0.108144 | 0 |
| multi_facility_tradeoff | greedy | — | — | completed | 16.2 | 100.0% | 1 | 7.8 | 11.3333 | True | 7.61e-05 | 0 |
| multi_facility_tradeoff | milp | — | — | completed | 16.2 | 100.0% | 1 | 7.8 | 11.3333 | True | 0.0141327 | — |
| multi_facility_tradeoff | exact | — | — | completed | 16.2 | 100.0% | 1 | 7.8 | 11.3333 | True | 0.0009682 | — |
| multi_facility_tradeoff | classical_multistart | 1 | 301 | completed | 16.2 | 100.0% | 1 | 7.8 | 11.3333 | True | 0.0022728 | 0 |
| multi_facility_tradeoff | classical_multistart | 2 | 302 | completed | 16.2 | 100.0% | 1 | 7.8 | 11.3333 | True | 0.0014673 | 0 |
| multi_facility_tradeoff | classical_multistart | 3 | 303 | completed | 16.2 | 100.0% | 1 | 7.8 | 11.3333 | True | 0.0031247 | 0 |
| multi_facility_tradeoff | classical_multistart | 4 | 304 | completed | 16.2 | 100.0% | 1 | 7.8 | 11.3333 | True | 0.0027905 | 0 |
| multi_facility_tradeoff | classical_multistart | 5 | 305 | completed | 16.2 | 100.0% | 1 | 7.8 | 11.3333 | True | 0.0015247 | 0 |
| multi_facility_tradeoff | classical_multistart | 6 | 306 | completed | 16.2 | 100.0% | 1 | 7.8 | 11.3333 | True | 0.0028403 | 0 |
| multi_facility_tradeoff | classical_multistart | 7 | 307 | completed | 16.2 | 100.0% | 1 | 7.8 | 11.3333 | True | 0.0017452 | 0 |
| multi_facility_tradeoff | classical_multistart | 8 | 308 | completed | 16.2 | 100.0% | 1 | 7.8 | 11.3333 | True | 0.0021866 | 0 |
| multi_facility_tradeoff | classical_multistart | 9 | 309 | completed | 16.2 | 100.0% | 1 | 7.8 | 11.3333 | True | 0.0026551 | 0 |
| multi_facility_tradeoff | classical_multistart | 10 | 310 | completed | 16.2 | 100.0% | 1 | 7.8 | 11.3333 | True | 0.0019043 | 0 |
| multi_facility_tradeoff | qaoa | 1 | 301 | completed | 42.7 | 50.0% | 2 | 1.8 | 4.5 | True | 0.188702 | 1.6358 |
| multi_facility_tradeoff | qaoa | 2 | 302 | completed | 39.2 | 50.0% | 1 | 2.8 | 4.66667 | True | 0.17727 | 1.41975 |
| multi_facility_tradeoff | qaoa | 3 | 303 | completed | 50 | 50.0% | 2 | 7 | 15 | True | 0.174056 | 2.08642 |
| multi_facility_tradeoff | qaoa | 4 | 304 | completed | 50 | 50.0% | 2 | 7 | 15 | True | 0.173227 | 2.08642 |
| multi_facility_tradeoff | qaoa | 5 | 305 | completed | 42.7 | 50.0% | 2 | 1.8 | 4.5 | True | 0.176904 | 1.6358 |
| multi_facility_tradeoff | qaoa | 6 | 306 | infeasible | 25.3 | 100.0% | 0 | 18 | 18.25 | False | 0.16847 | — |
| multi_facility_tradeoff | qaoa | 7 | 307 | completed | 27 | 100.0% | 2 | 12 | 25 | True | 0.174091 | 0.666667 |
| multi_facility_tradeoff | qaoa | 8 | 308 | completed | 53.5 | 50.0% | 3 | 6 | 25 | True | 0.173954 | 2.30247 |
| multi_facility_tradeoff | qaoa | 9 | 309 | infeasible | 18.5 | 100.0% | 2 | 6 | 25 | False | 0.169217 | — |
| multi_facility_tradeoff | qaoa | 10 | 310 | completed | 28.8 | 100.0% | 1 | 17 | 22.6667 | True | 0.172379 | 0.777778 |
| multi_facility_tradeoff | hybrid_qaoa_local_search | 1 | 301 | completed | 16.2 | 100.0% | 1 | 7.8 | 11.3333 | True | 0.189273 | 0 |
| multi_facility_tradeoff | hybrid_qaoa_local_search | 2 | 302 | completed | 39.2 | 50.0% | 1 | 2.8 | 4.66667 | True | 0.177527 | 1.41975 |
| multi_facility_tradeoff | hybrid_qaoa_local_search | 3 | 303 | completed | 16.2 | 100.0% | 1 | 7.8 | 11.3333 | True | 0.174629 | 0 |
| multi_facility_tradeoff | hybrid_qaoa_local_search | 4 | 304 | completed | 16.2 | 100.0% | 1 | 7.8 | 11.3333 | True | 0.173956 | 0 |
| multi_facility_tradeoff | hybrid_qaoa_local_search | 5 | 305 | completed | 16.2 | 100.0% | 1 | 7.8 | 11.3333 | True | 0.177429 | 0 |
| multi_facility_tradeoff | hybrid_qaoa_local_search | 6 | 306 | skipped_infeasible_qaoa_seed | — | — | — | — | — | False | 0.16847 | — |
| multi_facility_tradeoff | hybrid_qaoa_local_search | 7 | 307 | completed | 16.2 | 100.0% | 1 | 7.8 | 11.3333 | True | 0.174808 | 0 |
| multi_facility_tradeoff | hybrid_qaoa_local_search | 8 | 308 | completed | 16.2 | 100.0% | 1 | 7.8 | 11.3333 | True | 0.174708 | 0 |
| multi_facility_tradeoff | hybrid_qaoa_local_search | 9 | 309 | skipped_infeasible_qaoa_seed | — | — | — | — | — | False | 0.169217 | — |
| multi_facility_tradeoff | hybrid_qaoa_local_search | 10 | 310 | completed | 16.2 | 100.0% | 1 | 7.8 | 11.3333 | True | 0.173214 | 0 |

## QAOA repeated-run summary by scenario

Objective statistics below use feasible measured candidates only. Feasibility rate uses all attempted seeds, including errors.

| Scenario | Attempts | Measured | Feasible | Feasibility rate | Mean feasible objective | Median | Population SD | Mean runtime (s) |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| normal_reference | 10 | 10 | 9 | 0.9 | 69.8444 | 82.6 | 38.5315 | 0.131008 |
| inventory_shortage | 10 | 10 | 10 | 1 | 158.34 | 152.6 | 11.48 | 0.113199 |
| transport_cost_tradeoff | 10 | 10 | 10 | 1 | 8.6 | 5 | 10.8 | 0.102492 |
| emergency_demand_spike | 10 | 10 | 8 | 0.8 | 384.212 | 387.8 | 96.7295 | 0.204402 |
| transport_disruption | 10 | 10 | 8 | 0.8 | 140 | 140 | 0 | 0.10899 |
| multi_facility_tradeoff | 10 | 10 | 8 | 0.8 | 41.7375 | 42.7 | 9.13618 | 0.174827 |

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
| Runtime (seconds) | 6 | 5.34667e-05 | 4.495e-05 | 3.27e-05 | 8.06e-05 | 1.8111e-05 |
| Search-stage runtime (seconds) | 0 | — | — | — | — | — |
| QAOA-stage runtime (seconds) | 0 | — | — | — | — | — |
| Time to first feasible (seconds) | 0 | — | — | — | — | — |
| Time to target (seconds) | 0 | — | — | — | — | — |
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
| Runtime (seconds) | 6 | 0.00364048 | 0.0012427 | 0.0011531 | 0.0141327 | 0.00473164 |
| Search-stage runtime (seconds) | 0 | — | — | — | — | — |
| QAOA-stage runtime (seconds) | 0 | — | — | — | — | — |
| Time to first feasible (seconds) | 0 | — | — | — | — | — |
| Time to target (seconds) | 0 | — | — | — | — | — |
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
| Runtime (seconds) | 6 | 0.000256283 | 0.00010085 | 3.13e-05 | 0.0009682 | 0.000327982 |
| Search-stage runtime (seconds) | 0 | — | — | — | — | — |
| QAOA-stage runtime (seconds) | 0 | — | — | — | — | — |
| Time to first feasible (seconds) | 0 | — | — | — | — | — |
| Time to target (seconds) | 0 | — | — | — | — | — |
| Approximation gap vs Exact | 0 | — | — | — | — | — |

### Classical_Multistart

Attempts: `60`; completed: `60`; feasible: `60`; infeasible: `0`; feasible/attempted: `1.0`; statuses: `{'completed': 60}`.

| Metric | n | Mean | Median | Min | Max | Std. dev. (population) |
|---|---:|---:|---:|---:|---:|---:|
| Objective | 60 | 92.4333 | 82.6 | 5 | 215.6 | 80.6526 |
| Critical satisfaction rate | 50 | 0.616667 | 0.75 | 0 | 1 | 0.392994 |
| Total unmet demand | 60 | 2.33333 | 2.5 | 0 | 4 | 1.69967 |
| Transport cost | 60 | 14.8 | 8.4 | 0 | 54 | 18.5634 |
| Average travel time | 40 | 16.3333 | 18 | 11.3333 | 18 | 2.88675 |
| Runtime (seconds) | 60 | 0.000746888 | 0.00035885 | 8.61e-05 | 0.0031247 | 0.000792717 |
| Search-stage runtime (seconds) | 60 | 0.000723018 | 0.0003382 | 7.26e-05 | 0.003082 | 0.000783946 |
| QAOA-stage runtime (seconds) | 0 | — | — | — | — | — |
| Time to first feasible (seconds) | 60 | 2.73333e-05 | 2.33e-05 | 1.35e-05 | 7.54e-05 | 1.26575e-05 |
| Time to target (seconds) | 60 | 4.77417e-05 | 2.41e-05 | 1.38e-05 | 0.0001942 | 4.61057e-05 |
| Approximation gap vs Exact | 60 | 0 | 0 | 0 | 0 | 0 |

### Qaoa

Attempts: `60`; completed: `60`; feasible: `53`; infeasible: `7`; feasible/attempted: `0.8833333333333333`; statuses: `{'completed': 53, 'infeasible': 7}`.

| Metric | n | Mean | Median | Min | Max | Std. dev. (population) |
|---|---:|---:|---:|---:|---:|---:|
| Objective | 53 | 128.785 | 140 | 5 | 531.3 | 127.337 |
| Critical satisfaction rate | 50 | 0.4025 | 0.333333 | 0 | 1 | 0.31624 |
| Total unmet demand | 60 | 3.78333 | 3 | 0 | 15 | 3.62442 |
| Transport cost | 60 | 9.04 | 6.5 | 0 | 54 | 11.4928 |
| Average travel time | 39 | 17.2714 | 18 | 4.5 | 25 | 4.45033 |
| Runtime (seconds) | 60 | 0.139153 | 0.121298 | 0.0959849 | 0.227069 | 0.0380623 |
| Search-stage runtime (seconds) | 0 | — | — | — | — | — |
| QAOA-stage runtime (seconds) | 60 | 0.139171 | 0.121315 | 0.0959952 | 0.227089 | 0.0380661 |
| Time to first feasible (seconds) | 53 | 0.136814 | 0.116786 | 0.0959952 | 0.227089 | 0.0374959 |
| Time to target (seconds) | 29 | 0.113125 | 0.108895 | 0.0959952 | 0.194685 | 0.0178919 |
| Approximation gap vs Exact | 53 | 0.799777 | 0 | 0 | 7.2 | 1.34744 |

### Hybrid_Qaoa_Local_Search

Attempts: `60`; completed: `53`; feasible: `53`; infeasible: `7`; feasible/attempted: `0.8833333333333333`; statuses: `{'completed': 53, 'skipped_infeasible_qaoa_seed': 7}`.

| Metric | n | Mean | Median | Min | Max | Std. dev. (population) |
|---|---:|---:|---:|---:|---:|---:|
| Objective | 53 | 90.5698 | 39.2 | 5 | 215.6 | 79.636 |
| Critical satisfaction rate | 43 | 0.600775 | 0.75 | 0 | 1 | 0.384014 |
| Total unmet demand | 53 | 2.30189 | 1 | 0 | 4 | 1.7 |
| Transport cost | 53 | 13.9887 | 9 | 0 | 54 | 17.9709 |
| Average travel time | 35 | 16.2857 | 18 | 4.66667 | 18 | 3.32107 |
| Runtime (seconds) | 60 | 0.139374 | 0.121547 | 0.0961006 | 0.227731 | 0.0381923 |
| Search-stage runtime (seconds) | 60 | 0.000140125 | 4.2e-05 | 0 | 0.000723 | 0.000195555 |
| QAOA-stage runtime (seconds) | 60 | 0.139171 | 0.121315 | 0.0959952 | 0.227089 | 0.0380661 |
| Time to first feasible (seconds) | 53 | 0.136814 | 0.116786 | 0.0959952 | 0.227089 | 0.0374959 |
| Time to target (seconds) | 52 | 0.13613 | 0.116331 | 0.0959952 | 0.227628 | 0.0375436 |
| Approximation gap vs Exact | 53 | 0.0267878 | 0 | 0 | 1.41975 | 0.19317 |

## Paired objective comparisons

For each shared seed and scenario, the difference is baseline objective minus the compared method objective, so positive values favor the compared method. Intervals are descriptive percentile bootstrap intervals over seed pairs (5,000 resamples); they do not account for variation across scenario designs and are not a formal significance test. Infeasible candidates are excluded from objective differences but remain in the feasibility counts above.

| Scenario | Compared method vs baseline | Feasible paired seeds | Mean objective improvement | 95% bootstrap interval |
|---|---|---:|---:|---:|
| emergency_demand_spike | qaoa vs classical_multistart | 8 | -168.612 | [-233.188, -104.037] |
| emergency_demand_spike | hybrid_qaoa_local_search vs classical_multistart | 8 | 0 | [0, 0] |
| inventory_shortage | qaoa vs classical_multistart | 10 | -5.74 | [-14.35, 0] |
| inventory_shortage | hybrid_qaoa_local_search vs classical_multistart | 10 | 0 | [0, 0] |
| multi_facility_tradeoff | qaoa vs classical_multistart | 8 | -25.5375 | [-31.5, -18.9625] |
| multi_facility_tradeoff | hybrid_qaoa_local_search vs classical_multistart | 8 | -2.875 | [-8.625, 0] |
| normal_reference | qaoa vs classical_multistart | 9 | -44.6444 | [-70.1556, -22.3222] |
| normal_reference | hybrid_qaoa_local_search vs classical_multistart | 9 | 0 | [0, 0] |
| transport_cost_tradeoff | qaoa vs classical_multistart | 10 | -3.6 | [-10.8, 0] |
| transport_cost_tradeoff | hybrid_qaoa_local_search vs classical_multistart | 10 | 0 | [0, 0] |
| transport_disruption | qaoa vs classical_multistart | 8 | 0 | [0, 0] |
| transport_disruption | hybrid_qaoa_local_search vs classical_multistart | 8 | 0 | [0, 0] |

**Preregistered hybrid screen:** Not met on any tested scenario. The screen requires at least 5% paired mean objective improvement, a bootstrap interval entirely above zero, and no lower feasibility rate than classical multistart.

## Judge-ready answer

We investigate a synthetic integer allocation problem: choose shipments from available bank-to-hospital routes to minimize weighted critical and total unmet demand plus modeled per-unit transport cost and time. The QUBO encodes bounded shipment, unmet-demand, and inventory-slack integers as binary variables, adds squared equality penalties, converts the matrix to an Ising cost operator, then uses a classical parameter optimizer and finite-shot Qiskit Aer sampling. Every measured candidate is decoded, rescored under the original objective, and independently validated.

Baselines are Greedy, SciPy/HiGHS MILP, bounded Exact enumeration, and a stronger seeded classical multistart local search. The comparison ran six fixed synthetic scenarios with 10 paired seeds, QAOA `p=1`, 128 shots, COBYLA/15 iterations, and a 100-objective-evaluation cap on each local search. The hybrid refines only a feasible raw QAOA sample; it never repairs an infeasible sample. Exact and MILP agreed on all six scenarios.

In this confirmatory run, classical multistart matched the Exact reference in 60/60 trials. Raw QAOA produced 53/60 feasible candidates; hybrid refinement produced 53/60 feasible outputs and matched Exact in 52 trials. Mean local end-to-end time was 0.000746888s for classical multistart and 0.139153s for QAOA. These are local-machine observations with different computational work units, not a speedup estimate.

**Conclusion:** QAOA and its hybrid initialization showed no measurable advantage under these tested conditions; the preregistered hybrid screen was not met. The useful result is negative evidence for this small, already classically tractable suite: the local simulator added overhead, raw samples were sometimes infeasible or worse, and classical search already reached the verified optimum. This does not rule out other encodings, QAOA settings, hardware, or larger instance classes; those remain untested.

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
