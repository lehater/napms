import { useState } from "react";
import { ApiError, type PolicyMaterializationResult } from "../../app/api";
import {
  OutcomePattern,
  ScopeSelectorPattern,
  type ScopeSelectorState,
} from "../../presentation";
import { materializePolicy } from "./policyExportApplication";

function failureState(error: unknown): {
  state: ScopeSelectorState;
  message: string;
} {
  if (error instanceof ApiError) {
    if (error.kind === "unauthenticated" || error.kind === "forbidden") {
      return {
        state: "authorization-rejected",
        message: "Policy export was rejected by the backend.",
      };
    }
    if (error.kind === "rejected") {
      return {
        state: "validation-rejected",
        message: "The selected Policy Rule scope was rejected.",
      };
    }
  }
  return {
    state: "technical-error",
    message: "Policy export failed.",
  };
}

export function PolicyExportScreen() {
  const [refs, setRefs] = useState("");
  const [state, setState] = useState<ScopeSelectorState>("editing");
  const [statusMessage, setStatusMessage] = useState<string>();
  const [result, setResult] = useState<PolicyMaterializationResult | null>(
    null,
  );

  async function submit() {
    setState("submitting");
    setStatusMessage(undefined);
    try {
      setResult(await materializePolicy(refs));
      setState("editing");
    } catch (error) {
      const failure = failureState(error);
      setState(failure.state);
      setStatusMessage(failure.message);
    }
  }

  return (
    <>
      <ScopeSelectorPattern
        eyebrow="Policy materialization"
        title="Policy Export"
        description="Select an explicit Policy Rule scope or leave it empty for the current effective policy."
        label="Policy Rule IDs (comma separated; empty means current effective policy)"
        value={refs}
        onChange={setRefs}
        executeLabel="Execute Export"
        onExecute={() => void submit()}
        state={state}
        statusMessage={statusMessage}
      />

      {result ? (
        <OutcomePattern
          title="Policy materialization outcome"
          summary={<>Export result: {result.status}</>}
          tone={result.status === "COMPLETE" ? "success" : "warning"}
          details={
            <div>
              <p>Evaluated at {result.evaluationAt}</p>
              {result.status === "UNRESOLVED" && result.issues.length > 0 ? (
                <>
                  <h3>Blocking issues</h3>
                  <pre>{JSON.stringify(result.issues, null, 2)}</pre>
                </>
              ) : null}
              <h3>Effective policy rows</h3>
              {result.rows.length === 0 ? (
                <p>No effective rows.</p>
              ) : (
                <pre>{JSON.stringify(result.rows, null, 2)}</pre>
              )}
            </div>
          }
          provenance={
            <div>
              <h3>Rule provenance</h3>
              <pre>{JSON.stringify(result.ruleProvenance, null, 2)}</pre>
              <h3>Export authority evidence</h3>
              <pre>{JSON.stringify(result.exportAuthorityEvidence, null, 2)}</pre>
              {result.nonEffective.length > 0 ? (
                <>
                  <h3>Non-effective rules</h3>
                  <pre>{JSON.stringify(result.nonEffective, null, 2)}</pre>
                </>
              ) : null}
            </div>
          }
        />
      ) : null}
    </>
  );
}
