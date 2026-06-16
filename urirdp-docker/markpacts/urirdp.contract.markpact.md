# UriContract: urirdp

```yaml markpact:contract
apiVersion: urisys.io/v1
kind: UriContract
metadata:
  id: urirdp.contract
  version: 0.1.0
scheme: rdp
queries:
  - id: rdp.session.status
    pattern: rdp://{target}/session/query/status
    output:
      type: object
  - id: rdp.session.display
    pattern: rdp://{target}/session/query/display
    output:
      type: object
```
