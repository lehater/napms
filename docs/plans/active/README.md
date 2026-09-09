# Active execution

Current: `I21 — Configuration Rendering`, selected on branch `i21-configuration-rendering`.

Active plan: `docs/plans/active/PLAN-I21-configuration-rendering.md`.

Current stage: `S5 — Final gate and absorption`.

I20 Desired-vs-Configured Reconciliation and Enforcement Policy Derivation is complete and absorbed into canonical truth.

I21 S1-S4 are implemented on the branch. Accepted semantics: Configuration Rendering remains inside Access Policy Realization; the first target is Cisco Secure Firewall ASA CLI extended ACL; rendered configuration is derived on demand; exact semantic equivalence is required; failed rendering exposes no partial artifact.

Implemented proof: existing PostgreSQL APR composition derives `DesiredEnforcementPolicy`, renders it through the Cisco ASA adapter, independently projects rendered Permit statements back into normalized technical regions, requires exact equality, preserves rule/interaction/placement provenance and verifies no Access Rule/NEP/TAE owner state is mutated by derive+render.

Next: hosted PR final gate. On green, absorb I21 into engineering/roadmap truth, remove the completed active PLAN, set active execution to none and promote I22 without selecting it.

I22 Network Environment Operations remains downstream and must not be pulled into I21.