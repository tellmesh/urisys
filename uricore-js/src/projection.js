export function projectLatestBySource(events) {
  const result = new Map();
  for (const event of events) {
    if (event.source_uri) result.set(event.source_uri, event);
  }
  return Object.fromEntries(result.entries());
}

export function projectOperationCounts(events) {
  const counts = {};
  for (const event of events) {
    const key = event.operation || event.event_type || 'unknown';
    counts[key] = (counts[key] || 0) + 1;
  }
  return counts;
}

export function projectFailures(events) {
  return events.filter((event) => String(event.event_type || '').toLowerCase().includes('failed'));
}
