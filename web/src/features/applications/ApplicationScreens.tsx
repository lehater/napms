import { useEffect, useState } from "react";
import { ApiError, type ApplicationView, api } from "../../app/api";
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

export function ApplicationCatalogue({ create = false }: { create?: boolean }) {
  const [items, setItems] = useState<ApplicationView[]>([]);
  const [state, setState] = useState("loading");
  const [name, setName] = useState("");

  useEffect(() => {
    void api
      .listApplications()
      .then((value) => {
        setItems(value);
        setState("loaded");
      })
      .catch((error) => setState(errorKind(error)));
  }, []);

  async function submit(event: React.FormEvent) {
    event.preventDefault();
    setState("submitting");
    try {
      const value = await api.createApplication(name);
      navigate(`/applications/${value.applicationRef}`);
    } catch (error) {
      setState(errorKind(error));
    }
  }

  return (
    <>
      <PageHeader eyebrow="Application catalogue" title="Applications" />
      {state === "loading" && (
        <StatusBanner>Loading Applications…</StatusBanner>
      )}
      {state !== "loading" && items.length === 0 && (
        <EmptyState>No Applications.</EmptyState>
      )}
      <section className="panel">
        {items.map((item) => (
          <button
            type="button"
            key={item.applicationRef}
            onClick={() => navigate(`/applications/${item.applicationRef}`)}
          >
            {item.name} · {item.applicationRef}
          </button>
        ))}
      </section>
      {!create && (
        <button type="button" onClick={() => navigate("/applications/new")}>
          Create Application
        </button>
      )}
      {create && (
        <FormSection onSubmit={submit}>
          <ReferenceField label="Name" value={name} onChange={setName} />
          <button type="submit" disabled={!name || state === "submitting"}>
            Create Application
          </button>
        </FormSection>
      )}
      {!["loading", "loaded", "submitting"].includes(state) && (
        <StatusBanner kind="failed">
          Application operation: {state}.
        </StatusBanner>
      )}
    </>
  );
}

export function ApplicationDetail({
  applicationRef,
  createComponent = false,
}: {
  applicationRef: string;
  createComponent?: boolean;
}) {
  const [application, setApplication] = useState<ApplicationView | null>(null);
  const [state, setState] = useState("loading");
  const [name, setName] = useState("");

  useEffect(() => {
    setState("loading");
    void api
      .getApplication(applicationRef)
      .then((value) => {
        setApplication(value);
        setState("loaded");
      })
      .catch((error) => setState(errorKind(error)));
  }, [applicationRef]);

  async function addComponent(event: React.FormEvent) {
    event.preventDefault();
    if (!application) return;
    setState("submitting");
    try {
      await api.addComponent(
        application.applicationRef,
        application.version,
        name,
      );
      const value = await api.getApplication(application.applicationRef);
      setApplication(value);
      setName("");
      setState("loaded");
      navigate(`/applications/${application.applicationRef}`);
    } catch (error) {
      setState(errorKind(error));
    }
  }

  if (state === "loading")
    return <StatusBanner>Loading Application…</StatusBanner>;
  if (!application)
    return <StatusBanner kind="failed">Application: {state}.</StatusBanner>;

  return (
    <>
      <PageHeader eyebrow="Application detail" title={application.name}>
        <p className="muted">{application.applicationRef}</p>
      </PageHeader>
      <VersionedEditor version={application.version}>
        <h3>Components</h3>
        {application.components.length === 0 && (
          <EmptyState>No Components.</EmptyState>
        )}
        {application.components.map((component) => (
          <p key={component.componentRef}>
            {component.name} · {component.componentRef}
          </p>
        ))}
        <button
          type="button"
          onClick={() =>
            navigate(
              `/applications/${application.applicationRef}/components/new`,
            )
          }
        >
          Add Component
        </button>
        <h3>Interactions</h3>
        {(application.interactions ?? []).length === 0 && (
          <EmptyState>No Interactions.</EmptyState>
        )}
        {(application.interactions ?? []).map((interaction) => (
          <section className="panel" key={interaction.interactionRef}>
            <p>
              {interaction.sourceComponentRef} → {interaction.destinationComponentRef}
            </p>
            <p>{interaction.purpose || "No stated purpose"}</p>
            <p>Interaction ID: {interaction.interactionRef}</p>
            {interaction.revisions.map((revision) => (
              <div key={revision.interactionRevisionRef}>
                <strong>Revision {revision.revisionNo}</strong>
                <pre>{JSON.stringify(revision.trafficClauses, null, 2)}</pre>
              </div>
            ))}
            <button
              type="button"
              onClick={() =>
                navigate(
                  `/interactions/${interaction.interactionRef}/revisions/new`,
                )
              }
            >
              Publish Revision
            </button>
          </section>
        ))}
        <button type="button" onClick={() => navigate("/interactions/new")}>
          Create Interaction
        </button>
      </VersionedEditor>
      {createComponent && (
        <FormSection onSubmit={addComponent}>
          <ReferenceField
            label="Component name"
            value={name}
            onChange={setName}
          />
          <button type="submit" disabled={!name || state === "submitting"}>
            Add Component
          </button>
        </FormSection>
      )}
      {state !== "loaded" && (
        <StatusBanner kind="failed">
          Application operation: {state}.
        </StatusBanner>
      )}
    </>
  );
}

export function InteractionAuthoring({
  interactionRef,
}: {
  interactionRef?: string;
}) {
  const [source, setSource] = useState("");
  const [destination, setDestination] = useState("");
  const [purpose, setPurpose] = useState("");
  const [protocol, setProtocol] = useState("6");
  const [version, setVersion] = useState("0");
  const [state, setState] = useState("editing");

  async function submit(event: React.FormEvent) {
    event.preventDefault();
    setState("submitting");
    try {
      if (interactionRef) {
        await api.publishRevision(interactionRef, Number(version), [
          { ipProtocol: Number(protocol) },
        ]);
        setState("loaded");
      } else {
        const value = await api.createInteraction({
          sourceComponentRef: source,
          destinationComponentRef: destination,
          ...(purpose ? { purpose } : {}),
        });
        navigate(`/interactions/${value.interactionRef}/revisions/new`);
      }
    } catch (error) {
      setState(errorKind(error));
    }
  }

  return (
    <>
      <PageHeader
        eyebrow="Application detail"
        title={
          interactionRef ? "Publish interaction revision" : "Create interaction"
        }
      />
      <FormSection onSubmit={submit}>
        {!interactionRef && (
          <>
            <ReferenceField
              label="Source Component ID"
              value={source}
              onChange={setSource}
            />
            <ReferenceField
              label="Destination Component ID"
              value={destination}
              onChange={setDestination}
            />
            <ReferenceField
              label="Purpose"
              value={purpose}
              onChange={setPurpose}
            />
          </>
        )}
        {interactionRef && (
          <>
            <ReferenceField
              label="Interaction ID"
              value={interactionRef}
              readOnly
            />
            <ReferenceField
              label="Expected version"
              value={version}
              onChange={setVersion}
            />
            <ReferenceField
              label="IP protocol number"
              value={protocol}
              onChange={setProtocol}
            />
          </>
        )}
        <button
          type="submit"
          disabled={
            state === "submitting" ||
            (!interactionRef && (!source || !destination))
          }
        >
          {interactionRef ? "Publish revision" : "Create interaction"}
        </button>
      </FormSection>
      {!["editing", "loaded", "submitting"].includes(state) && (
        <StatusBanner kind={state === "conflict" ? "warning" : "failed"}>
          Interaction operation: {state}.
        </StatusBanner>
      )}
    </>
  );
}
