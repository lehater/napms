import { useEffect, useState } from "react";
import { api, ApiError, type ResourceView } from "../../app/api";
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
    void api.listResources().then((value) => {
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
        <p className="lede">\n          Locate a Resource by stable identity and inspect current facts before\n          history.\n        </p>
      </PageHeader>
      {state === "loading" && <StatusBanner>Loading Resources…</StatusBanner>}
      {state !== "loading" && items.length === 0 && (\n        <EmptyState>No Resources.</EmptyState>\n      )}
      <section className="panel">
        {items.map((item) => (
          <button type="button" key={item.resourceRef} onClick={() => navigate(`/resources/${item.resourceRef}`)}>
            {item.displayName} · {item.resourceRef}
          </button>
        ))}
      </section>
      {!create && (\n        <button type="button" onClick={() => navigate("/resources/new")}>\n          Create Resource\n        </button>\n      )}
      {create && (
        <FormSection onSubmit={submit}>
          <ReferenceField\n            label="Display name"\n            value={displayName}\n            onChange={setDisplayName}\n          />
          <ReferenceField\n            label="Authority scope"\n            value={authorityScopeRef}\n            onChange={setAuthorityScopeRef}\n          />
          <ReferenceField\n            label="Initial site ID"\n            value={siteRef}\n            onChange={setSiteRef}\n          />
          <button\n            type="submit"\n            disabled={!displayName || !authorityScopeRef || state === "submitting"}\n          >\n            Create Resource\n          </button>
        </FormSection>
      )}
      {!["loading", "loaded", "submitting"].includes(state) && (\n        <StatusBanner kind="failed">Resource operation: {state}.</StatusBanner>\n      )}
    </>
  );
}

export function ResourceDetail({ resourceRef }: { resourceRef: string }) {
  const [resource, setResource] = useState<ResourceView | null>(null);
  const [state, setState] = useState("loading");
  const [siteRef, setSiteRef] = useState("");
  const [role, setRole] = useState("");
  const [organizationRef, setOrganizationRef] = useState("");

  async function load() {
    setState("loading");
    try {
      const value = await api.getResource(resourceRef);
      setResource(value);
      setSiteRef(value.current.siteRef ?? "");
      setState("loaded");
    } catch (error) {
      setState(errorKind(error));
    }
  }

  useEffect(() => {
    void load();
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

  if (state === "loading")\n    return <StatusBanner>Loading Resource…</StatusBanner>;
  if (!resource)\n    return <StatusBanner kind="failed">Resource: {state}.</StatusBanner>;

  return (
    <>
      <PageHeader eyebrow="Resource detail" title={resource.displayName}>
        <p className="muted">\n          {resource.resourceRef} · authority {resource.authorityScopeRef}\n        </p>
      </PageHeader>
      <VersionedEditor version={resource.version}>
        <h3>Current facts</h3>
        <ReferenceField label="Site ID" value={siteRef} onChange={setSiteRef} />
        <button\n          type="button"\n          onClick={() =>\n            void mutate(() =>\n              api.setResourceSite(\n                resource.resourceRef,\n                resource.version,\n                siteRef || null,\n              ),\n            )\n          }\n        >\n          Save site\n        </button>
        <h4>Endpoints</h4>
        {resource.current.endpoints.map((endpoint) => (
          <p key={endpoint.endpointRef}>\n            {endpoint.endpointRef} ·{" "}\n            {endpoint.address\n              ? `${endpoint.address.kind} ${endpoint.address.value}`\n              : "No address"}\n          </p>
        ))}
        <button\n          type="button"\n          onClick={() =>\n            void mutate(() =>\n              api.addResourceEndpoint(resource.resourceRef, resource.version),\n            )\n          }\n        >\n          Add endpoint\n        </button>
        <h4>Responsibilities</h4>
        {resource.current.responsibilities.map((item) => (\n          <p key={item.role}>\n            {item.role}: {item.organizationRef}\n          </p>\n        ))}
        <ReferenceField\n          label="Responsibility role"\n          value={role}\n          onChange={setRole}\n        />
        <ReferenceField\n          label="Organization ID"\n          value={organizationRef}\n          onChange={setOrganizationRef}\n        />
        <button\n          type="button"\n          disabled={!role}\n          onClick={() =>\n            void mutate(() =>\n              api.setResourceResponsibility(\n                resource.resourceRef,\n                role,\n                resource.version,\n                organizationRef || null,\n              ),\n            )\n          }\n        >\n          Save responsibility\n        </button>
      </VersionedEditor>
      {state !== "loaded" && (\n        <StatusBanner kind="failed">Resource operation: {state}.</StatusBanner>\n      )}
      <ProvenancePanel>\n        <pre>{JSON.stringify(resource.history, null, 2)}</pre>\n      </ProvenancePanel>
    </>
  );
}
