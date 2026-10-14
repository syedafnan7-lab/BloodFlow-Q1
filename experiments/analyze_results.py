"""Summarize one actual experiment JSON file without changing its measurements."""

from __future__ import annotations

import argparse
import json
import math
import statistics
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
METRICS = (
    ("objective", "Objective"),
    ("critical_satisfaction", "Critical satisfaction rate"),
    ("total_unmet_demand", "Total unmet demand"),
    ("transport_cost", "Transport cost"),
    ("average_travel_time", "Average travel time"),
    ("runtime_seconds", "Runtime (seconds)"),
    ("approximation_gap", "Approximation gap vs Exact"),
)


def summarize(experiment: dict[str, Any]) -> dict[str, Any]:
    rows = experiment["results"]
    summary: dict[str, Any] = {"scenario_count": experiment["configuration"]["scenario_count"],
                               "methods": {}}
    methods = ("greedy", "milp", "exact", "qaoa")
    for method in methods:
        method_rows = [row for row in rows if row["method"] == method]
        method_summary: dict[str, Any] = {
            "attempt_count": len(method_rows),
            "completed_count": sum(row.get("status") in {"completed", "infeasible"} for row in method_rows),
            "status_counts": {status: sum(row.get("status") == status for row in method_rows)
                              for status in sorted({row.get("status") for row in method_rows})},
            "feasible_count": sum(row.get("feasibility") is True for row in method_rows),
            "infeasible_count": sum(row.get("feasibility") is False for row in method_rows),
            "feasibility_rate_over_attempts": (
                sum(row.get("feasibility") is True for row in method_rows) / len(method_rows)
                if method_rows else None
            ),
            "metrics": {},
        }
        for metric, _label in METRICS:
            # Objective values for infeasible QAOA samples use an unpenalized
            # expression, so they are excluded from solver-to-solver objective
            # summaries. Other observed metrics are retained for completed
            # QAOA samples, with feasibility counts shown separately.
            eligible = [row.get(metric) for row in method_rows
                        if row.get("status") in {"completed", "infeasible"}
                        and row.get(metric) is not None
                        and (metric != "objective" or row.get("feasibility") is True)]
            values = [float(value) for value in eligible if math.isfinite(float(value))]
            method_summary["metrics"][metric] = {
                "count": len(values),
                "mean": statistics.fmean(values) if values else None,
                "median": statistics.median(values) if values else None,
                "minimum": min(values) if values else None,
                "maximum": max(values) if values else None,
                "standard_deviation_population": statistics.pstdev(values) if values else None,
            }
        summary["methods"][method] = method_summary
    return summary


