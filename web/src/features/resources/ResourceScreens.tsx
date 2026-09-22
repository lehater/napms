import { useEffect, useState } from "react";
import { ApiError, api, type ResourceView } from "../../app/api";
import {
  PageHeader,
  ProvenancePanel,
  ReferenceField,
  StatusBanner,
  VersionedEditor,
} from "../../design-system/components";
import { ResourceCatalogueScreen } from "./ResourceCatalogueScreen";

function errorKind(error: unknown): string {
  return error instanceof ApiError ? error.kind : "technical";
}

export function ResourceCatalogue({ create = false }: { create?: boolean }) {
  return <ResourceCatalogueScreen create={create} />;
}

export function ResourceDetail({ resourceRef }: { resourceRef: string }) {
  const [resource, setResource] = useState<ResourceView | null>(null);
  const [state, setState] = useState("loading");
  const [siteRef, setSiteRef] = useState("");
  const [role, setRole] = useState<"OWNER" | "ADMINISTRATOR">("OWNER");
  const [organizationRef, setOrganizationRef] = useState("");
  const [endpointRef, setEndpointRef] = useState("");
  const [addressKind, setAddressKind] = useState("HOST");
  const [addressValue, setAddressValue] = useState("");

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

  if (state === "loading") {
    return <StatusBanner>Loading Resource…</StatusBanner>;
  }
  if (!resource) {
    return <StatusBanner kind="failed">Resource: {state}.</StatusBanner>;
  }

  return (
    <>
      <PageHeader eyebrow="Resource detail" title={resource.displayName}>
        <p className="muted technical-reference">
          {resource.resourceRef} · authority {resource.authorityScopeRef}
        </p>
      </PageHeader>

      <VersionedEditor version={resource.version}>
        <h3>Current facts</h3>

        <section className="resource-current-group">
          <h4>Site</h4>
          <ReferenceField
            label="Site ID"
            value={siteRef}
            onChange={setSiteRef}
          />
          <div>
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
          </div>
        </section>

        <section className="resource-current-group">
          <h4>Endpoints</h4>
          {resource.current.endpoints.length === 0 ? (
            <p className="muted">No endpoints.</p>
          ) : (
            resource.current.endpoints.map((endpoint) => (
              <p key={endpoint.endpointRef} className="current-summary">
                <span className="technical-reference">
                  {endpoint.endpointRef}
                </span>
                {" · "}
                {endpoint.address
                  ? `${endpoint.address.kind} ${endpoint.address.value}`
                  : "No address"}
              </p>
            ))
          )}
          <div>
            <button
              type="button"
              onClick={() =>
                void mutate(() =>
                  api.addResourceEndpoint(
                    resource.resourceRef,
                    resource.version,
                  ),
                )
              }
            >
              Add endpoint
            </button>
          </div>
          <ReferenceField
            label="Endpoint ID"
            value={endpointRef}
            onChange={setEndpointRef}
          />
          <label>
            Address kind
            <select
              value={addressKind}
              onChange={(event) => setAddressKind(event.target.value)}
            >
              <option value="HOST">HOST</option>
              <option value="PREFIX">PREFIX</option>
            </select>
          </label>
          <ReferenceField
            label="Address value"
            value={addressValue}
            onChange={setAddressValue}
          />
          <div>
            <button
              type="button"
              disabled={!endpointRef || !addressValue}
              onClick={() =>
                void mutate(() =>
                  api.setResourceAddress(
                    resource.resourceRef,
                    endpointRef,
                    resource.version,
                    { kind: addressKind, value: addressValue },
                  ),
                )
              }
            >
              Set endpoint address
            </button>
          </div>
        </section>

        <section className="resource-current-group">
          <h4>Responsibilities</h4>
          {resource.current.responsibilities.length === 0 ? (
            <p className="muted">No responsibilities.</p>
          ) : (
            resource.current.responsibilities.map((item) => (
              <p key={item.role} className="current-summary">
                {item.role}: {item.organizationRef}
              </p>
            ))
          )}
          <label>
            Responsibility role
            <select
              value={role}
              onChange={(event) =>
                setRole(event.target.value as "OWNER" | "ADMINISTRATOR")
              }
            >
              <option value="OWNER">OWNER</option>
              <option value="ADMINISTRATOR">ADMINISTRATOR</option>
            </select>
          </label>
          <ReferenceField
            label="Organization ID"
            value={organizationRef}
            onChange={setOrganizationRef}
          />
          <div>
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
          </div>
        </section>
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
