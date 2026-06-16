// Optional gRPC adapter skeleton. Requires: npm install @grpc/grpc-js @grpc/proto-loader
// It intentionally wraps the same runtime.call(uri, payload, context) contract as HTTP/WS/SSE.
export async function createGrpcUriServer({ runtime, protoPath, packageName = 'uricore.v1', serviceName = 'UriControl' }) {
  const grpc = await import('@grpc/grpc-js');
  const protoLoader = await import('@grpc/proto-loader');

  const definition = protoLoader.loadSync(protoPath, {
    keepCase: true,
    longs: String,
    enums: String,
    defaults: true,
    oneofs: true,
  });
  const loaded = grpc.loadPackageDefinition(definition);
  const service = packageName.split('.').reduce((acc, key) => acc[key], loaded)[serviceName].service;

  const server = new grpc.Server();
  server.addService(service, {
    Call: async (call, callback) => {
      try {
        const payload = call.request.payload_json ? JSON.parse(call.request.payload_json) : {};
        const context = call.request.context_json ? JSON.parse(call.request.context_json) : {};
        const result = await runtime.call(call.request.uri, payload, context);
        callback(null, {
          ok: result.ok,
          uri: result.uri,
          result_json: JSON.stringify(result.result ?? {}),
          event_json: JSON.stringify(result.event ?? {}),
          error_json: JSON.stringify(result.error ?? {}),
        });
      } catch (error) {
        callback(error);
      }
    },
  });
  return { grpc, server };
}
