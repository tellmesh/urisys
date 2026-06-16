# UriImplementation: uribrowser-python

```yaml markpact:implementation
apiVersion: urisys.io/v1
kind: UriImplementation
metadata:
  id: uribrowser-python
  version: 0.1.0
  language: python
  platform: any
implements:
  contract: uribrowser.contract
  version: ^1.0.0
runtime:
  type: python
  service:
    command: urisys-browser serve --port 8792
capabilities:
  - contract_command: browser.page.open
    handler: python://uribrowserdocker.handlers:open_page
  - contract_query: browser.page.dom
    handler: python://uribrowserdocker.handlers:get_dom
  - contract_command: browser.page.screenshot
    handler: python://uribrowserdocker.handlers:screenshot
  - contract_query: browser.status
    handler: python://uribrowserdocker.handlers:status
supports:
  drivers: [mock, system-open, playwright, remote-cdp]
```
