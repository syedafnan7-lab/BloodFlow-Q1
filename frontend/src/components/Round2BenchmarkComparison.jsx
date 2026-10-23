import { useMemo, useState } from 'react';
import { Download, Info } from 'lucide-react';

const METHOD_LABELS = { exact: 'Exact reference', greedy: 'Greedy baseline', qaoa: 'QAOA' };
const scenarioLabel = (value) => value.replaceAll('_', ' ');
const mean = (values) => values.length ? values.reduce((total, value) => total + value, 0) / values.length : null;
const rate = (items) => {
  const completed = items.filter((row) => row.status === 'completed' || row.status === 'infeasible');
  return completed.length ? completed.filter((row) => row.feasibility === true).length / completed.length : null;
};
const display = (value, digits = 1) => Number.isFinite(value) ? value.toFixed(digits) : 'Unavailable';

function downloadScenarioCsv(rows) {
  const columns = ['scenario_id', 'method', 'status', 'objective', 'feasibility', 'critical_satisfaction', 'critical_unmet_demand', 'total_unmet_demand', 'transport_cost', 'average_travel_time', 'runtime_seconds', 'approximation_gap'];
  const csv = [columns.join(','), ...rows.map((row) => columns.map((column) => JSON.stringify(row[column] ?? '')).join(','))].join('\n');
  const url = URL.createObjectURL(new Blob([csv], { type: 'text/csv;charset=utf-8' }));
  const anchor = document.createElement('a');
  anchor.href = url;
  anchor.download = 'bloodflow-q-round2-visible-runs.csv';
  anchor.click();
  URL.revokeObjectURL(url);
}

