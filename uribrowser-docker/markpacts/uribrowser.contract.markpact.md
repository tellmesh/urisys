# UriContract: uribrowser

```yaml markpact:contract
apiVersion: urisys.io/v1
kind: UriContract
metadata:
  id: uribrowser.contract
  version: 1.0.0
scheme: browser
commands:
  - id: browser.page.open
    pattern: browser://{session}/page/command/open
    input:
      type: object
      required: [url]
    side_effects: true
    requires_approval: true
  - id: browser.page.screenshot
    pattern: browser://{session}/page/command/screenshot
    side_effects: true
    requires_approval: true
queries:
  - id: browser.status
    pattern: browser://{session}/query/status
  - id: browser.page.dom
    pattern: browser://{session}/page/query/dom
events:
  - browser.page.open.completed
  - browser.page.screenshot.completed
```
