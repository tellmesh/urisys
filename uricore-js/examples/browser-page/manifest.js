export const pageManifest = {
  id: 'page-pack',
  version: 1,
  scheme: 'page',
  description: 'Controls state and DOM inside one browser page.',
  uri_patterns: [
    {
      pattern: 'page://state/{key}/query/get',
      kind: 'query',
      operation: 'get_state',
      handler: 'get_state',
      side_effects: false,
    },
    {
      pattern: 'page://state/{key}/command/set',
      kind: 'command',
      operation: 'set_state',
      handler: 'set_state',
      side_effects: true,
      approval: 'not_required',
    },
    {
      pattern: 'page://state/{key}/command/increment',
      kind: 'command',
      operation: 'increment_state',
      handler: 'increment_state',
      side_effects: true,
      approval: 'not_required',
    },
    {
      pattern: 'page://dom/title/command/set',
      kind: 'command',
      operation: 'set_title',
      handler: 'set_title',
      side_effects: true,
      approval: 'not_required',
    },
  ],
};