export default function Round2BenchmarkComparison({ study, error }) {
  const [scenario, setScenario] = useState('all');
  const [method, setMethod] = useState('all');
  const [selectedRun, setSelectedRun] = useState(null);
  const allRows = study?.results || [];
  const scenarios = study?.configuration?.scenarios ? Object.keys(study.configuration.scenarios) : [...new Set(allRows.map((row) => row.scenario_id))];
  const visibleRows = useMemo(() => allRows.filter((row) => (scenario === 'all' || row.scenario_id === scenario) && (method === 'all' || row.method === method)), [allRows, scenario, method]);
  const methods = [...new Set(allRows.map((row) => row.method))];
  const summaries = methods.map((id) => {
    const rows = visibleRows.filter((row) => row.method === id);
    return { id, rows, feasibility: rate(rows), runtime: mean(rows.map((row) => row.runtime_seconds).filter(Number.isFinite)), unmet: mean(rows.map((row) => row.total_unmet_demand).filter(Number.isFinite)), completed: rows.filter((row) => ['completed', 'infeasible'].includes(row.status)).length, attempts: rows.length };
  });
  const current = visibleRows.find((row) => `${row.scenario_id}-${row.method}` === selectedRun);
  if (error) return <section className="panel round2-panel" role="status">Round 2 artifact unavailable: {error}</section>;
  if (!study) return <section className="panel round2-panel" aria-busy="true">Loading Round 2 benchmark artifact…</section>;
  const config = study.configuration || {};
  return <section className="panel round2-panel" aria-labelledby="round2-title">
    <header className="round2-heading"><div><span className="eyebrow">HISTORICAL BENCHMARK · CANONICAL ROUND 2 ARTIFACT</span><h2 id="round2-title">Round 2 solver benchmark</h2><p>A one-run-per-method comparison across five synthetic cases. It is exploratory evidence, distinct from both the repeated confirmatory benchmark and the matched warm-start experiment.</p></div><a className="button button-secondary button-small" href="/round2-benchmark-20261007-01.json" download><Download size={14}/> Raw artifact</a></header>
    <div className="round2-meta"><span><b>Artifact</b> {config.invocation?.arguments?.at(-1) || '20261007-01'}</span><span><b>Runs</b> {allRows.length} across {scenarios.length} scenarios</span><span><b>Methods</b> Exact · Greedy · QAOA</span><span><b>QAOA</b> p={config.qaoa?.p ?? '—'} · {config.qaoa?.shots ?? '—'} shots · {config.qaoa?.optimizer || '—'}</span><span><b>Execution</b> Local Qiskit Aer simulator</span></div>
    <div className="round2-controls"><label>Scenario<select className="field-control" value={scenario} onChange={(event) => { setScenario(event.target.value); setSelectedRun(null); }}><option value="all">All scenarios</option>{scenarios.map((id) => <option key={id} value={id}>{scenarioLabel(id)}</option>)}</select></label><label>Method<select className="field-control" value={method} onChange={(event) => { setMethod(event.target.value); setSelectedRun(null); }}><option value="all">All methods</option>{methods.map((id) => <option key={id} value={id}>{METHOD_LABELS[id] || id}</option>)}</select></label><button className="button button-secondary button-small" type="button" onClick={() => downloadScenarioCsv(visibleRows)}><Download size={14}/> Export filtered CSV</button></div>
    <div className="round2-summary-grid">{summaries.map((item) => <article key={item.id}><h3>{METHOD_LABELS[item.id] || item.id}</h3><div className="round2-primary">{item.feasibility == null ? 'Unavailable' : `${(item.feasibility * 100).toFixed(0)}%`}<small>feasible completed runs · {item.completed}/{item.attempts} shown</small></div><div className="round2-meter" role="img" aria-label={`${METHOD_LABELS[item.id] || item.id} feasibility ${(item.feasibility || 0) * 100}%`}><i style={{ width: `${(item.feasibility || 0) * 100}%` }}/></div><p>Mean unmet demand {display(item.unmet, 2)} · mean runtime {item.runtime == null ? 'Unavailable' : `${(item.runtime * 1000).toFixed(2)} ms`}</p></article>)}</div>
    <div className="round2-scenarios"><div className="warm-study-cases-title"><h3>Scenario outcomes</h3><span>One observation per method and scenario; no uncertainty interval can be estimated.</span></div><div className="table-scroll"><table className="data-table"><thead><tr><th>Scenario</th><th>Method</th><th>Status</th><th>Feasible</th><th>Objective</th><th>Unmet demand</th><th>Runtime</th></tr></thead><tbody>{visibleRows.map((row) => <tr key={`${row.scenario_id}-${row.method}`} className={selectedRun === `${row.scenario_id}-${row.method}` ? 'is-selected' : ''}><th scope="row"><button type="button" className="text-button" onClick={() => { setScenario(row.scenario_id); setSelectedRun(`${row.scenario_id}-${row.method}`); }}>{scenarioLabel(row.scenario_id)}</button></th><td>{METHOD_LABELS[row.method] || row.method}</td><td>{row.status}</td><td>{row.feasibility === true ? 'Yes' : row.feasibility === false ? 'No' : 'Unavailable'}</td><td>{display(row.objective, 2)}</td><td>{display(row.total_unmet_demand, 0)}</td><td>{row.runtime_seconds == null ? 'Unavailable' : `${(row.runtime_seconds * 1000).toFixed(3)} ms`}</td></tr>)}</tbody></table></div></div>
    {current && <div className="round2-run-detail"><strong>{scenarioLabel(current.scenario_id)} · {METHOD_LABELS[current.method] || current.method}</strong><span>Objective basis: {current.objective_basis || 'Not recorded'}</span><span>Critical satisfaction: {current.critical_satisfaction == null ? 'Unavailable' : `${(current.critical_satisfaction * 100).toFixed(1)}%`}</span><span>Critical unmet demand: {current.critical_unmet_demand ?? 'Unavailable'}</span><span>Transport cost: {display(current.transport_cost, 2)}</span><span>Approximation gap: {current.approximation_gap == null ? 'Not available for this reference' : display(current.approximation_gap, 4)}</span><details><summary>Validation and allocation evidence</summary><pre>{JSON.stringify({ validation: current.validation, allocation: current.allocation, unmet_demand: current.unmet_demand }, null, 2)}</pre></details></div>}
    <details className="round2-limitations"><summary><Info size={14}/> Methods and limitations</summary><p>Five synthetic scenarios with one run per method per case; the dataset supports descriptive comparisons only and provides no repeated-seed uncertainty estimate. Exact is a classical small-instance reference. Runtime is recorded local end-to-end execution, not a hardware speedup comparison. QAOA uses a local simulator; these observations do not establish quantum advantage.</p><a href="/round2-benchmark-20261007-01.json" download>Download original artifact</a></details>
  </section>;
}
