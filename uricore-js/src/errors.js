export class UriCoreError extends Error {
  constructor(message, details = {}) {
    super(message);
    this.name = this.constructor.name;
    this.details = details;
  }
}

export class UriParseError extends UriCoreError {}
export class RouteNotFoundError extends UriCoreError {}
export class PolicyDeniedError extends UriCoreError {}
export class HandlerNotFoundError extends UriCoreError {}
export class HandlerExecutionError extends UriCoreError {}
