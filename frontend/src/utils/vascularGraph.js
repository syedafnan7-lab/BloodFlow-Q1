export const GRAPH_WIDTH = 1000;
export const GRAPH_HEIGHT = 580;

export function routeStatusKind(status) {
  if (status === 'available') return 'available';
  if (status === 'blocked') return 'blocked';
  if (typeof status === 'string' && /delay/i.test(status)) return 'delayed';
  if (typeof status === 'string' && /transit/i.test(status)) return 'in-transit';
  return 'unknown';
}

function nodeY(index, count) {
  if (count <= 1) return GRAPH_HEIGHT / 2;
  const usable = GRAPH_HEIGHT - 190;
  return 95 + (index * usable) / (count - 1);
}

export function buildVascularGraph({ banks = [], hospitals = [], routes = [] } = {}) {
  const validBanks = banks.filter((bank) => bank?.id);
  const validHospitals = hospitals.filter((hospital) => hospital?.id);
  const nodes = [
    ...validBanks.map((facility, index) => ({ facility, id: String(facility.id), type: 'bank', x: 170, y: nodeY(index, validBanks.length) })),
    ...validHospitals.map((facility, index) => ({ facility, id: String(facility.id), type: 'hospital', x: 830, y: nodeY(index, validHospitals.length) })),
  ];
  const nodeById = new Map(nodes.map((node) => [node.id, node]));
  const validRoutes = routes.filter((route) => route?.source && route?.destination);
  const links = validRoutes.flatMap((route, index) => {
    const source = nodeById.get(String(route.source));
    const destination = nodeById.get(String(route.destination));
    if (!source || !destination) return [];
    const bend = ((index % 3) - 1) * 22;
    return [{ route, index, source, destination, key: `${route.source}|${route.destination}`, kind: routeStatusKind(route.status), path: `M ${source.x + 30} ${source.y} C ${GRAPH_WIDTH / 2 - 95} ${source.y + bend}, ${GRAPH_WIDTH / 2 + 95} ${destination.y - bend}, ${destination.x - 30} ${destination.y}` }];
  });
  const unresolved = validRoutes.filter((route) => !nodeById.has(String(route.source)) || !nodeById.has(String(route.destination)));
  const malformed = routes.filter((route) => !route?.source || !route?.destination);
  return { nodes, links, unresolved, malformed };
}

export function matchesFacility(facility, query = '') {
  const needle = query.trim().toLocaleLowerCase();
  if (!needle) return true;
  return [facility?.name, facility?.id, facility?.location_id]
    .filter((value) => value != null)
    .some((value) => String(value).toLocaleLowerCase().includes(needle));
}
