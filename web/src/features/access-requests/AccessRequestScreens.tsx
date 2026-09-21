import { useEffect, useState } from "react";
import { ApiError, type AccessRequestView, api } from "../../app/api";
import { navigate } from "../../app/router";
import {
  EmptyState,
  FormSection,
  PageHeader,
  ReferenceField,
  StatusBanner,
  VersionedEditor,
} from "../../design-system/components";

const errorKind = (error: unknown) =>
  error instanceof ApiError ? error.kind : "technical";

export function AccessRequestScreens({
  create = false,
  requestRef,
}: {
  create?: boolean;
  requestRef?: string;
}) {
  const [items, setItems] = useState<AccessRequestView[]>([]);
  const [selected, setSelected] = useState<AccessRequestView | null>(null);
  const [state, setState] = useState("loading");
  const [source, setSource] = useState("");
  const [destination, setDestination] = useState("");
  const [revision, setRevision] = useState("");
  const [need, setNeed] = useState("");
  const [decision, setDecision] = useState<"ALLOWED" | "DENIED">("ALLOWED");
  const [externalDecisionRef, setExternalDecisionRef] = useState("");

  useEffect(() => {
    const load = requestRef
      ? api.getAccessRequest(requestRef)
      : api.listAccessRequests();
    void load
      .then((value) => {
        if (Array.isArray(value)) setItems(value);
        else setSelected(value);
        setState("loaded");
      })
      .catch((error) => setState(errorKind(error)));
  }, [requestRef]);

  async function submitRequest(event: React.FormEvent) {
    event.preventDefault();
    setState("submitting");
    try {
      const value = await api.submitAccessRequest({
        sourceDeploymentRef: source,
        destinationDeploymentRef: destination,
        interactionRevisionRef: revision,
        needRef: need,
      });
      navigate(`/access-requests/${value.requestRef}/decision`);
    } catch (error) {
      setState(errorKind(error));
    }
  }

  async function submitDecision(event: React.FormEvent) {
    event.preventDefault();
    if (!selected) return;
    setState("submitting");
    try {
      const value = await api.decideAccessRequest(
        selected.requestRef,
        selected.version,
        decision,
        externalDecisionRef || undefined,
      );
      if (value.policyRuleRef) {
        navigate(`/policy-rules/${value.policyRuleRef}`);
        return;
      }
      const refreshed = await api.getAccessRequest(selected.requestRef);
      setSelected(refreshed);
      setState("loaded");
    } catch (error) {
      setState(errorKind(error));
    }
  }

  return (
    <>
      <PageHeader eyebrow="Access policy" title="Access Requests" />
      {state === "loading" && (
        <StatusBanner>Loading Access Requests…</StatusBanner>
      )}
      {!requestRef && items.length === 0 && state !== "loading" && (
        <EmptyState>No Access Requests.</EmptyState>
      )}
      {!requestRef && (
        <section className="panel">
          {items.map((item) => (
            <button
              type="button"
              key={item.requestRef}
              onClick={() =>
                navigate(`/access-requests/${item.requestRef}/decision`)
              }
            >
              {item.requestRef} · {item.decisionResult || "PENDING"}
            </button>
          ))}
          {!create && (
            <button
              type="button"
              onClick={() => navigate("/access-requests/new")}
            >
              Submit Access Request
            </button>
          )}
        </section>
      )}
      {create && (
        <FormSection onSubmit={submitRequest}>
          <ReferenceField
            label="Source Deployment ID"
            value={source}
            onChange={setSource}
          />
          <ReferenceField
            label="Destination Deployment ID"
            value={destination}
            onChange={setDestination}
          />
          <ReferenceField
            label="Interaction Revision ID"
            value={revision}
            onChange={setRevision}
          />
          <ReferenceField
            label="Connectivity Need ID"
            value={need}
            onChange={setNeed}
          />
          <button
            type="submit"
            disabled={
              !source ||
              !destination ||
              !revision ||
              !need ||
              state === "submitting"
            }
          >
            Submit Request
          </button>
        </FormSection>
      )}
      {selected && (
        <>
          <VersionedEditor version={selected.version}>
            <ReferenceField
              label="Request ID"
              value={selected.requestRef}
              readOnly
            />
            <ReferenceField
              label="Source Deployment ID"
              value={selected.sourceDeploymentRef}
              readOnly
            />
            <ReferenceField
              label="Destination Deployment ID"
              value={selected.destinationDeploymentRef}
              readOnly
            />
            <ReferenceField
              label="Interaction Revision ID"
              value={selected.interactionRevisionRef}
              readOnly
            />
            <ReferenceField
              label="Connectivity Need ID"
              value={selected.needRef}
              readOnly
            />
            <p>Outcome: {selected.decisionResult || "PENDING"}</p>
          </VersionedEditor>
          {!selected.decisionResult && (
            <FormSection onSubmit={submitDecision}>
              <label>
                Decision
                <select
                  value={decision}
                  onChange={(event) =>
                    setDecision(event.target.value as "ALLOWED" | "DENIED")
                  }
                >
                  <option value="ALLOWED">Allowed</option>
                  <option value="DENIED">Denied</option>
                </select>
              </label>
              <ReferenceField
                label="External decision reference"
                value={externalDecisionRef}
                onChange={setExternalDecisionRef}
              />
              <button type="submit" disabled={state === "submitting"}>
                Record Decision
              </button>
            </FormSection>
          )}
        </>
      )}
      {!["loading", "loaded", "submitting"].includes(state) && (
        <StatusBanner kind={state === "conflict" ? "warning" : "failed"}>
          Access request operation: {state}.
        </StatusBanner>
      )}
    </>
  );
}
