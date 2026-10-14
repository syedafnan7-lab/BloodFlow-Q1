from __future__ import annotations

import json
from pathlib import Path

from experiments.analyze_results import paired_objective_comparisons
from experiments.run_experiments import build_round2_scenarios
from experiments.search_methods import classical_multistart, local_improve, state_from_allocation
from optimization.constraints import validate_allocation
from optimization.exact import ExactSolver, ExactSolverConfig
from optimization.greedy import GreedyAllocator
from optimization.objective import ObjectiveConfig

ROOT = Path(__file__).resolve().parents[1]


def objective() -> ObjectiveConfig:
    return ObjectiveConfig(10.0, 5.0, 1.0, 0.1, 0.0)


def test_classical_search_is_seeded_feasible_and_within_evaluation_budget() -> None:
    scenario = build_round2_scenarios()[-1]
    initial = GreedyAllocator().solve(scenario, objective())
    first, metrics = classical_multistart(
        scenario, objective(), initial.allocation, seed=101,
        max_evaluations=100, random_starts=3,
    )
    again, _ = classical_multistart(
        scenario, objective(), initial.allocation, seed=101,
        max_evaluations=100, random_starts=3,
    )
    report = validate_allocation(scenario, first.allocation, first.unmet_demand)
    exact = ExactSolver(ExactSolverConfig(max_candidate_states=50_000)).solve(scenario, objective())

    assert report["feasible"] is True
    assert metrics["objective_evaluations"] <= 100
    assert first.objective == again.objective
    assert first.objective == exact.objective_breakdown.total_objective


def test_hybrid_refinement_uses_same_search_and_never_worsens_feasible_seed() -> None:
    scenario = build_round2_scenarios()[0]
    start = GreedyAllocator().solve(scenario, objective())
    state = state_from_allocation(scenario, objective(), start.allocation)
    result, metrics = local_improve(scenario, objective(), state,
                                    max_evaluations=100, target_objective=25.2)
    assert result.objective <= state.objective
    assert metrics["objective_evaluations"] <= 100
    assert metrics["time_to_target_seconds"] == 0.0


def test_paired_comparison_uses_only_shared_feasible_seed_pairs() -> None:
    rows = [
        {"scenario_id": "case", "method": "classical_multistart", "seed": 1,
         "objective": 10.0, "feasibility": True},
        {"scenario_id": "case", "method": "qaoa", "seed": 1,
         "objective": 12.0, "feasibility": True},
        {"scenario_id": "case", "method": "classical_multistart", "seed": 2,
         "objective": 10.0, "feasibility": True},
        {"scenario_id": "case", "method": "qaoa", "seed": 2,
         "objective": 999.0, "feasibility": False},
    ]
    result = paired_objective_comparisons(rows, bootstrap_samples=100)
    qaoa = next(row for row in result if row["method"] == "qaoa")
    assert qaoa["paired_feasible_seeds"] == 1
    assert qaoa["mean_objective_improvement"] == -2.0
    assert qaoa["bootstrap_95pct_interval"] == [-2.0, -2.0]


def test_demo_study_json_is_the_same_confirmatory_run_as_raw_artifact() -> None:
    raw = json.loads((ROOT / "experiments/results/quantum-value-confirmatory-seed301-20261015.json").read_text())
    demo = json.loads((ROOT / "frontend/public/quantum-value-study.json").read_text())
    assert demo == raw
    assert len(demo["results"]) == 198
    assert demo["configuration"]["classical_search"]["seed_sequence"] == list(range(301, 311))
