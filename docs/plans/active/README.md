# Active execution

Current: `I21 — Configuration Rendering`, selected on branch `i21-configuration-rendering`.

Active plan: `docs/plans/active/PLAN-I21-configuration-rendering.md`.

Current stage: `S4 — Provenance/composition proof`.

I20 Desired-vs-Configured Reconciliation and Enforcement Policy Derivation is complete and absorbed into canonical truth.

I21 S1 is accepted: Configuration Rendering remains inside Access Policy Realization; the first target is Cisco Secure Firewall ASA CLI extended ACL; rendered configuration is derived on demand; exact semantic equivalence is required; failed rendering exposes no partial artifact.

S2/S3 are implemented on the branch: framework-free render contracts/use case, Cisco ASA renderer, independent semantic projector and exact/fail-closed tests. Hosted CI remains the executable gate because this connector environment cannot run the repository locally.

Next: compose existing I20 desired derivation into I21 rendering and prove provenance/no-side-effects, then final PR gate and absorption.

I22 Network Environment Operations remains downstream and must not be pulled into I21.