def render_report(experiment: dict[str, Any], summary: dict[str, Any], source: str) -> str:
    config = experiment["configuration"]
    rows = experiment["results"]
    lines = [
        "# BloodFlow-Q Experiment Results", "",
        f"**Raw data:** [`{Path(source).name}`](../{Path(source).as_posix()})  ",
        f"**Configuration:** [`{Path(source).stem}.json`](../experiments/configurations/{Path(source).stem}.json)",
        "", "## Methodology", "",
        "This report is generated from the raw JSON experiment output. It does not alter source measurements. "
        "Each method runs on the same fictional scenario with a shared objective. Greedy is the "
        "deterministic baseline; MILP uses HiGHS; Exact enumerates bounded allocation states up to its configured limit; "
        "QAOA uses the local Qiskit Aer simulator, samples finite-shot bitstrings, decodes them, and runs "
        "the shared classical feasibility validator. An infeasible QAOA sample is retained as infeasible and "
        "is not repaired. Runtime is measured locally and is environment-dependent.", "",
        "## Number and size of scenarios", "",
        f"Suite: **{config.get('suite', 'baseline')}**; scenarios: **{config['scenario_count']}**. Full inputs "
        f"and settings are in [`{Path(source).stem}.json`](../experiments/configurations/{Path(source).stem}.json). "
        "The Round 2 suite includes a deterministic 2-bank/2-hospital/1-group case with four routes. All values are "
        "synthetic. QUBO bit counts are reported per case; local QAOA is capped at 16 variables.", "",
        "| Scenario | Banks | Hospitals | Groups | Routes | Allocation vars | Inventory units | Demand units | QUBO bits |", "|---|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    qaoa_variables = {row["scenario_id"]: row.get("qubo_variable_count")
                      for row in rows if row["method"] == "qaoa"}
    for scenario_id, size in config["scenario_sizes"].items():
        lines.append(f"| {scenario_id} | {size['blood_banks']} | {size['hospitals']} | {size['blood_groups']} | {size.get('routes', '—')} | {size['allocation_decision_variables']} | {size['inventory_units']} | {size['demand_units']} | {qaoa_variables.get(scenario_id, '—')} |")
    lines += ["", "## Parameters", "",
              f"- Objective weights: `{json.dumps(config['objective_weights'], sort_keys=True)}`",
              f"- QAOA: `{json.dumps(config['qaoa'], sort_keys=True)}`",
              f"- QAOA repetitions: `{config.get('qaoa_repetitions', 1)}` independent seeds per scenario; failures remain in raw results.",
              f"- QUBO penalty weights: `{json.dumps(config['qubo_penalty_weights'], sort_keys=True)}`",
              f"- Exact candidate-state cap: `{config['exact_max_candidate_states']:,}`",
              f"- Software versions: `{json.dumps(config['environment']['packages'], sort_keys=True)}`", "",
              "## Per-scenario results", "",
              "`Feasible` is the validator result. A QAOA objective is reported only for a feasible decoded allocation; "
              "an infeasible measured candidate's raw objective expression is not comparable and is excluded from "
              "objective statistics. Approximation gap is `(method objective - reference objective) / abs(reference objective)` "
              "and is recorded only when the method and the optimum-capable reference are feasible. Runtime includes solving and "
              "the independent validation performed by this runner.", "",
              "| Scenario | Method | Rep | Seed | Status | Objective | Critical satisfied | Unmet | Transport cost | Avg travel time | Feasible | Runtime (s) | Gap vs reference |",
              "|---|---|---:|---:|---|---:|---:|---:|---:|---:|:---:|---:|---:|"]
    for row in rows:
        val = lambda value: "—" if value is None else (f"{value:.6g}" if isinstance(value, float) else str(value))
        critical = None if row.get("critical_satisfaction") is None else 100 * row["critical_satisfaction"]
        lines.append("| " + " | ".join((row["scenario_id"], row["method"],
            val(row.get("repetition")), val(row.get("seed")), row["status"],
            val(row.get("objective")), "—" if critical is None else f"{critical:.1f}%",
            val(row.get("total_unmet_demand")), val(row.get("transport_cost")),
            val(row.get("average_travel_time")), val(row.get("feasibility")),
            val(row.get("runtime_seconds")), val(row.get("approximation_gap")))) + " |")
    qaoa_rows = [row for row in rows if row.get("method") == "qaoa"]
    if qaoa_rows:
        lines += ["", "## QAOA repeated-run summary by scenario", "",
                  "Objective statistics below use feasible measured candidates only. Feasibility rate uses all attempted seeds, including errors.", "",
                  "| Scenario | Attempts | Measured | Feasible | Feasibility rate | Mean feasible objective | Median | Population SD | Mean runtime (s) |",
                  "|---|---:|---:|---:|---:|---:|---:|---:|---:|"]
        for scenario_id in config["scenario_sizes"]:
            scenario_rows = [row for row in qaoa_rows if row["scenario_id"] == scenario_id]
            feasible_objectives = [float(row["objective"]) for row in scenario_rows
                                   if row.get("feasibility") is True and row.get("objective") is not None
                                   and math.isfinite(float(row["objective"]))]
            measured_times = [float(row["runtime_seconds"]) for row in scenario_rows
                              if row.get("status") in {"completed", "infeasible"}
                              and row.get("runtime_seconds") is not None]
            fmt = lambda value: "—" if value is None else f"{value:.6g}"
            lines.append("| " + " | ".join((
                scenario_id, str(len(scenario_rows)),
                str(sum(row.get("status") in {"completed", "infeasible"} for row in scenario_rows)),
                str(len(feasible_objectives)),
                fmt(len(feasible_objectives) / len(scenario_rows) if scenario_rows else None),
                fmt(statistics.fmean(feasible_objectives) if feasible_objectives else None),
                fmt(statistics.median(feasible_objectives) if feasible_objectives else None),
                fmt(statistics.pstdev(feasible_objectives) if feasible_objectives else None),
                fmt(statistics.fmean(measured_times) if measured_times else None),
            )) + " |")
    lines += ["", "## Summary statistics", "",
              "Mean, median, minimum, maximum, and population standard deviation are calculated across available "
              "measurements only. No missing or failed run is converted to zero. Objective summaries use feasible "
              "results only; the remaining metrics use actual completed outputs, including infeasible QAOA samples. "
              "Critical satisfaction is summarized as a fraction from 0 to 1 (the scenario table shows percentages).", ""]
    for method in ("greedy", "milp", "exact", "qaoa"):
        method_summary = summary["methods"][method]
        lines += [f"### {method.title()}", "",
                  f"Attempts: `{method_summary['attempt_count']}`; completed: `{method_summary['completed_count']}`; "
                  f"feasible: `{method_summary['feasible_count']}`; infeasible: `{method_summary['infeasible_count']}`; "
                  f"feasible/attempted: `{method_summary['feasibility_rate_over_attempts']}`; statuses: "
                  f"`{method_summary['status_counts']}`.", "",
                  "| Metric | n | Mean | Median | Min | Max | Std. dev. (population) |", "|---|---:|---:|---:|---:|---:|---:|"]
        for metric, label in METRICS:
            values = method_summary["metrics"][metric]
            fmt = lambda value: "—" if value is None else f"{value:.6g}"
            lines.append(f"| {label} | {values['count']} | {fmt(values['mean'])} | {fmt(values['median'])} | {fmt(values['minimum'])} | {fmt(values['maximum'])} | {fmt(values['standard_deviation_population'])} |")
        lines.append("")
    lines += ["## Interpretation", "",
              "These measurements describe only this small synthetic instance set and this local software environment. "
              "Greedy, MILP, and Exact outputs can be compared on the same objective. Exact is an exhaustive reference "
              "only for cases solved within its cap; MILP is an optimum reference only when HiGHS reports success. "
              "Repeated QAOA seeds are descriptive observations, not formal statistical evidence. QAOA uses a hybrid classical optimizer "
              "and local simulator, so its runtime includes classical optimization and simulator work. Finite shots "
              "can yield infeasible samples; those remain visible. The sample is too small and the execution setup "
              "too limited to support broad performance claims.", "",
              "## Limitations", "",
              "- Cases remain small synthetic research instances; the two-bank/two-hospital case is not representative of an operational network.",
              "- Compatibility is a simplified prototype assumption, not a complete clinical compatibility model.",
              "- Local simulator results and wall-clock timings depend on package versions, machine load, and platform.",
              "- The QAOA candidate is a measured sample, not an optimality proof. Infeasible samples are not repaired.",
              "- The fixed seed supports repeatability but does not guarantee bit-identical results across environments.", "",
              "## Quantum advantage statement", "",
              "**These results do not demonstrate quantum advantage.** They are small, local simulator experiments with a hybrid classical-quantum workflow. No comparison establishes an advantage over classical optimization in runtime, quality, scale, or energy use.", "",
              "## Data integrity", "",
              "Raw result values are preserved in the linked JSON output. This report contains derived descriptive statistics only; it does not overwrite or edit raw results.", ""]
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("results", type=Path, help="raw experiment JSON file")
    parser.add_argument("--report", type=Path, default=ROOT / "docs" / "EXPERIMENT_RESULTS.md")
    parser.add_argument("--summary-json", type=Path, help="optional machine-readable statistics output")
    args = parser.parse_args()
    path = args.results if args.results.is_absolute() else ROOT / args.results
    experiment = json.loads(path.read_text(encoding="utf-8"))
    summary = summarize(experiment)
    try:
        source = str(path.relative_to(ROOT))
    except ValueError:
        source = str(path)
    report = render_report(experiment, summary, source)
    report_path = args.report if args.report.is_absolute() else ROOT / args.report
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(report, encoding="utf-8")
    if args.summary_json:
        summary_path = args.summary_json if args.summary_json.is_absolute() else ROOT / args.summary_json
        summary_path.parent.mkdir(parents=True, exist_ok=True)
        summary_path.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    print(f"Analyzed {len(experiment['results'])} raw result rows from {path}")
    print(f"Wrote {report_path}")


if __name__ == "__main__":
    main()
