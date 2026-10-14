"""Bounded feasible local search used in quantum-initialization experiments.

All scores are recomputed with the production objective and validator. The
classical baseline and QAOA-initialized method use the same one-unit
add/remove/transfer neighborhood and evaluation limit.
"""

from __future__ import annotations

import random
from dataclasses import dataclass
from time import perf_counter
from typing import Sequence

from optimization.constraints import validate_allocation
from optimization.models import AllocationDecision, AllocationVariable, Scenario
from optimization.objective import ObjectiveConfig, calculate_objective


@dataclass(frozen=True)
class SearchState:
    quantities: tuple[int, ...]
    allocation: tuple[AllocationDecision, ...]
    unmet_demand: dict[tuple[str, str], int]
    objective: float


def state_from_allocation(scenario: Scenario, config: ObjectiveConfig,
                          allocation: Sequence[AllocationDecision]) -> SearchState:
    variables = scenario.allocation_variables()
    keys = {(v.source, v.destination, v.blood_group, v.recipient_group): i
            for i, v in enumerate(variables)}
    values = [0] * len(variables)
    bank_used: dict[tuple[str, str], int] = {}
    served: dict[tuple[str, str], int] = {}
    for row in allocation:
        key = (row.source, row.destination, row.blood_group, row.recipient_group)
        if key not in keys:
            raise ValueError("starting allocation contains an ineligible shipment")
        index = keys[key]
        values[index] += row.quantity
        bank = (row.source, row.blood_group)
        demand = (row.destination, row.recipient_group)
        bank_used[bank] = bank_used.get(bank, 0) + row.quantity
        served[demand] = served.get(demand, 0) + row.quantity
    for key, quantity in bank_used.items():
        banks = {b.id: b for b in scenario.blood_banks}
        if quantity > banks[key[0]].inventory[key[1]]:
            raise ValueError("starting allocation exceeds inventory")
    hospitals = {h.id: h for h in scenario.hospitals}
    unmet = {(h.id, g): amount - served.get((h.id, g), 0)
             for h in scenario.hospitals for g, amount in h.demand.items()}
    decisions = tuple(AllocationDecision(v.source, v.destination, v.blood_group,
                                         v.recipient_group, values[i])
                      for i, v in enumerate(variables) if values[i] > 0)
    validation = validate_allocation(scenario, decisions, unmet)
    if not validation["feasible"]:
        raise ValueError(f"starting allocation is infeasible: {validation['violations']}")
    score = calculate_objective(scenario, decisions, config).total_objective
    return SearchState(tuple(values), decisions, unmet, float(score))


def _state_from_quantities(scenario: Scenario, config: ObjectiveConfig,
                           variables: Sequence[AllocationVariable],
                           quantities: Sequence[int]) -> SearchState:
    allocation = tuple(AllocationDecision(v.source, v.destination, v.blood_group,
                                          v.recipient_group, int(quantities[i]))
                       for i, v in enumerate(variables) if quantities[i] > 0)
    return state_from_allocation(scenario, config, allocation)


def random_feasible_state(scenario: Scenario, config: ObjectiveConfig,
                          rng: random.Random) -> SearchState:
    variables = scenario.allocation_variables()
    banks = {b.id: b for b in scenario.blood_banks}
    hospitals = {h.id: h for h in scenario.hospitals}
    remaining_inventory = {(b.id, g): q for b in scenario.blood_banks
                           for g, q in b.inventory.items()}
    remaining_demand = {(h.id, g): q for h in scenario.hospitals
                        for g, q in h.demand.items()}
    order = list(variables)
    rng.shuffle(order)
    allocation: list[AllocationDecision] = []
    for v in order:
        bank_key = (v.source, v.blood_group)
        demand_key = (v.destination, v.recipient_group)
        upper = min(v.upper_bound, remaining_inventory[bank_key], remaining_demand[demand_key])
        quantity = rng.randint(0, upper)
        if quantity:
            allocation.append(AllocationDecision(v.source, v.destination, v.blood_group,
                                                 v.recipient_group, quantity))
            remaining_inventory[bank_key] -= quantity
            remaining_demand[demand_key] -= quantity
    return state_from_allocation(scenario, config, allocation)


