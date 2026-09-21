import { useEffect, useState } from "react";
import { ApiError, type PolicyRuleView, api } from "../../app/api";
import { navigate } from "../../app/router";
import {
  EmptyState,
  PageHeader,
  ProvenancePanel,
  StatusBanner,
  VersionedEditor,
} from "../../design-system/components";

const errorKind = (error: unknown) =>
  error instanceof ApiError ? error.kind : "technical";

export function PolicyRuleScreens({ ruleRef }: { ruleRef?: string }) {
  const [items, setItems] = useState<PolicyRuleView[]>([]);
  const [selected, setSelected] = useState<PolicyRuleView | null>(null);
  const [state, setState] = useState("loading");

  useEffect(() => {
    const load = ruleRef ? api.getPolicyRule(ruleRef) : api.listPolicyRules();
    void load
      .then((value) => {
        if (Array.isArray(value)) setItems(value);
        else setSelected(value);
        setState("loaded");
      })
      .catch((error) => setState(errorKind(error)));
  }, [ruleRef]);

  async function toggleState() {
    if (!selected) return;
    setState("submitting");
    try {
      const next = selected.effectState === "ACTIVE" ? "INACTIVE" : "ACTIVE";
      await api.setPolicyRuleState(selected.policyRuleRef, selected.version, next);
      const value = await api.getPolicyRule(selected.policyRuleRef);
      setSelected(value);
      setState("loaded");
    } catch (error) {
      setState(errorKind(error));
    }
  }

  return (
    <>
      <PageHeader eyebrow="Desired access" title="Policy Rules" />
      {state === "loading" && <StatusBanner>Loading Policy Rules…</StatusBanner>}
      {!ruleRef && items.length === 0 && state !== "loading" && (
        <EmptyState>No Policy Rules.</EmptyState>
      )}
      {!ruleRef && (
        <section className="panel">
          {items.map((item) => (
            <button
              type="button"
              key={item.policyRuleRef}
              onClick={() => navigate(`/policy-rules/${item.policyRuleRef}`)}
            >
              {item.policyRuleRef} · {item.effectState}
            </button>
          ))}
          <button
            type="button"
            onClick={() => navigate("/policy-materializations/new")}
          >
            Export Effective Policy
          </button>
        </section>
      )}
      {selected && (
        <>
          <VersionedEditor version={selected.version}>
            <h3>{selected.policyRuleRef}</h3>
            <p>
              {selected.effectState} · {selected.sourceDeploymentRef} →{" "}
              {selected.destinationDeploymentRef}
            </p>
            <p>Interaction revision: {selected.interactionRevisionRef}</p>
            <button type="button" onClick={() => void toggleState()}>
              Set {selected.effectState === "ACTIVE" ? "Inactive" : "Active"}
            </button>
          </VersionedEditor>
          <ProvenancePanel>
            <h3>Authorization evidence</h3>
            <pre>{JSON.stringify(selected.authorizationEvidence, null, 2)}</pre>
            <h3>Justifications</h3>
            <pre>{JSON.stringify(selected.justifications, null, 2)}</pre>
            <h3>Operational history</h3>
            <pre>{JSON.stringify(selected.operationalHistory, null, 2)}</pre>
          </ProvenancePanel>
        </>
      )}
      {!["loading", "loaded", "submitting"].includes(state) && (
        <StatusBanner kind={state === "conflict" ? "warning" : "failed"}>
          Policy rule operation: {state}.
        </StatusBanner>
      )}
    </>
  );
}
