from __future__ import annotations

from experiments.analyze_results import summarize
from experiments.run_experiments import build_round2_scenarios
from optimization.exact import ExactSolver, ExactSolverConfig
from optimization.greedy import GreedyAllocator
from optimization.milp import MILPSolver
from optimization.objective import ObjectiveConfig
from quantum.qubo import count_scenario_qubo_variables


def _objective() -> ObjectiveConfig:
    return ObjectiveConfig(
        critical_unmet_weight=10.0,
        total_unmet_weight=5.0,
        transportation_cost_weight=1.0,
        transportation_time_weight=0.1,
        secondary_penalty_weight=0.0,
    )


def test_round2_suite_adds_two_bank_two_hospital_case_within_qaoa_limit() -> None:
    scenarios = build_round2_scenarios()
    multi = scenarios[-1]

    assert len(scenarios) == 6
    assert (len(multi.blood_banks), len(multi.hospitals), len(multi.routes)) == (2, 2, 4)
    assert len(multi.allocation_variables()) == 4
    assert count_scenario_qubo_variables(multi) <= 16

    milp = MILPSolver().solve(multi, _objective())
    exact = ExactSolver(ExactSolverConfig(max_candidate_states=50_000)).solve(multi, _objective())
    assert milp.feasibility_report["feasible"] is True
    assert exact.feasibility_report["feasible"] is True
    assert milp.objective_value == exact.objective_breakdown.total_objective


def test_transport_cost_tradeoff_is_explicit_and_milp_matches_exact() -> None:
    tradeoff = build_round2_scenarios()[2]
    greedy = GreedyAllocator().solve(tradeoff, _objective())
    milp = MILPSolver().solve(tradeoff, _objective())
    exact = ExactSolver(ExactSolverConfig(max_candidate_states=50_000)).solve(tradeoff, _objective())

    assert sum(item.quantity for item in milp.allocation) == 0
    assert sum(item.quantity for item in greedy.allocation) == 1
    assert greedy.objective_breakdown.total_objective == 41.0
    assert milp.unmet_demand[(tradeoff.hospitals[0].id, "O")] == 1
    assert milp.objective_value == 5.0
    assert exact.objective_breakdown.total_objective == milp.objective_value


def test_repeated_qaoa_summary_counts_failures_and_infeasible_runs() -> None:
    rows = [
        {"scenario_id": "case", "method": "qaoa", "status": "completed",
         "feasibility": True, "objective": 10.0, "runtime_seconds": 0.3,
         "repetition": 1, "seed": 7},
        {"scenario_id": "case", "method": "qaoa", "status": "infeasible",
         "feasibility": False, "objective": 999.0, "runtime_seconds": 0.4,
         "repetition": 2, "seed": 8},
        {"scenario_id": "case", "method": "qaoa", "status": "error",
         "feasibility": None, "objective": None, "runtime_seconds": 0.5,
         "repetition": 3, "seed": 9},
    ]
    summary = summarize({"configuration": {"scenario_count": 1}, "results": rows})["methods"]["qaoa"]

    assert summary["attempt_count"] == 3
    assert summary["completed_count"] == 2  # measured infeasible samples count as completed runs
    assert summary["feasible_count"] == 1
    assert summary["infeasible_count"] == 1
    assert summary["feasibility_rate_over_attempts"] == 1 / 3
    assert summary["metrics"]["objective"]["count"] == 1
    assert summary["metrics"]["objective"]["mean"] == 10.0
