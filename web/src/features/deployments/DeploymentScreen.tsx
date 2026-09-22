import { useEffect, useState } from "react";
import { ApiError } from "../../app/api";
import { navigate } from "../../app/router";
import {
  CataloguePattern,
  type CatalogueState,
  EditorPattern,
  type EditorState,
  StructuredListPattern,
} from "../../presentation";
import {
  createDeployment,
  queryDeployments,
} from "./deploymentApplication";
import type { DeploymentScreenModel } from "./deploymentModels";

type LoadState =
  | { kind: "loading" }
  | { kind: "loaded"; model: DeploymentScreenModel }
  | { kind: "authorization-rejected"; message: string }
  | { kind: "technical-error"; message: string };

function loadFailure(error: unknown): LoadState {
  if (
    error instanceof ApiError &&
    (error.kind === "unauthenticated" || error.kind === "forbidden")
  ) {
    return {
      kind: "authorization-rejected",
      message: "Deployment catalogue access was rejected by the backend.",
    };
  }
  return {
    kind: "technical-error",
    message: "Deployments could not be loaded.",
  };
}

function createFailure(error: unknown): {
  state: EditorState;
  message: string;
} {
  if (error instanceof ApiError) {
    if (error.kind === "unauthenticated" || error.kind === "forbidden") {
      return {
        state: "authorization-rejected",
        message: "Deployment creation was rejected by the backend.",
      };
    }
    if (error.kind === "rejected") {
      return {
        state: "validation-rejected",
        message: "Deployment values were rejected by the backend.",
      };
    }
    if (error.kind === "conflict") {
      return {
        state: "conflict",
        message: "Deployment creation conflicts with current server state.",
      };
    }
  }
  return {
    state: "technical-error",
    message: "Deployment creation failed.",
  };
}

function DeploymentListMode() {
  const [loadState, setLoadState] = useState<LoadState>({ kind: "loading" });

  useEffect(() => {
    let active = true;
    void queryDeployments()
      .then((model) => {
        if (active) setLoadState({ kind: "loaded", model });
      })
      .catch((error) => {
        if (active) setLoadState(loadFailure(error));
      });
    return () => {
      active = false;
    };
  }, []);

  const rows =
    loadState.kind === "loaded" ? loadState.model.deployments : [];
  const state: CatalogueState =
    loadState.kind === "loaded"
      ? rows.length === 0
        ? "empty"
        : "loaded"
      : loadState.kind;
  const statusMessage =
    loadState.kind === "authorization-rejected" ||
    loadState.kind === "technical-error"
      ? loadState.message
      : undefined;

  return (
    <CataloguePattern
      eyebrow="Deployment management"
      title="Deployments"
      description="Inspect Component deployments and the Resource realizing each deployment."
      primaryAction={{
        label: "Create Deployment",
        onInvoke: () => navigate("/deployments/new"),
      }}
      state={state}
      statusMessage={statusMessage}
      emptyMessage="No Deployments."
    >
      <StructuredListPattern
        label="Deployments"
        rows={rows}
        rowKey={(row) => row.deploymentRef}
        primary={(row) => (
          <>
            Component {row.componentRef} · Resource {row.resourceRef}
          </>
        )}
        secondary={(row) => row.deploymentRef}
        emptyMessage="No Deployments."
      />
    </CataloguePattern>
  );
}

function DeploymentCreateMode() {
  const [componentRef, setComponentRef] = useState("");
  const [resourceRef, setResourceRef] = useState("");
  const [state, setState] = useState<EditorState>("editing");
  const [statusMessage, setStatusMessage] = useState<string>();

  async function submit() {
    setState("submitting");
    setStatusMessage(undefined);
    try {
      await createDeployment({ componentRef, resourceRef });
      navigate("/deployments");
    } catch (error) {
      const failure = createFailure(error);
      setState(failure.state);
      setStatusMessage(failure.message);
    }
  }

  return (
    <EditorPattern
      eyebrow="Deployment management"
      title="Deployments"
      description="Create a Component deployment realized by an existing Resource."
      fields={[
        {
          id: "component-ref",
          label: "Component ID",
          value: componentRef,
          required: true,
          onChange: setComponentRef,
        },
        {
          id: "resource-ref",
          label: "Resource ID",
          value: resourceRef,
          required: true,
          onChange: setResourceRef,
        },
      ]}
      submitLabel="Create Deployment"
      submitDisabled={!componentRef || !resourceRef}
      onSubmit={() => void submit()}
      state={state}
      statusMessage={statusMessage}
    />
  );
}

export function DeploymentScreen({
  create = false,
}: {
  create?: boolean;
}) {
  return create ? <DeploymentCreateMode /> : <DeploymentListMode />;
}