def local_improve(scenario: Scenario, config: ObjectiveConfig, start: SearchState,
                  *, max_evaluations: int = 100,
                  target_objective: float | None = None) -> tuple[SearchState, dict[str, object]]:
    """Steepest descent over feasible 1-unit add, remove, and transfer moves."""
    if max_evaluations < 1:
        raise ValueError("max_evaluations must be positive")
    variables = scenario.allocation_variables()
    current = start
    evaluations = 0
    started = perf_counter()
    first_feasible_seconds = 0.0  # All accepted starts are validated before search.
    threshold = target_objective * 1.05 if target_objective is not None else None
    time_to_threshold = (0.0 if threshold is not None and current.objective <= threshold
                         else None)
    while evaluations < max_evaluations:
        best = current
        for i in range(len(variables)):
            if evaluations >= max_evaluations:
                break
            for delta in (-1, 1):
                candidate = list(current.quantities)
                candidate[i] += delta
                if candidate[i] < 0 or candidate[i] > variables[i].upper_bound:
                    continue
                try:
                    state = _state_from_quantities(scenario, config, variables, candidate)
                except ValueError:
                    continue
                evaluations += 1
                if state.objective < best.objective - 1e-12:
                    best = state
                if time_to_threshold is None and threshold is not None and state.objective <= threshold:
                    time_to_threshold = perf_counter() - started
            # Atomic source/destination reallocation, so an improving move
            # need not pass through a worse intermediate allocation.
            if current.quantities[i] > 0:
                for j in range(len(variables)):
                    if i == j or evaluations >= max_evaluations:
                        continue
                    source, target = variables[i], variables[j]
                    if (source.destination, source.recipient_group) != (target.destination, target.recipient_group):
                        continue
                    candidate = list(current.quantities)
                    candidate[i] -= 1
                    candidate[j] += 1
                    if candidate[j] > target.upper_bound:
                        continue
                    try:
                        state = _state_from_quantities(scenario, config, variables, candidate)
                    except ValueError:
                        continue
                    evaluations += 1
                    if state.objective < best.objective - 1e-12:
                        best = state
                    if time_to_threshold is None and threshold is not None and state.objective <= threshold:
                        time_to_threshold = perf_counter() - started
        if best.objective >= current.objective - 1e-12:
            break
        current = best
    return current, {
        "objective_evaluations": evaluations,
        "evaluation_budget": max_evaluations,
        "first_feasible_seconds": first_feasible_seconds,
        "time_to_target_seconds": time_to_threshold,
        "search_runtime_seconds": perf_counter() - started,
    }


def classical_multistart(scenario: Scenario, config: ObjectiveConfig,
                         greedy_allocation: Sequence[AllocationDecision], *,
                         seed: int, max_evaluations: int = 100,
                         random_starts: int = 3,
                         target_objective: float | None = None,
                         initialization_seconds: float = 0.0) -> tuple[SearchState, dict[str, object]]:
    """Search from greedy and seeded feasible starts under one shared budget."""
    started = perf_counter() - initialization_seconds
    rng = random.Random(seed)
    starts = [state_from_allocation(scenario, config, greedy_allocation)]
    starts.extend(random_feasible_state(scenario, config, rng) for _ in range(random_starts))
    remaining = max_evaluations
    best = starts[0]
    evaluations = 0
    best_metadata: dict[str, object] = {}
    time_to_target = (initialization_seconds if target_objective is not None
                      and starts[0].objective <= target_objective * 1.05 else None)
    for index, start in enumerate(starts):
        budget = max(1, remaining // (len(starts) - index))
        state, metadata = local_improve(scenario, config, start, max_evaluations=budget,
                                        target_objective=target_objective)
        if (time_to_target is None and metadata.get("time_to_target_seconds") is not None):
            time_to_target = (perf_counter() - started - float(metadata["search_runtime_seconds"])
                              + float(metadata["time_to_target_seconds"]))
        evaluations += int(metadata["objective_evaluations"])
        remaining = max(0, max_evaluations - evaluations)
        if state.objective < best.objective:
            best, best_metadata = state, metadata
        if remaining == 0:
            break
    return best, {
        "objective_evaluations": evaluations,
        "evaluation_budget": max_evaluations,
        "first_feasible_seconds": 0.0,
        "time_to_target_seconds": time_to_target,
        "search_runtime_seconds": perf_counter() - started,
        "seed": seed,
        "random_starts": random_starts,
    }
