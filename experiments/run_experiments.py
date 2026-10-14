"""Run bounded synthetic allocation suites across classical and QAOA methods.

Example (from the project root)::

    .venv/bin/python -m experiments.run_experiments --suite round2 --scenarios 6 \
        --repetitions 5 --shots 128

Every output file contains real solver responses. Failed or unavailable
methods are stored with an error status and null metrics, never imputed.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import platform
import sys
from dataclasses import asdict
from datetime import datetime, timezone
from importlib.metadata import PackageNotFoundError, version
from pathlib import Path
from time import perf_counter
from typing import Any

from backend.data_loader import load_data
from backend.scenario_factory import scenario_from_loaded_data
from optimization.constraints import validate_allocation
from optimization.decoder import evaluate_quantum_solution
from optimization.exact import ExactSolver, ExactSolverConfig, ExactSolverLimitError
from optimization.greedy import GreedyAllocator
from optimization.milp import MILPSolver, MILPSolverError
from optimization.models import BloodBank, Hospital, Route, Scenario, Urgency
from optimization.objective import ObjectiveConfig, calculate_objective
from quantum.qubo import QUBOPenaltyConfig, build_qubo
from experiments.search_methods import classical_multistart, local_improve, state_from_allocation
try:
    from quantum.qaoa_solver import QAOAConfig, QAOASolver
    _QAOA_IMPORT_ERROR: Exception | None = None
except Exception as error:  # Classical runs and raw QAOA error recording remain usable.
    QAOAConfig = None  # type: ignore[assignment,misc]
    QAOASolver = None  # type: ignore[assignment,misc]
    _QAOA_IMPORT_ERROR = error

ROOT = Path(__file__).resolve().parents[1]


def build_scenarios(count: int = 5) -> tuple[Scenario, ...]:
    """Create repeatable tiny scenarios using only bundled fictional records.

    Scenario dimensions are intentionally fixed at one bank, one hospital,
    one group. Quantities and route features vary in a small hand-authored
    matrix, keeping Exact and the 16-qubit local simulator within scope.
    """
    if not 1 <= count <= 5:
        raise ValueError("scenario count must be from 1 to 5")
    bundled = scenario_from_loaded_data(load_data(), "experiment_source")
    base_bank = next(bank for bank in bundled.blood_banks if bank.id == "bank_a")
    base_hospital = next(h for h in bundled.hospitals if h.id == "hospital_1")
    base_route = next(r for r in bundled.routes if r.source == base_bank.id and r.destination == base_hospital.id)
    group = "O"
    specifications = (
        ("normal_reference", 12, 4, "high", "available", 18.0, 4.5),
        ("inventory_shortage", 2, 6, "critical", "available", 18.0, 4.5),
        ("demand_below_inventory", 8, 3, "medium", "available", 18.0, 4.5),
        ("transport_disruption", 5, 4, "high", "blocked", 18.0, 4.5),
        ("critical_shortage", 4, 7, "critical", "available", 31.0, 7.0),
    )
    scenarios: list[Scenario] = []
    for name, inventory, demand, urgency, status, travel, cost in specifications[:count]:
        bank = BloodBank(base_bank.id, base_bank.name, base_bank.location_id, {group: inventory})
        hospital = Hospital(
            base_hospital.id, base_hospital.name, base_hospital.location_id,
            {group: demand}, {group: Urgency(urgency, base_hospital.urgency[group].priority_weight)},
        )
        route = Route(base_route.source, base_route.destination, travel, base_route.distance_km,
                      cost, status)
        scenarios.append(Scenario(
            id=name, blood_groups=(group,), blood_banks=(bank,), hospitals=(hospital,),
            routes=(route,), compatibility={(group, group): bundled.compatibility[(group, group)]},
            synthetic=True,
        ))
    return tuple(scenarios)


def build_round2_scenarios(count: int = 6) -> tuple[Scenario, ...]:
    """Build a small evidence suite, including one 2-bank/2-hospital case.

    The first five cases isolate ordinary demand, shortage, a real transport
    versus unmet-demand trade-off, a demand spike, and a blocked route. The
    final case has competing hospitals drawing from two banks over four routes.
    All quantities and transport values are explicitly synthetic.
    """
    if not 1 <= count <= 6:
        raise ValueError("Round 2 scenario count must be from 1 to 6")
    bundled = scenario_from_loaded_data(load_data(), "round2_experiment_source")
    base_bank = next(bank for bank in bundled.blood_banks if bank.id == "bank_a")
    base_hospital = next(h for h in bundled.hospitals if h.id == "hospital_1")
    group = "O"

    def single(name: str, inventory: int, demand: int, urgency: str,
               travel: float, cost: float, route_status: str = "available") -> Scenario:
        bank = BloodBank(base_bank.id, base_bank.name, base_bank.location_id, {group: inventory})
        hospital = Hospital(
            base_hospital.id, base_hospital.name, base_hospital.location_id,
            {group: demand},
            {group: Urgency(urgency, base_hospital.urgency[group].priority_weight)},
        )
        route = Route(bank.id, hospital.id, travel, 0.0, cost, route_status)
        return Scenario(
            id=name, blood_groups=(group,), blood_banks=(bank,), hospitals=(hospital,),
            routes=(route,), compatibility={(group, group): bundled.compatibility[(group, group)]},
            synthetic=True,
        )

    cases = [
        single("normal_reference", 12, 4, "high", 18.0, 4.5),
        single("inventory_shortage", 2, 6, "critical", 18.0, 4.5),
        # Under default weights, the modeled route burden exceeds medium
        # unmet-demand cost. This is intentional evidence of the trade-off.
        single("transport_cost_tradeoff", 1, 1, "medium", 10.0, 40.0),
        single("emergency_demand_spike", 12, 16, "critical", 18.0, 4.5),
        single("transport_disruption", 5, 4, "high", 18.0, 4.5, "blocked"),
    ]

    banks = (
        BloodBank("bank_a", base_bank.name, base_bank.location_id, {group: 2}),
        BloodBank("bank_b", "Synthetic Bank B", "location_b", {group: 1}),
    )
    hospitals = (
        Hospital("hospital_1", base_hospital.name, base_hospital.location_id,
                 {group: 2}, {group: Urgency("medium", 1.0)}),
        Hospital("hospital_2", "Synthetic Hospital 2", "location_c",
                 {group: 2}, {group: Urgency("critical", 3.0)}),
    )
    routes = (
        Route("bank_a", "hospital_1", 5.0, 2.0, 1.0, "available"),
        Route("bank_a", "hospital_2", 25.0, 12.0, 6.0, "available"),
        Route("bank_b", "hospital_1", 18.0, 9.0, 5.0, "available"),
        Route("bank_b", "hospital_2", 4.0, 1.5, 0.8, "available"),
    )
    cases.append(Scenario(
        id="multi_facility_tradeoff", blood_groups=(group,), blood_banks=banks,
        hospitals=hospitals, routes=routes,
        compatibility={(group, group): bundled.compatibility[(group, group)]}, synthetic=True,
    ))
    return tuple(cases[:count])


def _scenario_size(scenario: Scenario) -> dict[str, int]:
    return {
        "blood_banks": len(scenario.blood_banks), "hospitals": len(scenario.hospitals),
        "blood_groups": len(scenario.blood_groups),
        "allocation_decision_variables": len(scenario.allocation_variables()),
        "routes": len(scenario.routes),
        "inventory_units": sum(sum(bank.inventory.values()) for bank in scenario.blood_banks),
        "demand_units": sum(sum(h.demand.values()) for h in scenario.hospitals),
    }


def _critical_satisfaction(scenario: Scenario, result) -> float | None:
    total = sum(h.demand[g] for h in scenario.hospitals for g in h.demand
                if h.urgency[g].category in {"high", "critical"})
    if total == 0:
        return None
    critical_unmet = result.objective_breakdown.critical_unmet_units
    return max(0, total - critical_unmet) / total


def _record(scenario: Scenario, method: str, result: Any, validation: dict[str, Any], runtime: float,
            objective_basis: str = "classical objective on validated allocation") -> dict[str, Any]:
    objective = result.objective_breakdown
    shipped = sum(row.quantity for row in result.allocation)
    return {
        "scenario_id": scenario.id, "method": method,
        "status": "completed" if validation["feasible"] else "infeasible",
        "objective": objective.total_objective,
        "critical_satisfaction": _critical_satisfaction(scenario, result),
        "critical_unmet_demand": objective.critical_unmet_units,
        "total_unmet_demand": objective.total_unmet_units,
        "transport_cost": objective.transportation_cost,
        "average_travel_time": objective.transportation_time / shipped if shipped else None,
        "feasibility": bool(validation["feasible"]),
        "runtime_seconds": runtime,
        "objective_basis": objective_basis,
        "validation": validation,
        "allocation": [asdict(row) for row in result.allocation],
        "unmet_demand": [
            {"hospital_id": hospital, "blood_group": group, "units": amount}
            for (hospital, group), amount in sorted(result.unmet_demand.items())
        ],
    }


def run_experiments(*, count: int, seed: int, p: int, shots: int, optimizer: str,
                    max_iterations: int, penalty_weight: float, max_exact_states: int,
                    suite: str = "baseline", repetitions: int = 5,
                    critical_weight: float = 10.0, unmet_weight: float = 5.0,
                    transport_cost_weight: float = 1.0, transport_time_weight: float = 0.1,
                    secondary_penalty_weight: float = 0.0) -> dict[str, Any]:
    if suite not in {"baseline", "round2"}:
        raise ValueError("suite must be 'baseline' or 'round2'")
    if isinstance(repetitions, bool) or not isinstance(repetitions, int) or not 1 <= repetitions <= 20:
        raise ValueError("repetitions must be an integer from 1 to 20")
    scenarios = (build_scenarios(count) if suite == "baseline"
                 else build_round2_scenarios(count))
    objective = ObjectiveConfig(critical_weight, unmet_weight, transport_cost_weight,
                                transport_time_weight, secondary_penalty_weight)
    penalties = QUBOPenaltyConfig(penalty_weight, penalty_weight)
    qaoa_settings = {"p": p, "shots": shots, "optimizer": optimizer,
                     "max_iterations": max_iterations, "base_seed": seed,
                     "seed_sequence": [seed + index for index in range(repetitions)],
                     "repetitions": repetitions, "max_qubits": 16}
    records: list[dict[str, Any]] = []
    sizes = {scenario.id: _scenario_size(scenario) for scenario in scenarios}

    for scenario in scenarios:
        scenario_records: dict[str, dict[str, Any]] = {}
        # Classical baselines are timed separately. Their returned candidate
        # is checked again by the shared independent validator.
        for name, solver in (("greedy", GreedyAllocator()),
                             ("milp", MILPSolver()),
                             ("exact", ExactSolver(ExactSolverConfig(max_exact_states)))):
            started = perf_counter()
            try:
                result = solver.solve(scenario, objective)
                validation = validate_allocation(scenario, result.allocation, result.unmet_demand)
                item = _record(scenario, name, result, validation, perf_counter() - started)
            except ExactSolverLimitError as error:
                item = {"scenario_id": scenario.id, "method": name, "status": "skipped_too_large",
                        "objective": None, "critical_satisfaction": None,
                        "critical_unmet_demand": None, "total_unmet_demand": None,
                        "transport_cost": None, "average_travel_time": None, "feasibility": None,
                        "runtime_seconds": perf_counter() - started, "detail": str(error),
                        "validation": None, "allocation": [], "unmet_demand": []}
            except MILPSolverError as error:
                item = {"scenario_id": scenario.id, "method": name, "status": "error",
                        "objective": None, "critical_satisfaction": None,
                        "critical_unmet_demand": None, "total_unmet_demand": None,
                        "transport_cost": None, "average_travel_time": None, "feasibility": None,
                        "runtime_seconds": perf_counter() - started, "detail": str(error),
                        "validation": None, "allocation": [], "unmet_demand": []}
            except Exception as error:
                item = {"scenario_id": scenario.id, "method": name, "status": "error",
                        "objective": None, "critical_satisfaction": None,
                        "critical_unmet_demand": None, "total_unmet_demand": None,
                        "transport_cost": None, "average_travel_time": None, "feasibility": None,
                        "runtime_seconds": perf_counter() - started,
                        "detail": f"{type(error).__name__}: {error}",
                        "validation": None, "allocation": [], "unmet_demand": []}
            item["repetition"] = None
            item["seed"] = None
            scenario_records[name] = item

        exact = scenario_records["exact"]
        milp = scenario_records["milp"]
        target_objective = None
        if exact.get("status") == "completed" and milp.get("status") == "completed":
            if math.isclose(float(exact["objective"]), float(milp["objective"]), rel_tol=1e-9, abs_tol=1e-9):
                target_objective = float(exact["objective"])
        elif exact.get("status") == "completed":
            target_objective = float(exact["objective"])
        elif milp.get("status") == "completed":
            target_objective = float(milp["objective"])

        classical_search_items: list[dict[str, Any]] = []
        for repetition_index in range(repetitions):
            run_seed = seed + repetition_index
            started = perf_counter()
            try:
                greedy_started = perf_counter()
                greedy_start = GreedyAllocator().solve(scenario, objective)
                greedy_initialization_seconds = perf_counter() - greedy_started
                improved, search_metrics = classical_multistart(
                    scenario, objective, greedy_start.allocation, seed=run_seed,
                    max_evaluations=100, random_starts=3,
                    target_objective=target_objective,
                    initialization_seconds=perf_counter() - started)
                validation = validate_allocation(scenario, improved.allocation,
                                                 improved.unmet_demand)
                scored = type("ScoredSearchState", (), {
                    "allocation": improved.allocation,
                    "unmet_demand": improved.unmet_demand,
                    "objective_breakdown": calculate_objective(
                        scenario, improved.allocation, objective),
                })()
                row = _record(scenario, "classical_multistart", scored, validation,
                              perf_counter() - started) | search_metrics | {
                    "repetition": repetition_index + 1, "seed": run_seed,
                    "first_feasible_seconds": greedy_initialization_seconds,
                    "reference_objective": target_objective,
                    "target_objective": (target_objective * 1.05
                                         if target_objective is not None else None),
                }
            except Exception as error:
                row = {"scenario_id": scenario.id, "method": "classical_multistart",
                       "status": "error", "detail": f"{type(error).__name__}: {error}",
                       "objective": None, "feasibility": None,
                       "runtime_seconds": perf_counter() - started,
                       "repetition": repetition_index + 1, "seed": run_seed,
                       "objective_evaluations": 0, "evaluation_budget": 100}
            classical_search_items.append(row)

        qaoa_items: list[dict[str, Any]] = []
        hybrid_items: list[dict[str, Any]] = []
        for repetition_index in range(repetitions):
            run_seed = seed + repetition_index
            started = perf_counter()
            sample = None
            evaluated = None
            validation = None
            qubo = None
            try:
                if _QAOA_IMPORT_ERROR is not None or QAOAConfig is None or QAOASolver is None:
                    raise RuntimeError(f"QAOA dependency import failed: {_QAOA_IMPORT_ERROR}")
                qubo = build_qubo(scenario, objective, penalties)
                settings = {"p": p, "shots": shots, "optimizer": optimizer,
                            "max_iterations": max_iterations, "seed": run_seed,
                            "max_qubits": 16}
                sample = QAOASolver(QAOAConfig(**settings)).solve(qubo)
                evaluated = evaluate_quantum_solution(qubo, sample.best_bitstring)
                validation = validate_allocation(scenario, evaluated.decoded_allocation,
                                                 evaluated.unmet_demand)
                item = _record(scenario, "qaoa", evaluated, validation,
                               perf_counter() - started, evaluated.objective_basis) | {
                    "qubo_variable_count": qubo.variable_count,
                    "best_measured_bitstring": sample.best_bitstring,
                    "counts": dict(sample.counts), "measured_energy": sample.objective_value,
                    "qaoa_depth": sample.qaoa_depth, "shots": sample.number_of_shots,
                    "optimizer_information": dict(sample.optimizer_information),
                    "validator_violations": list(evaluated.violations),
                    "repetition": repetition_index + 1, "seed": run_seed,
                }
                qaoa_pipeline_runtime = perf_counter() - started
                item["qaoa_runtime_seconds"] = qaoa_pipeline_runtime
                item["first_feasible_seconds"] = (qaoa_pipeline_runtime
                                                    if validation["feasible"] else None)
                item["time_to_target_seconds"] = (
                    qaoa_pipeline_runtime
                    if validation["feasible"] and target_objective is not None
                    and evaluated.objective_breakdown.total_objective <= target_objective * 1.05
                    else None)
            except Exception as error:
                qaoa_pipeline_runtime = perf_counter() - started
                item = {
                    "scenario_id": scenario.id, "method": "qaoa", "status": "error",
                    "detail": f"{type(error).__name__}: {error}", "objective": None,
                    "critical_satisfaction": None, "critical_unmet_demand": None,
                    "total_unmet_demand": None, "transport_cost": None,
                    "average_travel_time": None, "feasibility": None,
                    "runtime_seconds": perf_counter() - started, "validation": None,
                    "allocation": [], "unmet_demand": [],
                    "repetition": repetition_index + 1, "seed": run_seed,
                }
            qaoa_items.append(item)

            hybrid_started = started
            if sample is None or evaluated is None or validation is None:
                hybrid_items.append({
                    "scenario_id": scenario.id, "method": "hybrid_qaoa_local_search",
                    "status": "error", "detail": item.get("detail", "QAOA candidate unavailable"),
                    "objective": None, "feasibility": None,
                    "runtime_seconds": item["runtime_seconds"], "qaoa_runtime_seconds": item["runtime_seconds"],
                    "search_runtime_seconds": 0.0, "first_feasible_seconds": None,
                    "time_to_target_seconds": None, "seed": run_seed,
                    "repetition": repetition_index + 1,
                })
            elif not validation["feasible"]:
                hybrid_items.append({
                    "scenario_id": scenario.id, "method": "hybrid_qaoa_local_search",
                    "status": "skipped_infeasible_qaoa_seed",
                    "objective": None, "feasibility": False,
                    "runtime_seconds": item["runtime_seconds"],
                    "qaoa_runtime_seconds": qaoa_pipeline_runtime,
                    "search_runtime_seconds": 0.0, "first_feasible_seconds": None,
                    "time_to_target_seconds": None,
                    "raw_qaoa_candidate_objective": evaluated.objective_breakdown.total_objective,
                    "raw_qaoa_allocation": [asdict(row) for row in evaluated.decoded_allocation],
                    "validator_violations": list(evaluated.violations),
                    "objective_evaluations": 0, "evaluation_budget": 100,
                    "seed": run_seed, "repetition": repetition_index + 1,
                })
            else:
                try:
                    initial_state = state_from_allocation(
                        scenario, objective, evaluated.decoded_allocation)
                    improved, search_metrics = local_improve(
                        scenario, objective, initial_state, max_evaluations=100,
                        target_objective=target_objective)
                    hybrid_validation = validate_allocation(scenario, improved.allocation,
                                                            improved.unmet_demand)
                    scored = type("ScoredHybridState", (), {
                        "allocation": improved.allocation,
                        "unmet_demand": improved.unmet_demand,
                        "objective_breakdown": calculate_objective(
                            scenario, improved.allocation, objective),
                    })()
                    row = _record(scenario, "hybrid_qaoa_local_search", scored,
                                  hybrid_validation, perf_counter() - hybrid_started) | {
                        "qaoa_runtime_seconds": qaoa_pipeline_runtime,
                        "search_runtime_seconds": search_metrics["search_runtime_seconds"],
                        "first_feasible_seconds": qaoa_pipeline_runtime,
                        "time_to_target_seconds": (
                            qaoa_pipeline_runtime + search_metrics["time_to_target_seconds"]
                            if search_metrics["time_to_target_seconds"] is not None else None),
                        "raw_qaoa_candidate_objective": evaluated.objective_breakdown.total_objective,
                        "raw_qaoa_allocation": [asdict(row) for row in evaluated.decoded_allocation],
                        "raw_qaoa_feasible": True,
                        "objective_evaluations": search_metrics["objective_evaluations"],
                        "evaluation_budget": search_metrics["evaluation_budget"],
                        "reference_objective": target_objective,
                        "target_objective": (target_objective * 1.05
                                             if target_objective is not None else None),
                        "seed": run_seed, "repetition": repetition_index + 1,
                    }
                    hybrid_items.append(row)
                except Exception as error:
                    hybrid_items.append({
                        "scenario_id": scenario.id, "method": "hybrid_qaoa_local_search",
                        "status": "error", "detail": f"{type(error).__name__}: {error}",
                        "objective": None, "feasibility": None,
                        "runtime_seconds": perf_counter() - hybrid_started,
                        "qaoa_runtime_seconds": qaoa_pipeline_runtime,
                        "search_runtime_seconds": 0.0, "seed": run_seed,
                        "repetition": repetition_index + 1,
                    })

        # Require the two optimum-capable classical references to agree before
        # assigning a QAOA approximation gap.
        reference = None
        if exact.get("status") == "completed" and milp.get("status") == "completed":
            if math.isclose(float(exact["objective"]), float(milp["objective"]), rel_tol=1e-9, abs_tol=1e-9):
                reference = {"method": "exact_and_milp", "objective": exact["objective"]}
        elif exact.get("status") == "completed":
            reference = {"method": "exact", "objective": exact["objective"]}
        elif milp.get("status") == "completed":
            reference = {"method": "milp", "objective": milp["objective"]}

        for item in (scenario_records["greedy"], *qaoa_items):
            item["approximation_reference"] = reference["method"] if reference else None
            if reference is None:
                item["approximation_gap"] = None
                mismatch = exact.get("status") == "completed" and milp.get("status") == "completed"
                item["approximation_gap_status"] = (
                    "unavailable: Exact and MILP objective disagreement" if mismatch
                    else "unavailable: no completed feasible optimum reference")
            elif item.get("status") == "completed" and item.get("feasibility") is True:
                reference_value = float(reference["objective"])
                method_value = float(item["objective"])
                if reference_value == 0:
                    item["approximation_gap"] = 0.0 if method_value == 0 else None
                    item["approximation_gap_status"] = (
                        "defined: both objectives are zero" if method_value == 0
                        else "undefined: reference objective is zero")
                else:
                    item["approximation_gap"] = (method_value - reference_value) / abs(reference_value)
                    item["approximation_gap_status"] = "defined"
            else:
                item["approximation_gap"] = None
                item["approximation_gap_status"] = "unavailable: feasible method result is required"
        for row in (*classical_search_items, *hybrid_items):
            row["approximation_reference"] = reference["method"] if reference else None
            if reference and row.get("status") == "completed" and row.get("feasibility") is True:
                ref = float(reference["objective"])
                value = float(row["objective"])
                row["approximation_gap"] = (0.0 if ref == 0 and value == 0 else
                                             (value - ref) / abs(ref) if ref != 0 else None)
            else:
                row["approximation_gap"] = None
        records.extend(scenario_records[method] for method in ("greedy", "milp", "exact"))
        records.extend(classical_search_items)
        records.extend(qaoa_items)
        records.extend(hybrid_items)

    tracked_inputs = (ROOT / "data" / "blood_banks.json", ROOT / "data" / "hospitals.json",
                      ROOT / "data" / "routes.json", ROOT / "data" / "compatibility.json")
    tracked_inputs += tuple(ROOT / path for path in (
        "backend/scenario_factory.py",
        "experiments/analyze_results.py",
        "experiments/search_methods.py",
        "docs/QUANTUM_VALUE_PROTOCOL.md",
        "optimization/models.py", "optimization/objective.py", "optimization/constraints.py",
        "optimization/greedy.py", "optimization/milp.py", "optimization/exact.py",
        "optimization/decoder.py", "quantum/qubo.py", "quantum/ising.py", "quantum/qaoa_solver.py",
    ))
    tracked_inputs += (Path(__file__).resolve(),)
    source_hashes = {
        str(path.relative_to(ROOT)): hashlib.sha256(path.read_bytes()).hexdigest()
        for path in tracked_inputs
    }
    config = {
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "invocation": {"module": "experiments.run_experiments", "arguments": sys.argv[1:]},
        "source_files_sha256": source_hashes,
        "suite": suite,
        "scenario_source": ("five-case historical baseline" if suite == "baseline"
                            else "six-case Round 2 suite with a synthetic 2-bank/2-hospital case"),
        "scenario_sizes": sizes,
        "scenarios": {
            scenario.id: {
                "synthetic": scenario.synthetic,
                "blood_groups": list(scenario.blood_groups),
                "blood_banks": [asdict(bank) for bank in scenario.blood_banks],
                "hospitals": [
                    {"id": hospital.id, "name": hospital.name,
                     "location_id": hospital.location_id,
                     "demand": dict(hospital.demand),
                     "urgency": {group: asdict(value)
                                 for group, value in hospital.urgency.items()}}
                    for hospital in scenario.hospitals
                ],
                "routes": [asdict(route) for route in scenario.routes],
                "compatibility": [
                    {"donor_group": donor, "recipient_group": recipient, "allowed": allowed}
                    for (donor, recipient), allowed in scenario.compatibility.items()
                ],
            }
            for scenario in scenarios
        },
        "scenario_count": len(scenarios),
        "qaoa_repetitions": repetitions,
        "classical_search": {"repetitions": repetitions, "seed_sequence": [seed + i for i in range(repetitions)],
                             "objective_evaluation_budget_per_run": 100, "random_starts": 3,
                             "neighborhood": "one-unit add/remove/transfer; best-improvement"},
        "hybrid_search": {"repetitions": repetitions, "seed_sequence": [seed + i for i in range(repetitions)],
                          "objective_evaluation_budget_per_run": 100,
                          "initialization": "best measured QAOA bitstring; infeasible raw candidates are not repaired"},
        "objective_weights": asdict(objective),
        "qaoa": qaoa_settings,
        "qubo_penalty_weights": asdict(penalties),
        "exact_max_candidate_states": max_exact_states,
        "environment": {
            "python": sys.version.split()[0], "platform": platform.platform(),
            "packages": {name: _package_version(name) for name in
                         ("qiskit", "qiskit-aer", "numpy", "scipy")},
        },
        "limits": {"scenario_count_max": 5 if suite == "baseline" else 6, "qaoa_max_qubits": 16,
                   "max_inventory_units_per_bank": 12, "max_demand_units_per_hospital": 7},
    }
    return {"configuration": config, "results": records}


def _package_version(name: str) -> str | None:
    try:
        return version(name)
    except PackageNotFoundError:
        return None


def _experiment_output_paths(run_id: str) -> tuple[Path, Path]:
    """Return safe output paths for a run without touching existing results."""
    if not run_id.replace("-", "").replace("_", "").isalnum():
        raise ValueError("run id may contain only letters, numbers, hyphens, and underscores")
    results_dir = ROOT / "experiments" / "results"
    config_dir = ROOT / "experiments" / "configurations"
    results_dir.mkdir(parents=True, exist_ok=True)
    config_dir.mkdir(parents=True, exist_ok=True)
    results_path = results_dir / f"{run_id}.json"
    config_path = config_dir / f"{run_id}.json"
    existing = [path for path in (results_path, config_path) if path.exists()]
    if existing:
        names = ", ".join(str(path.relative_to(ROOT)) for path in existing)
        raise FileExistsError(
            f"experiment run id {run_id!r} already has output file(s): {names}; "
            "choose a new --run-id to preserve prior results"
        )
    return results_path, config_path


def _write_experiment_files(
    results_path: Path, config_path: Path, experiment: dict[str, Any]
) -> None:
    """Write a new result/config pair without replacing existing files.

    Exclusive file creation is a second collision check in case another run
    claims the same ID after path validation. If writing either member fails,
    remove only files created by this call so a partial pair is not left behind.
    """
    existing = [path for path in (results_path, config_path) if path.exists()]
    if existing:
        raise FileExistsError(
            "experiment output already exists; choose a new --run-id: "
            + ", ".join(str(path) for path in existing)
        )
    payloads = (
        (results_path, json.dumps(experiment, indent=2) + "\n"),
        (config_path, json.dumps(experiment["configuration"], indent=2) + "\n"),
    )
    created: list[Path] = []
    try:
        for path, payload in payloads:
            with path.open("x", encoding="utf-8") as output:
                created.append(path)
                output.write(payload)
    except Exception:
        for path in created:
            path.unlink(missing_ok=True)
        raise


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--suite", choices=("baseline", "round2"), default="baseline",
                        help="historical five-case baseline or expanded Round 2 suite")
    parser.add_argument("--scenarios", type=int, choices=range(1, 7),
                        help="number of cases (defaults to all cases in the selected suite)")
    parser.add_argument("--repetitions", type=int, default=5, choices=range(1, 21),
                        help="independent QAOA seeds per scenario; classical methods run once")
    parser.add_argument("--seed", type=int, default=7)
    parser.add_argument("--p", type=int, default=1, choices=range(1, 4))
    parser.add_argument("--shots", type=int, default=128, choices=range(32, 1025))
    parser.add_argument("--optimizer", choices=("COBYLA", "Nelder-Mead", "Powell"), default="COBYLA")
    parser.add_argument("--max-iterations", type=int, default=15, choices=range(1, 101))
    parser.add_argument("--penalty-weight", type=float, default=10000.0)
    parser.add_argument("--critical-weight", type=float, default=10.0)
    parser.add_argument("--unmet-weight", type=float, default=5.0)
    parser.add_argument("--transport-cost-weight", type=float, default=1.0)
    parser.add_argument("--transport-time-weight", type=float, default=0.1)
    parser.add_argument("--secondary-penalty-weight", type=float, default=0.0)
    parser.add_argument("--max-exact-states", type=int, default=50_000, choices=range(1, 50_001))
    parser.add_argument("--run-id", help="optional safe filename suffix; defaults to UTC timestamp")
    args = parser.parse_args()
    maximum_scenarios = 5 if args.suite == "baseline" else 6
    scenario_count = args.scenarios if args.scenarios is not None else maximum_scenarios
    if scenario_count > maximum_scenarios:
        parser.error(f"--suite {args.suite} supports at most {maximum_scenarios} scenarios")
    run_id = args.run_id or datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    try:
        results_path, config_path = _experiment_output_paths(run_id)
    except (ValueError, FileExistsError) as error:
        parser.error(str(error))

    experiment = run_experiments(count=scenario_count, suite=args.suite,
                                 repetitions=args.repetitions,
                                 seed=args.seed, p=args.p,
                                 shots=args.shots, optimizer=args.optimizer,
                                 max_iterations=args.max_iterations,
                                 penalty_weight=args.penalty_weight,
                                 max_exact_states=args.max_exact_states,
                                 critical_weight=args.critical_weight,
                                 unmet_weight=args.unmet_weight,
                                 transport_cost_weight=args.transport_cost_weight,
                                 transport_time_weight=args.transport_time_weight,
                                 secondary_penalty_weight=args.secondary_penalty_weight)
    try:
        _write_experiment_files(results_path, config_path, experiment)
    except (OSError, FileExistsError) as error:
        parser.error(str(error))
    print(f"Wrote raw results: {results_path.relative_to(ROOT)}")
    print(f"Wrote configuration: {config_path.relative_to(ROOT)}")
    for row in experiment["results"]:
        print(f"{row['scenario_id']:<24} {row['method']:<7} {row['status']:<16} "
              f"objective={row.get('objective')} feasible={row.get('feasibility')} "
              f"runtime={row.get('runtime_seconds')}s")


if __name__ == "__main__":
    main()
