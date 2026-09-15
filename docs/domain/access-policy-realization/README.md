# Access Policy Realization domain

Current authority:

- `tactical-model.md` — source-neutral comparison, delta and verified additive change intent;
- `../../requirements/policy-realization-reconciliation-g1.md` — observable comparison/convergence behavior;
- `../../requirements/access-policy-realization-mvp.md` — APR-specific behavior contract.

Core semantic rule for complete comparable inputs:

```text
common  = required ∩ configured
missing = required - configured
excess  = configured - required
```

`Realized` requires both missing and excess to be empty. Incomplete, mismatched or unsupported input is `Uncomparable`, not drift. Current automated change design is additive `ENSURE-PERMIT` for missing access; excess remains evidence only.

APR does not parse provider-native policy, select enforcement targets, render provider configuration or execute device mutation.
