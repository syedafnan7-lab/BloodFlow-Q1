import { useMemo } from 'react';
import { AlertTriangle, Boxes, Droplet, Hospital, Route as RouteIcon } from 'lucide-react';
import { api } from '../services/api';
import { useApi } from '../hooks/useApi';
import { ErrorState, LoadingState } from '../components/Feedback';
import PageHeader from '../components/PageHeader';
import { StatItem } from '../components/DataField';
import VascularNetworkMap from '../components/VascularNetworkMap';
import { routeStatusKind } from '../utils/vascularGraph';

export default function Network() {
  const { data, loading, error, reload } = useApi(api.getScenario, []);
  const routes = data?.routes || [];
  const banks = data?.blood_banks || [];
  const hospitals = data?.hospitals || [];
  const routeCounts = useMemo(() => routes.reduce((counts, route) => {
    const kind = routeStatusKind(route?.status);
    counts[kind] = (counts[kind] || 0) + 1;
    return counts;
  }, {}), [routes]);

  return <>
    <PageHeader
      eyebrow="SUPPLY & DISTRIBUTION NETWORK"
      title="Transport Network"
      description="Explore the scenario’s blood-bank supply, hospital demand, and modeled route connections. This network is schematic because facility coordinates are not part of the model."
    />

    {loading && <LoadingState label="Loading logistics network model…" />}
    {!loading && error && <ErrorState message={error} onRetry={reload} />}

    {!loading && !error && data?.synthetic === true && <div className="network-page-flow">
      <section className="network-kpi-grid" aria-label="Synthetic scenario network summary">
        <StatItem label="Supply facilities" value={banks.length} unit="blood banks" />
        <StatItem label="Demand facilities" value={hospitals.length} unit="hospitals" />
        <StatItem label="Available routes" value={routeCounts.available || 0} unit="modeled connections" tone="success" />
        <StatItem label="Blocked routes" value={routeCounts.blocked || 0} unit="scenario disruptions" tone={(routeCounts.blocked || 0) > 0 ? 'warning' : 'default'} />
      </section>

      <VascularNetworkMap banks={banks} hospitals={hospitals} routes={routes} />

      <section className="network-data-provenance" aria-label="Network model notes">
        <div className="network-provenance-mark"><RouteIcon size={16}/></div>
        <p><strong>Scenario data</strong> Facilities, stock, demand, route relationships, distance, travel-time and cost values come directly from the active synthetic scenario. They are model parameters, not live operations data.</p>
        <div className="network-status-counts"><span><Droplet size={13}/> {banks.length} banks</span><span><Hospital size={13}/> {hospitals.length} hospitals</span><span><Boxes size={13}/> {routes.length} routes</span>{(routeCounts.unknown || 0) > 0 && <span><AlertTriangle size={13}/> {routeCounts.unknown} unknown status</span>}</div>
      </section>
    </div>}

    {!loading && !error && data && data.synthetic !== true && <div className="notice notice-error" role="status">
      The backend did not identify this scenario as synthetic. Network information is not displayed.
    </div>}
  </>;
}
