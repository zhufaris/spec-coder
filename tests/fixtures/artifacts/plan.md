# Example plan
<!-- spec-coder:artifact-v1 plan -->
## Wave W1: `T1`
### - [ ] T1: Check documents
| Field | Content |
| --- | --- |
| Spec references | SCN-1, INV-1, ARCH-1 |
| Dependencies | None |
| Delegation mode | Default direct worker |
| Mutation ownership | scripts/check.py |
| Concurrency conflicts | None |
| Acceptance criteria and verification | Invoke CLI on valid and invalid documents and assert exit codes. |
