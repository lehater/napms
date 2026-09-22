import { useEffect, useState } from "react";
import { ApiError } from "../../app/api";
import { navigate } from "../../app/router";
import {
  CataloguePattern,
  type CatalogueState,
  DetailPattern,
  type DetailState,
  EditorPattern,
  type EditorPatternProps,
  type EditorState,
  OutcomePattern,
  StructuredListPattern,
} from "../../presentation";
import {
  decideAccessRequest,
  queryAccessRequest,
  queryAccessRequests,
  submitAccessRequest,
} from "./accessRequestApplication";
import type {
  AccessRequestCatalogueItem,
  AccessRequestDetailScreenModel,
} from "./accessRequestModels";

type CatalogueLoadState =
  | { kind: "loading" }
  | { kind: "loaded"; items: AccessRequestCatalogueItem[] }
  | { kind: "authorization-rejected"; message: string }
  | { kind: "technical-error"; message: string };

function catalogueFailure(error: unknown): CatalogueLoadState {
  if (
    error instanceof ApiError &&
    (error.kind === "unauthenticated" || error.kind === "forbidden")
  ) {
    return {
      kind: "authorization-rejected",
      message: "Access Request catalogue access was rejected by the backend.",
    };
  }
  return {
    kind: "technical-error",
    message: "Access Requests could not be loaded.",
  };
}

function detailFailure(error: unknown): {
  state: DetailState;
  message: string;
} {
  if (error instanceof ApiError) {
    if (error.kind === "not-found") {
      return {
        state: "not-found",
        message: "The requested Access Request does not exist.",
      };
    }
    if (error.kind === "unauthenticated" || error.kind === "forbidden") {
      return {
        state: "authorization-rejected",
        message: "Access Request access was rejected by the backend.",
      };
    }
    if (error.kind === "rejected") {
      return {
        state: "validation-rejected",
        message: "Access Request values were rejected by the backend.",
      };
    }
    if (error.kind === "conflict") {
      return {
        state: "conflict",
        message:
          "The Access Request changed before this operation could be applied.",
      };
    }
  }
  return {
    state: "technical-error",
    message: "The Access Request operation failed.",
  };
}

function editorFailure(error: unknown): {
  state: EditorState;
  message: string;
} {
  const failure = detailFailure(error);
  if (failure.state === "not-found") {
    return { state: "technical-error", message: failure.message };
  }
  return {
    state: failure.state as EditorState,
    message: failure.message,
  };
}

function AccessRequestListMode() {
  const [loadState, setLoadState] = useState<CatalogueLoadState>({
    kind: "loading",
  });

  useEffect(() => {
    let active = true;
    void queryAccessRequests()
      .then((items) => {
        if (active) setLoadState({ kind: "loaded", items });
      })
      .catch((error) => {
        if (active) setLoadState(catalogueFailure(error));
      });
    return () => {
      active = false;
    };
  }, []);

  const rows = loadState.kind === "loaded" ? loadState.items : [];
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
      eyebrow="Access policy"
      title="Access Requests"
      description="Submit connectivity requests and inspect immutable permission outcomes."
      primaryAction={{
        label: "Submit Access Request",
        onInvoke: () => navigate("/access-requests/new"),
      }}
      state={state}
      statusMessage={statusMessage}
      emptyMessage="No Access Requests."
    >
      <StructuredListPattern
        label="Access Requests"
        rows={rows}
        rowKey={(row) => row.requestRef}
        primary={(row) => row.requestRef}
        secondary={(row) => row.decisionResult ?? "PENDING"}
        onOpen={(row) =>
          navigate(`/access-requests/${row.requestRef}/decision`)
        }
        emptyMessage="No Access Requests."
      />
    </CataloguePattern>
  );
}

function AccessRequestCreateMode() {
  const [source, setSource] = useState("");
  const [destination, setDestination] = useState("");
  const [revision, setRevision] = useState("");
  const [need, setNeed] = useState("");
  const [state, setState] = useState<EditorState>("editing");
  const [statusMessage, setStatusMessage] = useState<string>();

  async function submit() {
    setState("submitting");
    setStatusMessage(undefined);
    try {
      const requestRef = await submitAccessRequest({
        sourceDeploymentRef: source,
        destinationDeploymentRef: destination,
        interactionRevisionRef: revision,
        needRef: need,
      });
      navigate(`/access-requests/${requestRef}/decision`);
    } catch (error) {
      const failure = editorFailure(error);
      setState(failure.state);
      setStatusMessage(failure.message);
    }
  }

  return (
    <EditorPattern
      eyebrow="Access policy"
      title="Access Requests"
      description="Submit a connectivity request; backend admission remains authoritative."
      fields={[
        {
          id: "source-deployment-ref",
          label: "Source Deployment ID",
          value: source,
          required: true,
          onChange: setSource,
        },
        {
          id: "destination-deployment-ref",
          label: "Destination Deployment ID",
          value: destination,
          required: true,
          onChange: setDestination,
        },
        {
          id: "interaction-revision-ref",
          label: "Interaction Revision ID",
          value: revision,
          required: true,
          onChange: setRevision,
        },
        {
          id: "need-ref",
          label: "Connectivity Need ID",
          value: need,
          required: true,
          onChange: setNeed,
        },
      ]}
      submitLabel="Submit Request"
      submitDisabled={!source || !destination || !revision || !need}
      onSubmit={() => void submit()}
      state={state}
      statusMessage={statusMessage}
    />
  );
}

