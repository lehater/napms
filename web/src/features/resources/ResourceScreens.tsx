import { useEffect, useState } from "react";
import { ApiError, api, type ResourceView } from "../../app/api";
import { navigate } from "../../app/router";
import {
  EmptyState,
  FormSection,
  PageHeader,
  ProvenancePanel,
  ReferenceField,
  StatusBanner,
  VersionedEditor,
} from "../../design-system/components";

function errorKind(error: unknown): string {
  return error instanceof ApiError ? error.kind : "technical";
}

export function ResourceCatalogue({ create = false }: { create?: boolean }) {
  const [items, setItems] = useState<ResourceView[]>([]);
  const [state, setState] = useState("loading");
  const [displayName, setDisplayName] = useState("");
  const [authorityScopeRef, setAuthorityScopeRef] = useState("");
  const [siteRef, setSiteRef] = useState("");

  useEffect(() => {
    void api
      .listResources()
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
      const created = await api.createResource({
        displayName,
        authorityScopeRef,
        ...(siteRef ? { siteRef } : {}),
      });
      navigate(`/resources/${created.resourceRef}`);
    } catch (error) {
      setState(errorKind(error));
    }
  }

  return (
    <>
      <PageHeader eyebrow="Resource catalogue" title="Resources">
        <p className="lede">
          Locate a Resource by stable identity and inspect current facts before
          history.
        </p>
      </PageHeader>
      {state === "loading" && <StatusBanner>Loading Resources…</StatusBanner>}
      {state !== "loading" && items.length === 0 && (
        <EmptyState>No Resources.</EmptyState>
      )}
      <section className="panel">
        {items.map((item) => (
          <button
            type="button"
            key={item.resourceRef}
            onClick={() => navigate(`/resources/${item.resourceRef}`)}
          >
            {item.displayName} · {item.resourceRef}
          </button>
        ))}
      </section>
      {!create && (
        <button type="button" onClick={() => navigate("/resources/new")}>
          Create Resource
        </button>
      )}
      {create && (
        <FormSection onSubmit={submit}>
          <ReferenceField
            label="Display name"
            value={displayName}
            onChange={setDisplayName}
          />
          <ReferenceField
            label="Authority scope"
            value={authorityScopeRef}
            onChange={setAuthorityScopeRef}
          />
          <ReferenceField
            label="Initial site ID"
            value={siteRef}
            onChange={setSiteRef}
          />
          <button
            type="submit"
            disabled={
              !displayName || !authorityScopeRef || state === "submitting"
            }
          >
            Create Resource
          </button>
        </FormSection>
      )}
      {!["loading", "loaded", "submitting"].includes(state) && (
        <StatusBanner kind="failed">Resource operation: {state}.</StatusBanner>
      )}
    </>
  );
}

export function ResourceDetail({ resourceRef }: { resourceRef: string }) {
  const [resource, setResource] = useState<ResourceView | null>(null);
  const [state, setState] = useState("loading");
  const [siteRef, setSiteRef] = useState("");
  const [role, setRole] = useState("");
  const [organizationRef, setOrganizationRef] = useState("");

  useEffect(() => {
    setState("loading");
    void api
      .getResource(resourceRef)
      .then((value) => {
        setResource(value);
        setSiteRef(value.current.siteRef ?? "");
        setState("loaded");
      })
      .catch((error) => setState(errorKind(error)));
  }, [resourceRef]);

  async function mutate(call: () => Promise<ResourceView>) {
    setState("submitting");
    try {
      const value = await call();
      setResource(value);
      setSiteRef(value.current.siteRef ?? "");
      setState("loaded");
    } catch (error) {
      setState(errorKind(error));
    }
  }

  if (state === "loading")
    return <StatusBanner>Loading Resource…</StatusBanner>;
  if (!resource)
    return <StatusBanner kind="failed">Resource: {state}.</StatusBanner>;

  return (
    <>
      <PageHeader eyebrow="Resource detail" title={resource.displayName}>
        <p className="muted">
          {resource.resourceRef} · authority {resource.authorityScopeRef}
        </p>
      </PageHeader>
      <VersionedEditor version={resource.version}>
        <h3>Current facts</h3>
        <ReferenceField label="Site ID" value={siteRef} onChange={setSiteRef} />
        <button
          type="button"
          onClick={() =>
            void mutate(() =>
              api.setResourceSite(
                resource.resourceRef,
                resource.version,
                siteRef || null,
              ),
            )
          }
        >
          Save site
        </button>
        <h4>Endpoints</h4>
        {resource.current.endpoints.map((endpoint) => (
          <p key={endpoint.endpointRef}>
            {endpoint.endpointRef} ·{" "}
            {endpoint.address
              ? `${endpoint.address.kind} ${endpoint.address.value}`
              : "No address"}
          </p>
        ))}
        <button
          type="button"
          onClick={() =>
            void mutate(() =>
              api.addResourceEndpoint(resource.resourceRef, resource.version),
            )
          }
        >
          Add endpoint
        </button>
        <h4>Responsibilities</h4>
        {resource.current.responsibilities.map((item) => (
          <p key={item.role}>
            {item.role}: {item.organizationRef}
          </p>
        ))}
        <ReferenceField
          label="Responsibility role"
          value={role}
          onChange={setRole}
        />
        <ReferenceField
          label="Organization ID"
          value={organizationRef}
          onChange={setOrganizationRef}
        />
        <button
          type="button"
          disabled={!role}
          onClick={() =>
            void mutate(() =>
              api.setResourceResponsibility(
                resource.resourceRef,
                role,
                resource.version,
                organizationRef || null,
              ),
            )
          }
        >
          Save responsibility
        </button>
      </VersionedEditor>
      {state !== "loaded" && (
        <StatusBanner kind="failed">Resource operation: {state}.</StatusBanner>
      )}
      <ProvenancePanel>
        <pre>{JSON.stringify(resource.history, null, 2)}</pre>
      </ProvenancePanel>
    </>
  );
}
