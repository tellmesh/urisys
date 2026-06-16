# UriContract: urillm vision

```yaml markpact:contract
apiVersion: urisys.io/v1
kind: UriContract
metadata:
  id: urillm-vision.contract
  version: 0.1.0
scheme: llm
queries:
  - id: llm.vision.analyze
    pattern: llm://{target}/vision/query/analyze
```
