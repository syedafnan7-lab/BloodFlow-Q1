import { useMemo, useRef, useState } from 'react';
import { Activity, ArrowDownRight, ArrowRight, Building2, CircleHelp, Droplet, Hospital, Minus, Plus, RotateCcw, Search, X } from 'lucide-react';
import { buildVascularGraph, GRAPH_HEIGHT, GRAPH_WIDTH, matchesFacility } from '../utils/vascularGraph';

const STATUS_TEXT = { available: 'Available for modeled shipment', blocked: 'Blocked in this scenario', delayed: 'Delayed', 'in-transit': 'In transit', unknown: 'Status unavailable' };
const sumValues = (record) => Object.values(record || {}).reduce((sum, value) => sum + (Number.isFinite(Number(value)) ? Number(value) : 0), 0);
const formatValue = (value, unit) => value != null && value !== '' && Number.isFinite(Number(value)) ? `${value} ${unit}` : 'Not recorded';

function FacilityIcon({ type, x, y }) {
  return type === 'bank' ? <g transform={`translate(${x} ${y})`} className="vascular-glyph" aria-hidden="true"><path d="M0-8 C-2-4-5-1-5 2a5 5 0 0 0 10 0C5-1 2-4 0-8Z"/><path d="M-2 2h4"/></g> : <g transform={`translate(${x} ${y})`} className="vascular-glyph" aria-hidden="true"><rect x="-7" y="-7" width="14" height="14" rx="3"/><path d="M0-4v8M-4 0h8"/></g>;
}

