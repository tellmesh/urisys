import { UriParseError } from './errors.js';

export function parseUri(value) {
  if (typeof value !== 'string' || !value.trim()) {
    throw new UriParseError('URI must be a non-empty string.', { value });
  }

  const raw = value.trim();
  const schemeMatch = raw.match(/^([a-zA-Z][a-zA-Z0-9+.-]*):\/\//);
  if (!schemeMatch) {
    throw new UriParseError('URI must start with scheme://', { value: raw });
  }

  const scheme = schemeMatch[1];
  const rest = raw.slice(schemeMatch[0].length);
  const [beforeFragment, fragment = ''] = rest.split('#', 2);
  const [beforeQuery, queryString = ''] = beforeFragment.split('?', 2);
  const slashIndex = beforeQuery.indexOf('/');

  const authority = slashIndex === -1 ? beforeQuery : beforeQuery.slice(0, slashIndex);
  const path = slashIndex === -1 ? '' : beforeQuery.slice(slashIndex + 1);
  const segments = path.split('/').filter(Boolean).map(decodeURIComponent);
  const query = Object.fromEntries(new URLSearchParams(queryString));

  return {
    raw,
    scheme,
    authority: decodeURIComponent(authority || ''),
    path,
    segments,
    query,
    fragment,
  };
}

export function uriKindFromSegments(parsed) {
  const words = new Set(parsed.segments.concat(Object.keys(parsed.query)));
  if (words.has('command')) return 'command';
  if (words.has('query')) return 'query';
  if (words.has('event')) return 'event';
  if (words.has('view')) return 'view';
  return 'unknown';
}

export function normalizeUri(value) {
  const parsed = parseUri(value);
  const path = parsed.segments.map(encodeURIComponent).join('/');
  const query = new URLSearchParams(parsed.query).toString();
  return `${parsed.scheme}://${encodeURIComponent(parsed.authority)}${path ? `/${path}` : ''}${query ? `?${query}` : ''}${parsed.fragment ? `#${parsed.fragment}` : ''}`;
}
