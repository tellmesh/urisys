export { manifest as domManifest, handlers as domHandlers, register as registerDom } from '../../uridom-js/src/index.js';
export { manifest as pageManifest, handlers as pageHandlers, register as registerPage } from '../../uripage-js/src/index.js';

export function registerBrowserPage(registry) {
  // This file is an umbrella package for browser-side URI control. Importing from local workspace paths keeps demos dependency-free.
  throw new Error('Use registerDom(registry) and registerPage(registry), or install the packages and import them directly.');
}
