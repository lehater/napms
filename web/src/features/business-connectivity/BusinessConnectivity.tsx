import { useEffect, useState } from "react";
import { ApiError, api, type ProcessView } from "../../app/api";
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

export function BusinessConnectivity({
  create = false,
  processRef,
}: {
  create?: boolean;
  processRef?: string;
}) {
  const [items, setItems] = useState<ProcessView[]>([]);
  const [selected, setSelected] = useState<ProcessView | null>(null);
  const [state, setState] = useState("loading");
  const [name, setName] = useState("");
  const [description, setDescription] = useState("");
  const [criticality, setCriticality] = useState("");
  const [organizationRef, setOrganizationRef] = useState("");
  const [organizationName, setOrganizationName] = useState("");
  const [interactionRef, setInteractionRef] = useState("");
  const [componentRef, setComponentRef] = useState("");
  const [basis, setBasis] = useState("");

  useEffect(() => {
    const load = processRef ? api.getProcess(processRef) : api.listProcesses();
    void load
      .then((value) => {
        if (Array.isArray(value)) setItems(value);
        else {
          setSelected(value);
          setCriticality(value.criticalityLabel ?? "");
          setOrganizationRef(value.organizationExternalReference ?? "");
          setOrganizationName(value.organizationDisplayName ?? "");
        }
        setState("loaded");
      })
      .catch((error) => setState(errorKind(error)));
  }, [processRef]);

  async function createProcess(event: React.FormEvent) {
    event.preventDefault();
    setState("submitting");
    try {
      const value = await api.createProcess({
        name,
        ...(description ? { description } : {}),
        ...(criticality ? { criticalityLabel: criticality } : {}),
      });
      navigate(`/business-processes/${value.processRef}`);
    } catch (error) {
      setState(errorKind(error));
    }
  }

  async function saveCriticality() {
    if (!selected) return;
    setState("submitting");
    try {
      await api.setProcessCriticality(
        selected.processRef,
        selected.version,
        criticality || null,
      );
      const value = await api.getProcess(selected.processRef);
      setSelected(value);
      setCriticality(value.criticalityLabel ?? "");
      setState("loaded");
    } catch (error) {
      setState(errorKind(error));
    }
  }

  async function saveOrganization() {
    if (!selected) return;
    setState("submitting");
    try {
      await api.setProcessResponsibleOrganization(
        selected.processRef,
        selected.version,
        organizationRef || null,
        organizationName || null,
      );
      const value = await api.getProcess(selected.processRef);
      setSelected(value);
      setOrganizationRef(value.organizationExternalReference ?? "");
      setOrganizationName(value.organizationDisplayName ?? "");
      setState("loaded");
    } catch (error) {
      setState(errorKind(error));
    }
  }

  async function retireNeed(needRef: string) {
    if (!selected) return;
    setState("submitting");
    try {
      await api.retireNeed(selected.processRef, needRef, selected.version);
      const value = await api.getProcess(selected.processRef);
      setSelected(value);
      setState("loaded");
    } catch (error) {
      setState(errorKind(error));
    }
  }

  async function declareNeed(event: React.FormEvent) {
    event.preventDefault();
    if (!selected) return;
    setState("submitting");
    try {
      await api.declareNeed(selected.processRef, selected.version, {
        interactionRef,
        participantComponentRef: componentRef,
        businessBasis: basis,
      });
      const value = await api.getProcess(selected.processRef);
      setSelected(value);
      setState("loaded");
    } catch (error) {
      setState(errorKind(error));
    }
  }

  return (
    <>
      <PageHeader eyebrow="Business connectivity" title="Business Processes" />
      {state === "loading" && (
        <StatusBanner>Loading Business Processes…</StatusBanner>
      )}
      {!processRef && items.length === 0 && state !== "loading" && (
        <EmptyState>No Business Processes.</EmptyState>
      )}
      {!processRef && (
        <section className="panel">
          {items.map((item) => (
            <button
              type="button"
              key={item.processRef}
              onClick={() => navigate(`/business-processes/${item.processRef}`)}
            >
              {item.name} · {item.processRef}
            </button>
          ))}
          {!create && (
            <button
              type="button"
              onClick={() => navigate("/business-processes/new")}
            >
              Create Business Process
            </button>
          )}
        </section>
      )}
      {create && (
        <FormSection onSubmit={createProcess}>
          <ReferenceField label="Name" value={name} onChange={setName} />
          <ReferenceField
            label="Description"
            value={description}
            onChange={setDescription}
          />
          <ReferenceField
            label="Criticality"
            value={criticality}
            onChange={setCriticality}
          />
          <button type="submit" disabled={!name || state === "submitting"}>
            Create Business Process
          </button>
        </FormSection>
      )}
      {selected && (
        <>
          <VersionedEditor version={selected.version}>
            <h3>{selected.name}</h3>
            <p>
              {selected.description || "No description"} · criticality{" "}
              {selected.criticalityLabel || "unset"}
            </p>
            <ReferenceField
              label="Responsible organization reference"
              value={organizationRef}
              onChange={setOrganizationRef}
            />
            <ReferenceField
              label="Responsible organization name"
              value={organizationName}
              onChange={setOrganizationName}
            />
            <button
              type="button"
              disabled={state === "submitting"}
              onClick={() => void saveOrganization()}
            >
              Save responsible organization
            </button>
            <ReferenceField
              label="Criticality"
              value={criticality}
              onChange={setCriticality}
            />
            <button
              type="button"
              disabled={state === "submitting"}
              onClick={() => void saveCriticality()}
            >
              Save criticality
            </button>
            <h4>Connectivity Needs</h4>
            {selected.needs.length === 0 && (
              <EmptyState>No Connectivity Needs.</EmptyState>
            )}
            {selected.needs.map((need) => (
              <div key={need.needRef}>
                <p>
                  {need.needRef} · {need.status} · Interaction{" "}
                  {need.interactionRef} · Participant{" "}
                  {need.participantComponentRef} · {need.businessBasis}
                </p>
                {need.status === "ACTIVE" && (
                  <button
                    type="button"
                    onClick={() => void retireNeed(need.needRef)}
                  >
                    Retire Connectivity Need
                  </button>
                )}
              </div>
            ))}
          </VersionedEditor>
          <FormSection onSubmit={declareNeed}>
            <ReferenceField
              label="Interaction ID"
              value={interactionRef}
              onChange={setInteractionRef}
            />
            <ReferenceField
              label="Participant Component ID"
              value={componentRef}
              onChange={setComponentRef}
            />
            <ReferenceField
              label="Business basis"
              value={basis}
              onChange={setBasis}
            />
            <button
              type="submit"
              disabled={
                !interactionRef ||
                !componentRef ||
                !basis ||
                state === "submitting"
              }
            >
              Declare Connectivity Need
            </button>
          </FormSection>
        </>
      )}
      {!["loading", "loaded", "submitting"].includes(state) && (
        <StatusBanner kind={state === "conflict" ? "warning" : "failed"}>
          Business connectivity operation: {state}.
        </StatusBanner>
      )}
    </>
  );
}
