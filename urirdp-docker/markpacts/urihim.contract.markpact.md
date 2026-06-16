# UriContract: urihim

```yaml markpact:contract
apiVersion: urisys.io/v1
kind: UriContract
metadata:
  id: urihim.contract
  version: 0.1.0
scheme: him
commands:
  - id: him.mouse.click
    pattern: him://{target}/mouse/command/click
    side_effects: true
    requires_approval: true
  - id: him.keyboard.type
    pattern: him://{target}/keyboard/command/type
    side_effects: true
    requires_approval: true
```