export default function VascularNetworkMap({ banks = [], hospitals = [], routes = [] }) {
  const [query, setQuery] = useState('');
  const [facilityFocus, setFacilityFocus] = useState('all');
  const [routeStatus, setRouteStatus] = useState('all');
  const [selectedFacility, setSelectedFacility] = useState('');
  const [selectedRoute, setSelectedRoute] = useState('');
  const [zoom, setZoom] = useState(1);
  const [pan, setPan] = useState({ x: 0, y: 0 });
  const dragRef = useRef(null);
  const { nodes, links, unresolved, malformed } = useMemo(() => buildVascularGraph({ banks, hospitals, routes }), [banks, hospitals, routes]);
  const facilities = useMemo(() => [...banks.map((facility) => ({ ...facility, kind: 'bank' })), ...hospitals.map((facility) => ({ ...facility, kind: 'hospital' }))], [banks, hospitals]);
  const matchingFacilities = useMemo(() => facilities.filter((facility) => matchesFacility(facility, query)), [facilities, query]);
  const visibleLinks = useMemo(() => links.filter((link) => routeStatus === 'all' || (routeStatus === 'other' ? !['available', 'blocked'].includes(link.kind) : link.kind === routeStatus)), [links, routeStatus]);
  const chosenFacility = facilities.find((facility) => String(facility.id) === selectedFacility);
  const chosenNode = nodes.find((node) => node.id === selectedFacility);
  const chosenLink = links.find((link) => link.key === selectedRoute);
  const facilityRoutes = chosenFacility ? visibleLinks.filter((link) => String(link.route.source) === String(chosenFacility.id) || String(link.route.destination) === String(chosenFacility.id)) : [];
  const selectedRouteSource = chosenLink?.source.facility;
  const selectedRouteDestination = chosenLink?.destination.facility;
  const unmatchedCount = facilities.length - matchingFacilities.length;
  const graphEmpty = nodes.length === 0;

  const chooseFacility = (facility) => {
    if (!facility) return;
    setSelectedFacility(String(facility.id));
    setSelectedRoute('');
    setQuery(facility.name || facility.id);
    const node = nodes.find((item) => item.id === String(facility.id));
    if (node) {
      const nextZoom = Math.max(zoom, 1.18);
      setZoom(nextZoom);
      setPan({ x: GRAPH_WIDTH / 2 - node.x * nextZoom, y: GRAPH_HEIGHT / 2 - node.y * nextZoom });
    }
  };
  const chooseLink = (link) => {
    setSelectedRoute(link.key);
    setSelectedFacility('');
  };
  const clearFilters = () => {
    setQuery(''); setFacilityFocus('all'); setRouteStatus('all'); setSelectedFacility(''); setSelectedRoute('');
  };
  const zoomBy = (delta) => setZoom((value) => Math.min(2.2, Math.max(0.75, Number((value + delta).toFixed(2)))));

  return <section className="vascular-workspace panel" aria-labelledby="vascular-map-title">
    <header className="vascular-heading"><div><span className="eyebrow">SYNTHETIC LOGISTICS MODEL · SCHEMATIC</span><h2 id="vascular-map-title">Supply to hospital network</h2><p>Connections show modeled scenario routes. This view is schematic, not a geographic map or live vehicle tracker.</p></div><div className="vascular-network-totals"><span><strong>{nodes.length}</strong> facilities</span><span><strong>{links.length}</strong> modeled connections</span></div></header>
    <div className="vascular-controls">
      <div className="vascular-search-wrap"><label htmlFor="vascular-search"><Search size={15}/> Search facilities</label><div className="vascular-search-input"><input id="vascular-search" aria-label="Search facilities" type="search" value={query} placeholder="Name, ID, or location code" autoComplete="off" onChange={(event) => { setQuery(event.target.value); setSelectedFacility(''); setSelectedRoute(''); }} onKeyDown={(event) => { if (event.key === 'Enter' && matchingFacilities.length) { event.preventDefault(); chooseFacility(matchingFacilities[0]); } }} /><button type="button" aria-label="Clear facility search" disabled={!query} onClick={() => { setQuery(''); setSelectedFacility(''); }}><X size={14}/></button></div>{query && !selectedFacility && <ul className="vascular-search-results" role="listbox" aria-label="Matching facilities">{matchingFacilities.slice(0, 6).map((facility) => <li key={facility.id}><button type="button" role="option" onClick={() => chooseFacility(facility)}><span>{facility.kind === 'bank' ? <Droplet size={13}/> : <Hospital size={13}/>}</span><b>{facility.name || facility.id}</b><small>{facility.location_id || facility.id}</small></button></li>)}{matchingFacilities.length === 0 && <li className="vascular-search-empty">No facility matches that search.</li>}</ul>}</div>
      <label className="vascular-select-label">Facility focus<select className="field-control" value={facilityFocus} onChange={(event) => setFacilityFocus(event.target.value)}><option value="all">All facility types</option><option value="bank">Blood banks</option><option value="hospital">Hospitals</option></select></label>
      <label className="vascular-select-label">Route status<select className="field-control" aria-label="Route status filter" value={routeStatus} onChange={(event) => { setRouteStatus(event.target.value); setSelectedRoute(''); }}><option value="all">All route statuses</option><option value="available">Available</option><option value="blocked">Blocked</option><option value="other">Unknown / other</option></select></label>
      {(query || facilityFocus !== 'all' || routeStatus !== 'all') && <button type="button" className="button button-secondary button-small vascular-clear" onClick={clearFilters}>Clear filters</button>}
    </div>
    <div className="vascular-layout">
      <div className="vascular-canvas-wrap">
        <div className="vascular-canvas-topline"><span><i className="vascular-schematic-dot"/> Scenario network · not to scale</span><div className="vascular-zoom-tools" role="group" aria-label="Network map controls"><button type="button" aria-label="Zoom out" disabled={zoom <= 0.75} onClick={() => zoomBy(-0.15)}><Minus size={14}/></button><span aria-live="polite">{Math.round(zoom * 100)}%</span><button type="button" aria-label="Zoom in" disabled={zoom >= 2.2} onClick={() => zoomBy(0.15)}><Plus size={14}/></button><button type="button" aria-label="Fit full network" onClick={() => { setZoom(1); setPan({ x: 0, y: 0 }); }}><RotateCcw size={14}/><span>Fit</span></button></div></div>
        {graphEmpty ? <div className="vascular-empty"><Building2 size={22}/><strong>No facility records in this scenario</strong><span>The API returned no blood banks or hospitals for the selected synthetic model.</span></div> : <div className="vascular-svg-scroll"><svg className="vascular-svg" viewBox={`0 0 ${GRAPH_WIDTH} ${GRAPH_HEIGHT}`} role="group" aria-labelledby="vascular-svg-title vascular-svg-description" onWheel={(event) => { event.preventDefault(); zoomBy(event.deltaY < 0 ? 0.08 : -0.08); }} onPointerDown={(event) => { if (event.target.dataset.panSurface === 'true') { event.currentTarget.setPointerCapture(event.pointerId); dragRef.current = { x: event.clientX, y: event.clientY, pan }; } }} onPointerMove={(event) => { if (!dragRef.current) return; const rect = event.currentTarget.getBoundingClientRect(); const dx = ((event.clientX - dragRef.current.x) / rect.width) * GRAPH_WIDTH / zoom; const dy = ((event.clientY - dragRef.current.y) / rect.height) * GRAPH_HEIGHT / zoom; setPan({ x: Math.max(-210, Math.min(210, dragRef.current.pan.x + dx)), y: Math.max(-130, Math.min(130, dragRef.current.pan.y + dy)) }); }} onPointerUp={() => { dragRef.current = null; }} onPointerCancel={() => { dragRef.current = null; }}>
          <title id="vascular-svg-title">Schematic blood bank and hospital route network</title><desc id="vascular-svg-description">{banks.length} blood banks on the left connect to {hospitals.length} hospitals on the right. Select a labeled node or route to inspect the synthetic scenario data. Pan by dragging open space; zoom with the controls or mouse wheel.</desc>
          <defs><pattern id="vascular-grid" width="32" height="32" patternUnits="userSpaceOnUse"><circle cx="1" cy="1" r="1" className="vascular-grid-point"/></pattern><marker id="vascular-arrow-available" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse"><path d="M 0 0 L 10 5 L 0 10 z" className="vascular-arrow available"/></marker><marker id="vascular-arrow-blocked" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse"><path d="M 0 0 L 10 5 L 0 10 z" className="vascular-arrow blocked"/></marker><marker id="vascular-arrow-warning" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse"><path d="M 0 0 L 10 5 L 0 10 z" className="vascular-arrow warning"/></marker><marker id="vascular-arrow-unknown" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse"><path d="M 0 0 L 10 5 L 0 10 z" className="vascular-arrow unknown"/></marker></defs>
          <rect width="1000" height="580" fill="url(#vascular-grid)" data-pan-surface="true" className="vascular-pan-surface"/>
          <g transform={`translate(${pan.x} ${pan.y}) scale(${zoom})`}>
            <text className="vascular-column-label" x="170" y="36" textAnchor="middle">BLOOD BANKS</text><text className="vascular-column-label" x="830" y="36" textAnchor="middle">HOSPITALS</text>
            <path className="vascular-spine" d="M 500 55 C 468 130 532 180 500 255 S 468 390 500 525"/><path className="vascular-spine-branch" d="M 500 165 C 430 155 445 112 395 104 M 500 310 C 568 328 552 380 610 395"/>
            {visibleLinks.map((link) => {
              const related = selectedFacility && (link.source.id === selectedFacility || link.destination.id === selectedFacility);
              const textMatch = !query || matchesFacility(link.source.facility, query) || matchesFacility(link.destination.facility, query);
              const dimmed = Boolean((selectedFacility && !related) || (query && !textMatch));
              const active = selectedRoute === link.key;
              return <g className={`vascular-route-group ${active ? 'is-selected' : ''} ${dimmed ? 'is-dimmed' : ''} status-${link.kind}`} key={link.key} role="button" tabIndex={0} aria-label={`${link.source.facility.name || link.source.id} to ${link.destination.facility.name || link.destination.id}. ${STATUS_TEXT[link.kind]}. Select route details.`} aria-pressed={active} onClick={() => chooseLink(link)} onKeyDown={(event) => { if (event.key === 'Enter' || event.key === ' ') { event.preventDefault(); chooseLink(link); } }}><path className="vascular-route-hit" d={link.path}/><path className="vascular-route-line" d={link.path} markerEnd={`url(#vascular-arrow-${link.kind === 'available' ? 'available' : link.kind === 'blocked' ? 'blocked' : ['delayed', 'in-transit'].includes(link.kind) ? 'warning' : 'unknown'})`}/></g>;
            })}
            {nodes.map((node) => {
              const selected = selectedFacility === node.id;
              const focused = facilityFocus === 'all' || facilityFocus === node.type;
              const searched = !query || matchesFacility(node.facility, query);
              const opacity = (focused ? 1 : 0.36) * (searched ? 1 : 0.25);
              return <g key={node.id} className={`vascular-node status-${node.type} ${selected ? 'is-selected' : ''}`} transform={`translate(${node.x} ${node.y})`} role="button" tabIndex={0} aria-label={`${node.facility.name || node.id}, ${node.type === 'bank' ? 'blood bank' : 'hospital'}, location ${node.facility.location_id || 'not recorded'}. Select facility details.`} aria-pressed={selected} style={{ opacity }} onClick={() => chooseFacility(node.facility)} onKeyDown={(event) => { if (event.key === 'Enter' || event.key === ' ') { event.preventDefault(); chooseFacility(node.facility); } }}><circle className="vascular-node-halo" r="31"/><circle className="vascular-node-body" r="22"/><FacilityIcon type={node.type} x={0} y={0}/><text className={`vascular-node-name ${node.type === 'bank' ? 'label-left' : 'label-right'}`} x={node.type === 'bank' ? -38 : 38} y="-2" textAnchor={node.type === 'bank' ? 'end' : 'start'}>{node.facility.name || node.id}</text><text className={`vascular-node-subtitle ${node.type === 'bank' ? 'label-left' : 'label-right'}`} x={node.type === 'bank' ? -38 : 38} y="14" textAnchor={node.type === 'bank' ? 'end' : 'start'}>{node.facility.location_id || node.id}</text></g>;
            })}
          </g>
        </svg></div>}
        <div className="vascular-legend" aria-label="Route status legend"><span><i className="status-line available"/>Available in scenario</span><span><i className="status-line blocked"/>Blocked in scenario</span><span><i className="status-line warning"/>Delayed / in transit</span><span><i className="status-line unknown"/>Other / unknown status</span><span><i className="status-shape bank"/>Blood bank</span><span><i className="status-shape hospital"/>Hospital</span></div>
        {unresolved.length > 0 && <div className="vascular-data-note" role="status"><CircleHelp size={14}/><span>{unresolved.length} route record{unresolved.length === 1 ? '' : 's'} point to a facility absent from this scenario; those connections are not drawn: {unresolved.map((item) => `${item.source} → ${item.destination}`).join(', ')}.</span></div>}
        {malformed.length > 0 && <div className="vascular-data-note" role="status"><CircleHelp size={14}/><span>{malformed.length} route record{malformed.length === 1 ? '' : 's'} lack a source or destination and cannot be shown.</span></div>}
      </div>
      <aside className="vascular-inspector" aria-live="polite" aria-label="Selected network details">
        {chosenFacility ? <><div className="vascular-inspector-header"><span className={`vascular-detail-icon ${chosenNode?.type || 'unknown'}`}>{chosenNode?.type === 'bank' ? <Droplet size={16}/> : <Hospital size={16}/>}</span><div><span className="eyebrow">{chosenNode?.type === 'bank' ? 'SUPPLY FACILITY' : 'DEMAND FACILITY'}</span><h3>{chosenFacility.name || chosenFacility.id}</h3></div></div><dl className="vascular-detail-list"><div><dt>Facility ID</dt><dd>{chosenFacility.id}</dd></div><div><dt>Location code</dt><dd>{chosenFacility.location_id || 'Not recorded'}</dd></div>{chosenNode?.type === 'bank' ? <><div><dt>Total inventory</dt><dd>{sumValues(chosenFacility.inventory)} units</dd></div><div><dt>Blood groups</dt><dd>{Object.keys(chosenFacility.inventory || {}).length ? Object.entries(chosenFacility.inventory).map(([group, amount]) => `${group}: ${amount}`).join(' · ') : 'Not recorded'}</dd></div></> : <><div><dt>Total demand</dt><dd>{sumValues(chosenFacility.demand)} units</dd></div><div><dt>Blood groups</dt><dd>{Object.keys(chosenFacility.demand || {}).length ? Object.entries(chosenFacility.demand).map(([group, amount]) => `${group}: ${amount}`).join(' · ') : 'Not recorded'}</dd></div><div><dt>Urgency tags</dt><dd>{Object.values(chosenFacility.urgency || {}).map((urgency) => urgency?.category).filter(Boolean).join(', ') || 'None recorded'}</dd></div></>}</dl><div className="vascular-connected"><h4>Connected routes <span>{facilityRoutes.length}</span></h4>{facilityRoutes.map((link) => <button type="button" key={link.key} onClick={() => chooseLink(link)}><span>{link.source.facility.name || link.source.id} <ArrowRight size={11}/> {link.destination.facility.name || link.destination.id}</span><b className={`route-status-text ${link.kind}`}>{link.kind === 'available' ? 'Available' : link.kind === 'blocked' ? 'Blocked' : 'Unknown'}</b></button>)}{facilityRoutes.length === 0 && <p>No route relationships are recorded for this facility.</p>}</div></> : chosenLink ? <><div className="vascular-inspector-header"><span className="vascular-detail-icon route"><ArrowDownRight size={16}/></span><div><span className="eyebrow">MODELED CONNECTION</span><h3>Route details</h3></div></div><p className="vascular-route-endpoint">{selectedRouteSource?.name || chosenLink.route.source}<ArrowRight size={14}/>{selectedRouteDestination?.name || chosenLink.route.destination}</p><dl className="vascular-detail-list"><div><dt>Scenario status</dt><dd className={`route-status-text ${chosenLink.kind}`}>{STATUS_TEXT[chosenLink.kind]}</dd></div><div><dt>Source facility</dt><dd>{chosenLink.route.source}</dd></div><div><dt>Destination</dt><dd>{chosenLink.route.destination}</dd></div><div><dt>Modeled travel time</dt><dd>{formatValue(chosenLink.route.travel_time_minutes, 'min')}</dd></div><div><dt>Modeled distance</dt><dd>{formatValue(chosenLink.route.distance_km, 'km')}</dd></div><div><dt>Transport cost</dt><dd>{formatValue(chosenLink.route.transport_cost, 'points')}</dd></div></dl><p className="vascular-route-note">These are scenario parameters, not live navigation directions or a delivery ETA.</p></> : <div className="vascular-inspector-empty"><Activity size={20}/><strong>Explore the network</strong><p>Select a facility to review its scenario inventory or demand, or choose a route to inspect its modeled status and constraints.</p><span>{matchingFacilities.length} matching facilities · {visibleLinks.length} visible routes{unmatchedCount ? ` · ${unmatchedCount} outside the current search` : ''}</span></div>}
      </aside>
    </div>
    <details className="vascular-accessible-list"><summary>Browse facilities and routes as a list</summary><div className="vascular-accessible-columns"><section><h3>Facilities</h3><ul>{facilities.map((facility) => <li key={facility.id}><button type="button" onClick={() => chooseFacility(facility)}>{facility.name || facility.id} <small>{facility.kind === 'bank' ? 'Blood bank' : 'Hospital'} · {facility.location_id || 'location not recorded'}</small></button></li>)}</ul></section><section><h3>Modeled routes</h3><ul>{links.map((link) => <li key={link.key}><button type="button" onClick={() => chooseLink(link)}>{link.source.facility.name || link.source.id} to {link.destination.facility.name || link.destination.id} <small>{STATUS_TEXT[link.kind]}</small></button></li>)}</ul></section></div></details>
  </section>;
}
