# UriBundle: RDP Linux GUI + KVM/HIM/OCR/LLM

This bundle describes a Docker Linux GUI instance exposed over RDP and automated through KVM URI calls.

```yaml markpact:bundle
apiVersion: urisys.io/v1
kind: UriBundle
metadata:
  id: urirdp-kvm-docker.bundle
  version: 0.1.0
imports:
  contracts:
    - ./urirdp.contract.markpact.md
    - ./urikvm.contract.markpact.md
    - ./urihim.contract.markpact.md
    - ./uriocr.contract.markpact.md
    - ./urillm-vision.contract.markpact.md
runtime:
  docker:
    compose: ../docker-compose.yml
    service: urirdp
ports:
  rdp: 3389
  uri: 8795
routes:
  - match: rdp://local/**
    target: local://container
  - match: kvm://local/**
    target: local://container
  - match: him://local/**
    target: local://container
  - match: ocr://local/**
    target: local://container
  - match: llm://local/**
    target: local://container
```
