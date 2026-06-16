export const manifest = {
  id: 'uridom-js',
  version: 1,
  scheme: 'dom',
  description: 'Browser DOM control pack for URI-driven pages.',
  uri_patterns: [
    { pattern: 'dom://element/{selector}/query/text', kind: 'query', operation: 'getText', side_effects: false, approval: 'not_required' },
    { pattern: 'dom://element/{selector}/command/set-text', kind: 'command', operation: 'setText', side_effects: true, approval: 'not_required' },
    { pattern: 'dom://element/{selector}/command/add-class', kind: 'command', operation: 'addClass', side_effects: true, approval: 'not_required' },
    { pattern: 'dom://element/{selector}/command/click', kind: 'command', operation: 'clickElement', side_effects: true, approval: 'required' }
  ]
};

function decodeSelector(value) {
  return decodeURIComponent(String(value || '')).replace(/^#/, '#');
}

function findElement(context) {
  const selector = decodeSelector(context.params.selector);
  const el = document.querySelector(selector);
  if (!el) throw new Error(`DOM element not found: ${selector}`);
  return { selector, el };
}

export const handlers = {
  getText(payload, context) {
    const { selector, el } = findElement(context);
    return { selector, text: el.textContent || '' };
  },
  setText(payload, context) {
    const { selector, el } = findElement(context);
    el.textContent = String(payload.text ?? payload.value ?? '');
    return { selector, text: el.textContent };
  },
  addClass(payload, context) {
    const { selector, el } = findElement(context);
    const className = String(payload.className ?? payload.class ?? 'active');
    el.classList.add(className);
    return { selector, className, classes: [...el.classList] };
  },
  clickElement(payload, context) {
    const { selector, el } = findElement(context);
    el.click();
    return { selector, clicked: true };
  }
};

export function register(registry) {
  registry.loadManifest(manifest, handlers);
  return registry;
}
