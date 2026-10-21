import test from 'node:test';
import assert from 'node:assert/strict';
import { formatDashboardCount, getDashboardAccessState } from '../src/utils/dashboardAccess.js';
import { getDashboardMetrics } from '../src/services/donorNetwork.js';

test('distinguishes configuration, sign-in, admin denial, and query failures', () => {
  assert.equal(getDashboardAccessState({ configured: false }).key, 'not_configured');
  assert.equal(getDashboardAccessState({ configured: true }).key, 'sign_in_required');
  assert.equal(getDashboardAccessState({ configured: true, session: {}, error: { code: '42501' } }).key, 'admin_required');
  assert.equal(getDashboardAccessState({ configured: true, session: {}, error: { code: '08006' } }).key, 'database_error');
});

test('keeps true zero separate from missing or invalid counts', () => {
  assert.equal(formatDashboardCount({ count: 0 }, 'count', 'Sign in'), '0');
  assert.equal(formatDashboardCount({}, 'count', 'Sign in'), 'Sign in');
  assert.equal(formatDashboardCount({ count: -1 }, 'count', 'Sign in'), 'Sign in');
});

test('preserves database authorization error codes for access-state mapping', async () => {
  const client = { rpc: async () => ({ data: null, error: { code: '42501', message: 'permission denied' } }) };
  await assert.rejects(getDashboardMetrics(client), (error) => error.code === '42501');
});
