import { PolicyDeniedError } from './errors.js';

export class PolicyGate {
  constructor(defaults = {}) {
    this.defaults = {
      requireApprovalForSideEffects: true,
      allowSchemes: null,
      denySchemes: [],
      ...defaults,
    };
  }

  check(route, payload = {}, context = {}) {
    const policy = { ...this.defaults, ...(route.policy || {}) };

    if (policy.allowSchemes && !policy.allowSchemes.includes(route.scheme)) {
      throw new PolicyDeniedError(`Scheme not allowed: ${route.scheme}`, {
        scheme: route.scheme,
        uri: route.uri,
      });
    }

    if (policy.denySchemes?.includes(route.scheme)) {
      throw new PolicyDeniedError(`Scheme denied: ${route.scheme}`, {
        scheme: route.scheme,
        uri: route.uri,
      });
    }

    const approvalRequired =
      route.approval === 'required' ||
      (policy.requireApprovalForSideEffects && route.side_effects);

    if (approvalRequired && !context.approved) {
      throw new PolicyDeniedError('Approval required for side-effecting URI command.', {
        uri: route.uri,
        operation: route.operation,
        side_effects: route.side_effects,
      });
    }

    return { allowed: true, approval_required: approvalRequired };
  }
}
