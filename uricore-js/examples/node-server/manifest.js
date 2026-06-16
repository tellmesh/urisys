export const nodeManifest = {
  id: 'node-pack',
  version: 1,
  scheme: 'node',
  description: 'Node.js URI service pack.',
  uri_patterns: [
    {
      pattern: 'node://counter/query/get',
      kind: 'query',
      operation: 'get_counter',
      handler: 'get_counter',
      side_effects: false,
    },
    {
      pattern: 'node://counter/command/increment',
      kind: 'command',
      operation: 'increment_counter',
      handler: 'increment_counter',
      side_effects: true,
      approval: 'required',
    },
    {
      pattern: 'node://python/math/add',
      kind: 'command',
      operation: 'python_math_add',
      handler: 'python_math_add',
      side_effects: false,
      approval: 'not_required',
    },
  ],
};
