import test from 'node:test';
import assert from 'node:assert/strict';
import { buildVascularGraph, matchesFacility, routeStatusKind } from '../src/utils/vascularGraph.js';
import { readFileSync } from 'node:fs';

const networkSource = readFileSync(new URL('../src/components/VascularNetworkMap.jsx', import.meta.url), 'utf8');
const networkPage = readFileSync(new URL('../src/pages/Network.jsx', import.meta.url), 'utf8');
const stylesheet = readFileSync(new URL('../src/styles.css', import.meta.url), 'utf8');

test('schematic graph uses only facility records and their modeled relationships', () => {
  const graph = buildVascularGraph({
    banks: [{ id: 'bank-a', name: 'North Bank', location_id: 'LOC-1' }],
    hospitals: [{ id: 'hospital-a', name: 'Central Hospital', location_id: 'LOC-2' }],
    routes: [{ source: 'bank-a', destination: 'hospital-a', status: 'available', distance_km: 8 }],
  });
  assert.equal(graph.nodes.length, 2);
  assert.equal(graph.links.length, 1);
  assert.equal(graph.links[0].source.id, 'bank-a');
  assert.equal(graph.links[0].destination.id, 'hospital-a');
  assert.match(graph.links[0].path, /^M 200 /);
  assert.deepEqual([graph.unresolved.length, graph.malformed.length], [0, 0]);
});

test('facility positions are stable and remain within the schematic canvas', () => {
  const data = { banks: [{ id: 'b1' }, { id: 'b2' }], hospitals: [{ id: 'h1' }, { id: 'h2' }], routes: [] };
  const one = buildVascularGraph(data);
  const two = buildVascularGraph(data);
  assert.deepEqual(one.nodes, two.nodes);
  assert.ok(one.nodes.every((node) => node.x > 0 && node.x < 1000 && node.y > 0 && node.y < 580));
});

test('unknown or incomplete route relationships are surfaced, not drawn against invented facilities', () => {
  const graph = buildVascularGraph({ banks: [{ id: 'b1' }], hospitals: [], routes: [
    { source: 'b1', destination: 'missing-hospital', status: 'open' },
    { source: 'b1', status: 'available' },
  ] });
  assert.equal(graph.links.length, 0);
  assert.equal(graph.unresolved.length, 1);
  assert.equal(graph.malformed.length, 1);
  assert.equal(routeStatusKind('open'), 'unknown');
  assert.equal(routeStatusKind('delayed'), 'delayed');
  assert.equal(routeStatusKind('in_transit'), 'in-transit');
});

test('facility search uses only recorded names, IDs, and location codes', () => {
  const facility = { name: 'Central Hospital', id: 'hospital-1', location_id: 'LOC-20' };
  assert.equal(matchesFacility(facility, 'central'), true);
  assert.equal(matchesFacility(facility, 'hospital-1'), true);
  assert.equal(matchesFacility(facility, 'loc-20'), true);
  assert.equal(matchesFacility(facility, 'nonexistent place'), false);
  assert.equal(matchesFacility(facility, ''), true);
});

test('network UI exposes keyboard-selected facilities/routes and operable search, filters and navigation controls', () => {
  assert.match(networkPage, /api\.getScenario/);
  assert.match(networkPage, /data\?\.synthetic === true/);
  assert.match(networkSource, /aria-label="Search facilities"/);
  assert.match(networkSource, /aria-label="Route status/);
  assert.match(networkSource, /aria-label="Zoom in"/);
  assert.match(networkSource, /aria-label="Zoom out"/);
  assert.match(networkSource, /aria-label="Fit full network"/);
  assert.match(networkSource, /onPointerMove/);
  assert.match(stylesheet, /@media\(prefers-reduced-motion:reduce\) \{ \.vascular-route-line,\.vascular-node/);
  assert.match(networkSource, /Browse facilities and routes as a list/);
});
