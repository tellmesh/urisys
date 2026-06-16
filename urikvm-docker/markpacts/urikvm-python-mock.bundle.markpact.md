# UriBundle: KVM mock stack

```yaml markpact:bundle
apiVersion: urisys.io/v1
kind: UriBundle
metadata:
  id: urikvm-python-mock.bundle
  version: 0.1.0
imports:
  contracts:
    - ./urikvm.contract.markpact.md
    - ./urihim.contract.markpact.md
    - ./uriocr.contract.markpact.md
    - ./urillm-vision.contract.markpact.md
runtime:
  command: urisys-kvm serve --port 8794
routes:
  - match: kvm://local/**
    target: local://python-runtime
  - match: him://local/**
    target: local://python-runtime
  - match: ocr://local/**
    target: local://python-runtime
  - match: llm://local/**
    target: local://python-runtime
```
