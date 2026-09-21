import { useEffect, useState } from "react";
import { ApiError, api, type DeploymentView } from "../../app/api";
import { navigate } from "../../app/router";
import {
  EmptyState,
  FormSection,
  PageHeader,
  ReferenceField,
  StatusBanner,
} from "../../design-system/components";

const errorKind = (error: unknown) =>
  error instanceof ApiError ? error.kind : "technical";

export function DeploymentScreens({ create = false }: { create?: boolean }) {
  const [items, setItems] = useState<DeploymentView[]>([]);
  const [componentRef, setComponentRef] = useState("");
  const [resourceRef, setResourceRef] = useState("");
  const [state, setState] = useState("loading");

  useEffect(() => {
    void api
      .listDeployments()
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
      const value = await api.createDeployment(componentRef, resourceRef);
      setItems((current) => [...current, value]);
      setState("loaded");
      navigate("/deployments");
    } catch (error) {
      setState(errorKind(error));
    }
  }

  return (
    <>
      <PageHeader eyebrow="Deployment management" title="Deployments" />
      {state === "loading" && <StatusBanner>Loading Deployments…</StatusBanner>}
      {items.length === 0 && state !== "loading" && (
        <EmptyState>No Deployments.</EmptyState>
      )}
      <section className="panel">
        {items.map((item) => (
          <p key={item.deploymentRef}>
            {item.deploymentRef} · Component {item.componentRef} · Resource{" "}
            {item.resourceRef}
          </p>
        ))}
      </section>
      {!create && (
        <button type="button" onClick={() => navigate("/deployments/new")}>
          Create Deployment
        </button>
      )}
      {create && (
        <FormSection onSubmit={submit}>
          <ReferenceField
            label="Component ID"
            value={componentRef}
            onChange={setComponentRef}
          />
          <ReferenceField
            label="Resource ID"
            value={resourceRef}
            onChange={setResourceRef}
          />
          <button
            type="submit"
            disabled={!componentRef || !resourceRef || state === "submitting"}
          >
            Create Deployment
          </button>
        </FormSection>
      )}
      {!["loading", "loaded", "submitting"].includes(state) && (
        <StatusBanner kind="failed">Deployment operation: {state}.</StatusBanner>
      )}
    </>
  );
}
