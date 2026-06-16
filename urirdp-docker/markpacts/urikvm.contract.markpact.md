# UriContract: urikvm

```yaml markpact:contract
apiVersion: urisys.io/v1
kind: UriContract
metadata:
  id: urikvm.contract
  version: 0.1.0
scheme: kvm
queries:
  - id: kvm.display.info
    pattern: kvm://{target}/display/query/info
  - id: kvm.screenshot
    pattern: kvm://{target}/monitor/{monitor}/query/screenshot
commands:
  - id: kvm.click_text
    pattern: kvm://{target}/task/command/click-text
    side_effects: true
    requires_approval: true
  - id: kvm.type_text
    pattern: kvm://{target}/task/command/type-text
    side_effects: true
    requires_approval: true
```
