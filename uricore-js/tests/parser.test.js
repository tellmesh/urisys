import test from 'node:test';
import assert from 'node:assert/strict';
import { parseUri, templateToRegex } from '../src/index.js';

test('parse URI', () => {
  const parsed = parseUri('browser://default/page/open?wait=true#x');
  assert.equal(parsed.scheme, 'browser');
  assert.equal(parsed.authority, 'default');
  assert.deepEqual(parsed.segments, ['page', 'open']);
  assert.equal(parsed.query.wait, 'true');
  assert.equal(parsed.fragment, 'x');
});

test('template regex captures params', () => {
  const { regex } = templateToRegex('page://state/{key}/command/{action}');
  const match = regex.exec('page://state/counter/command/increment');
  assert.equal(match.groups.key, 'counter');
  assert.equal(match.groups.action, 'increment');
});
