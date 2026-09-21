import { useState } from "react";
import { ApiError, api } from "../../app/api";
import {
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
  const [result, setResult] = useState<Record<string, unknown> | null>(null);

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

  const unresolved =
    result &&
    ("unresolved" in result ||
      ("status" in result &&
        String(result.status).toUpperCase() !== "COMPLETE"));

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
          <StatusBanner kind={unresolved ? "warning" : "success"}>
            {unresolved ? "UNRESOLVED / DEGRADED" : "COMPLETE"}
          </StatusBanner>
          <section className="panel">
            <h3>Materialized policy</h3>
            <pre>{JSON.stringify(result, null, 2)}</pre>
          </section>
          <ProvenancePanel>
            Evaluation and provenance are preserved in the authoritative
            materialization response.
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
