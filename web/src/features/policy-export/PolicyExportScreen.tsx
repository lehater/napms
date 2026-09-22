import { useState } from "react";
import { ApiError, api, type PolicyMaterializationResult } from "../../app/api";
import {
  EmptyState,
  FormSection,
  PageHeader,
  ProvenancePanel,
  ReferenceField,
  StatusBanner,
} from "../../design-system/components";

const errorKind = (error: unknown) =>
  error instanceof ApiError ? error.kind : "technical";

export function PolicyExportScreen() {
  const [refs, setRefs] = useState("");
  const [state, setState] = useState("editing");
  const [result, setResult] = useState<PolicyMaterializationResult | null>(
    null,
  );

  async function submit(event: React.FormEvent) {
    event.preventDefault();
    setState("submitting");
    try {
      const selected = refs
        .split(",")
        .map((value) => value.trim())
        .filter(Boolean);
      const value = await api.materialize(
        selected.length ? selected : undefined,
      );
      setResult(value);
      setState("complete");
    } catch (error) {
      setState(errorKind(error));
    }
  }

  return (
    <>
      <PageHeader eyebrow="Policy materialization" title="Policy Export" />
      <FormSection onSubmit={submit}>
        <ReferenceField
          label="Policy Rule IDs (comma separated; empty means current effective policy)"
          value={refs}
          onChange={setRefs}
        />
        <button type="submit" disabled={state === "submitting"}>
          Execute Export
        </button>
      </FormSection>
      {result && (
        <>
          <StatusBanner
            kind={result.status === "UNRESOLVED" ? "blocked" : "success"}
          >
            Export result: {result.status}
          </StatusBanner>
          <p>Evaluated at {result.evaluationAt}</p>
          {result.status === "UNRESOLVED" && result.issues.length > 0 && (
            <section className="panel">
              <h3>Blocking issues</h3>
              <pre>{JSON.stringify(result.issues, null, 2)}</pre>
            </section>
          )}
          <section className="panel">
            <h3>Effective policy rows</h3>
            {result.rows.length === 0 ? (
              <EmptyState>No effective rows.</EmptyState>
            ) : (
              <pre>{JSON.stringify(result.rows, null, 2)}</pre>
            )}
          </section>
          <ProvenancePanel>
            <h3>Rule provenance</h3>
            <pre>{JSON.stringify(result.ruleProvenance, null, 2)}</pre>
            <h3>Export authority evidence</h3>
            <pre>{JSON.stringify(result.exportAuthorityEvidence, null, 2)}</pre>
            {result.nonEffective.length > 0 && (
              <>
                <h3>Non-effective rules</h3>
                <pre>{JSON.stringify(result.nonEffective, null, 2)}</pre>
              </>
            )}
          </ProvenancePanel>
        </>
      )}
      {!["editing", "submitting", "complete"].includes(state) && (
        <StatusBanner kind={state === "conflict" ? "warning" : "failed"}>
          Policy export operation: {state}.
        </StatusBanner>
      )}
    </>
  );
}