function AccessRequestDetailMode({ requestRef }: { requestRef: string }) {
  const [model, setModel] = useState<AccessRequestDetailScreenModel | null>(
    null,
  );
  const [state, setState] = useState<DetailState>("loading");
  const [statusMessage, setStatusMessage] = useState<string>();
  const [decision, setDecision] = useState<"ALLOWED" | "DENIED">("ALLOWED");
  const [externalDecisionRef, setExternalDecisionRef] = useState("");

  useEffect(() => {
    let active = true;
    void queryAccessRequest(requestRef)
      .then((next) => {
        if (!active) return;
        setModel(next);
        setState("loaded");
      })
      .catch((error) => {
        if (!active) return;
        const failure = detailFailure(error);
        setState(failure.state);
        setStatusMessage(failure.message);
      });
    return () => {
      active = false;
    };
  }, [requestRef]);

  async function recordDecision() {
    if (!model) return;
    setState("submitting");
    setStatusMessage(undefined);
    try {
      const result = await decideAccessRequest(
        model,
        decision,
        externalDecisionRef || undefined,
      );
      if (result.policyRuleRef) {
        navigate(`/policy-rules/${result.policyRuleRef}`);
        return;
      }
      setModel(result.request);
      setState("loaded");
    } catch (error) {
      const failure = detailFailure(error);
      setState(failure.state);
      setStatusMessage(failure.message);
    }
  }

  const decisionEditor: EditorPatternProps | undefined =
    model && !model.decisionResult
      ? {
          title: "Record Decision",
          fields: [
            {
              id: "decision",
              label: "Decision",
              value: decision,
              options: [
                { value: "ALLOWED", label: "Allowed" },
                { value: "DENIED", label: "Denied" },
              ],
              onChange: (value) => setDecision(value as "ALLOWED" | "DENIED"),
            },
            {
              id: "external-decision-ref",
              label: "External decision reference",
              value: externalDecisionRef,
              onChange: setExternalDecisionRef,
            },
          ],
          submitLabel: "Record Decision",
          onSubmit: () => void recordDecision(),
          state: state === "submitting" ? "submitting" : "editing",
        }
      : undefined;

  const sections = model
    ? [
        {
          id: "request",
          title: "Request",
          summary: (
            <div>
              <p>Source Deployment ID: {model.sourceDeploymentRef}</p>
              <p>Destination Deployment ID: {model.destinationDeploymentRef}</p>
              <p>Interaction Revision ID: {model.interactionRevisionRef}</p>
              <p>Connectivity Need ID: {model.needRef}</p>
            </div>
          ),
        },
        {
          id: "outcome",
          title: "Outcome",
          summary: (
            <OutcomePattern
              title="Request outcome"
              summary={<>Outcome: {model.decisionResult ?? "PENDING"}</>}
              tone={
                model.decisionResult === "ALLOWED"
                  ? "success"
                  : model.decisionResult === "DENIED"
                    ? "warning"
                    : "info"
              }
              details={
                model.decidedAt ? (
                  <p>
                    Decided at {model.decidedAt}
                    {model.decidedBySubject
                      ? ` by ${model.decidedBySubject}`
                      : ""}
                  </p>
                ) : undefined
              }
            />
          ),
          editors: decisionEditor ? [decisionEditor] : undefined,
        },
      ]
    : [];

  return (
    <DetailPattern
      eyebrow="Access policy"
      title="Access Requests"
      technicalContext={model?.requestRef ?? requestRef}
      version={model?.version}
      sections={sections}
      state={state}
      statusMessage={statusMessage}
      onRetry={() => window.location.reload()}
      onReturn={() => navigate("/access-requests")}
    />
  );
}

export function AccessRequestScreen({
  create = false,
  requestRef,
}: {
  create?: boolean;
  requestRef?: string;
}) {
  if (requestRef) {
    return <AccessRequestDetailMode requestRef={requestRef} />;
  }
  return create ? <AccessRequestCreateMode /> : <AccessRequestListMode />;
}
