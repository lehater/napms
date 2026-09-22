import { useEffect, useState } from "react";
import { ApiError } from "../../app/api";
import { navigate } from "../../app/router";
import { DetailPattern, type DetailState } from "../../presentation";
import { queryDeploymentDetail } from "./deploymentApplication";
import type { DeploymentDetailScreenModel } from "./deploymentModels";

function failureState(error: unknown): {
  state: DetailState;
  message: string;
} {
  if (error instanceof ApiError) {
    if (error.kind === "not-found") {
      return {
        state: "not-found",
        message: "Deployment was not found.",
      };
    }
    if (error.kind === "unauthenticated" || error.kind === "forbidden") {
      return {
        state: "authorization-rejected",
        message: "Deployment detail access was rejected by the backend.",
      };
    }
  }
  return {
    state: "technical-error",
    message: "Deployment detail could not be loaded.",
  };
}

export function DeploymentDetailScreen({
  deploymentRef,
}: {
  deploymentRef: string;
}) {
  const [model, setModel] = useState<DeploymentDetailScreenModel>();
  const [state, setState] = useState<DetailState>("loading");
  const [statusMessage, setStatusMessage] = useState<string>();

  useEffect(() => {
    let active = true;
    setState("loading");
    setStatusMessage(undefined);
    void queryDeploymentDetail(deploymentRef)
      .then((next) => {
        if (!active) return;
        setModel(next);
        setState("loaded");
      })
      .catch((error) => {
        if (!active) return;
        const failure = failureState(error);
        setState(failure.state);
        setStatusMessage(failure.message);
      });
    return () => {
      active = false;
    };
  }, [deploymentRef]);

  const sections = model
    ? [
        {
          id: "realization",
          title: "Deployment realization",
          summary: (
            <dl>
              <dt>Component</dt>
              <dd data-presentation-technical-context>{model.componentRef}</dd>
              <dt>Resource</dt>
              <dd data-presentation-technical-context>{model.resourceRef}</dd>
            </dl>
          ),
        },
      ]
    : [];

  return (
    <DetailPattern
      eyebrow="Deployment detail"
      title="Deployment"
      technicalContext={model?.deploymentRef ?? deploymentRef}
      description="Inspect the Component deployment and the Resource that realizes it."
      sections={sections}
      state={state}
      statusMessage={statusMessage}
      onRetry={() => window.location.reload()}
      onReturn={() => navigate("/deployments")}
    />
  );
}
