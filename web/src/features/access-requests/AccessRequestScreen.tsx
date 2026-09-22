import { useEffect, useMemo, useState } from "react";
import { ApiError } from "../../app/api";
import { navigate } from "../../app/router";
import {
  CataloguePattern,
  type CatalogueState,
  type DataTableColumn,
  DataTablePattern,
  DetailPattern,
  type DetailState,
  EditorPattern,
  type EditorPatternProps,
  type EditorState,
  FilterBarPattern,
  OutcomePattern,
} from "../../presentation";
import {
  decideAccessRequest,
  queryAccessRequest,
  queryAccessRequests,
  submitAccessRequest,
} from "./accessRequestApplication";
import {
  type AccessRequestCatalogueQueryState,
  defaultAccessRequestCatalogueQuery,
} from "./accessRequestCatalogueQuery";
import type {
  AccessRequestCatalogueItem,
  AccessRequestCatalogueScreenModel,
  AccessRequestDetailScreenModel,
} from "./accessRequestModels";

type CatalogueLoadState =
  | { kind: "loading" }
  | { kind: "loaded"; model: AccessRequestCatalogueScreenModel }
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
  const [query, setQuery] = useState<AccessRequestCatalogueQueryState>(
    defaultAccessRequestCatalogueQuery,
  );
  const [loadState, setLoadState] = useState<CatalogueLoadState>({
    kind: "loading",
  });

  useEffect(() => {
    let active = true;
    setLoadState({ kind: "loading" });
    void queryAccessRequests(query)
      .then((model) => {
        if (active) setLoadState({ kind: "loaded", model });
      })
      .catch((error) => {
        if (active) setLoadState(catalogueFailure(error));
      });
    return () => {
      active = false;
    };
  }, [query]);

  function updateQuery(
    patch: Partial<AccessRequestCatalogueQueryState>,
    resetPage = true,
  ) {
    setQuery((current) => ({
      ...current,
      ...patch,
      page: resetPage ? 1 : (patch.page ?? current.page),
    }));
  }

  const columns = useMemo<
    readonly DataTableColumn<AccessRequestCatalogueItem>[]
  >(
    () => [
      {
        id: "request-reference",
        label: "Request",
        emphasis: "primary",
        sortKey: "requestRef",
        render: (row) => row.requestRef,
      },
      {
        id: "decision",
        label: "Decision",
        sortKey: "decisionResult",
        render: (row) => row.decisionResult ?? "PENDING",
      },
      {
        id: "source-deployment",
        label: "Source Deployment",
        emphasis: "technical",
        render: (row) => row.sourceDeploymentRef,
      },
      {
        id: "destination-deployment",
        label: "Destination Deployment",
        emphasis: "technical",
        render: (row) => row.destinationDeploymentRef,
      },
      {
        id: "submitted-at",
        label: "Submitted",
        sortKey: "submittedAt",
        render: (row) => row.submittedAt,
      },
    ],
    [],
  );

  const model = loadState.kind === "loaded" ? loadState.model : undefined;
  const rows = model?.requests ?? [];
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
  const queryActive =
    query.search !== "" ||
    query.sourceDeploymentRef !== "" ||
    query.destinationDeploymentRef !== "" ||
    query.decisionResult !== "" ||
    query.sortBy !== defaultAccessRequestCatalogueQuery.sortBy ||
    query.sortDirection !==
      defaultAccessRequestCatalogueQuery.sortDirection ||
    query.pageSize !== defaultAccessRequestCatalogueQuery.pageSize;

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
      emptyMessage="No Access Requests match the current query."
      queryControls={
        <FilterBarPattern
          search={{
            label: "Search Access Requests",
            value: query.search,
            placeholder: "Request ID",
            onChange: (value) => updateQuery({ search: value }),
          }}
          filters={[
            {
              id: "source-deployment-ref",
              label: "Source Deployment ID",
              value: query.sourceDeploymentRef,
              onChange: (value) => updateQuery({ sourceDeploymentRef: value }),
            },
            {
              id: "destination-deployment-ref",
              label: "Destination Deployment ID",
              value: query.destinationDeploymentRef,
              onChange: (value) =>
                updateQuery({ destinationDeploymentRef: value }),
            },
            {
              id: "decision-result",
              label: "Decision",
              value: query.decisionResult,
              options: [
                { value: "", label: "Any decision" },
                { value: "ALLOWED", label: "Allowed" },
                { value: "DENIED", label: "Denied" },
              ],
              onChange: (value) =>
                updateQuery({
                  decisionResult:
                    value as AccessRequestCatalogueQueryState["decisionResult"],
                }),
            },
          ]}
          sort={{
            field: query.sortBy,
            fields: [
              { value: "submittedAt", label: "Submitted" },
              { value: "requestRef", label: "Request" },
              { value: "decisionResult", label: "Decision" },
            ],
            direction: query.sortDirection,
            onFieldChange: (field) =>
              updateQuery({
                sortBy: field as AccessRequestCatalogueQueryState["sortBy"],
              }),
            onDirectionChange: (sortDirection) =>
              updateQuery({ sortDirection }),
          }}
          active={queryActive}
          onClear={() => setQuery(defaultAccessRequestCatalogueQuery)}
        />
      }
    >
      <DataTablePattern
        label="Access Requests"
        rows={rows}
        columns={columns}
        rowKey={(row) => row.requestRef}
        onOpen={(row) =>
          navigate(`/access-requests/${row.requestRef}/decision`)
        }
        sort={{
          field: query.sortBy,
          direction: query.sortDirection,
          onChange: (field, sortDirection) =>
            updateQuery({
              sortBy: field as AccessRequestCatalogueQueryState["sortBy"],
              sortDirection,
            }),
        }}
        paging={{
          page: model?.page ?? query.page,
          pageSize: model?.pageSize ?? query.pageSize,
          total: model?.total ?? 0,
          onPageChange: (page) => updateQuery({ page }, false),
          onPageSizeChange: (pageSize) => updateQuery({ pageSize }),
        }}
        emptyMessage="No Access Requests match the current query."
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
