# UriContract: uriocr

```yaml markpact:contract
apiVersion: urisys.io/v1
kind: UriContract
metadata:
  id: uriocr.contract
  version: 0.1.0
scheme: ocr
queries:
  - id: ocr.latest_text
    pattern: ocr://{target}/image/latest/query/text
```
