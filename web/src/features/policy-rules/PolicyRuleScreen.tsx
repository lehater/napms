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
  type EditorPatternProps,
  FilterBarPattern,
  OutcomePattern,
} from "../../presentation";
import {
  attachPolicyRuleJustification,
  queryPolicyRule,
  queryPolicyRules,
  setPolicyRuleEffectState,
} from "./policyRuleApplication";
import {
  type PolicyRuleCatalogueQueryState,
  defaultPolicyRuleCatalogueQuery,
} from "./policyRuleCatalogueQuery";
import type {
  PolicyRuleCatalogueItem,
  PolicyRuleCatalogueScreenModel,
  PolicyRuleDetailScreenModel,
} from "./policyRuleModels";

type CatalogueLoadState =
  | { kind: "loading" }
  | { kind: "loaded"; model: PolicyRuleCatalogueScreenModel }
  | { kind: "authorization-rejected"; message: string }
  | { kind: "technical-error"; message: string };

function catalogueFailure(error: unknown): CatalogueLoadState {
  if (
    error instanceof ApiError &&
    (error.kind === "unauthenticated" || error.kind === "forbidden")
  ) {
    return {
      kind: "authorization-rejected",
      message: "Policy Rule catalogue access was rejected by the backend.",
    };
  }
  return {
    kind: "technical-error",
    message: "Policy Rules could not be loaded.",
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
        message: "The requested Policy Rule does not exist.",
      };
    }
    if (error.kind === "unauthenticated" || error.kind === "forbidden") {
      return {
        state: "authorization-rejected",
        message: "Policy Rule access was rejected by the backend.",
      };
    }
    if (error.kind === "rejected") {
      return {
        state: "validation-rejected",
        message: "Policy Rule values were rejected by the backend.",
      };
    }
    if (error.kind === "conflict") {
      return {
        state: "conflict",
        message: "The Policy Rule changed before the operation was applied.",
      };
    }
  }
  return {
    state: "technical-error",
    message: "The Policy Rule operation failed.",
  };
}

function PolicyRuleListMode() {
  const [query, setQuery] = useState<PolicyRuleCatalogueQueryState>(
    defaultPolicyRuleCatalogueQuery,
  );
  const [loadState, setLoadState] = useState<CatalogueLoadState>({
    kind: "loading",
  });

  useEffect(() => {
    let active = true;
    setLoadState({ kind: "loading" });
    void queryPolicyRules(query)
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
    patch: Partial<PolicyRuleCatalogueQueryState>,
    resetPage = true,
  ) {
    setQuery((current) => ({
      ...current,
      ...patch,
      page: resetPage ? 1 : (patch.page ?? current.page),
    }));
  }

  const columns = useMemo<readonly DataTableColumn<PolicyRuleCatalogueItem>[]>(
    () => [
      {
        id: "policy-rule-reference",
        label: "Policy Rule",
        emphasis: "primary",
        sortKey: "policyRuleRef",
        render: (row) => row.policyRuleRef,
      },
      {
        id: "effect-state",
        label: "State",
        sortKey: "effectState",
        render: (row) => row.effectState,
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
        id: "interaction-revision",
        label: "Interaction Revision",
        emphasis: "technical",
        render: (row) => row.interactionRevisionRef,
      },
    ],
    [],
  );

  const model = loadState.kind === "loaded" ? loadState.model : undefined;
  const rows = model?.rules ?? [];
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
    query.effectState !== "" ||
    query.sortBy !== defaultPolicyRuleCatalogueQuery.sortBy ||
    query.sortDirection !== defaultPolicyRuleCatalogueQuery.sortDirection ||
    query.pageSize !== defaultPolicyRuleCatalogueQuery.pageSize;

  return (
    <CataloguePattern
      eyebrow="Desired access"
      title="Policy Rules"
      description="Inspect authoritative desired-access rules and supported operational state."
      primaryAction={{
        label: "Export Effective Policy",
        onInvoke: () => navigate("/policy-materializations/new"),
      }}
      state={state}
      statusMessage={statusMessage}
      emptyMessage="No Policy Rules match the current query."
      queryControls={
        <FilterBarPattern
          search={{
            label: "Search Policy Rules",
            value: query.search,
            placeholder: "Policy Rule ID",
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
              id: "effect-state",
              label: "State",
              value: query.effectState,
              options: [
                { value: "", label: "Any state" },
                { value: "ACTIVE", label: "Active" },
                { value: "INACTIVE", label: "Inactive" },
              ],
              onChange: (value) =>
                updateQuery({
                  effectState:
                    value as PolicyRuleCatalogueQueryState["effectState"],
                }),
            },
          ]}
          sort={{
            field: query.sortBy,
            fields: [
              { value: "policyRuleRef", label: "Policy Rule" },
              { value: "effectState", label: "State" },
            ],
            direction: query.sortDirection,
            onFieldChange: (field) =>
              updateQuery({
                sortBy: field as PolicyRuleCatalogueQueryState["sortBy"],
              }),
            onDirectionChange: (sortDirection) =>
              updateQuery({ sortDirection }),
          }}
          active={queryActive}
          onClear={() => setQuery(defaultPolicyRuleCatalogueQuery)}
        />
      }
    >
      <DataTablePattern
        label="Policy Rules"
        rows={rows}
        columns={columns}
        rowKey={(row) => row.policyRuleRef}
        onOpen={(row) => navigate(`/policy-rules/${row.policyRuleRef}`)}
        sort={{
          field: query.sortBy,
          direction: query.sortDirection,
          onChange: (field, sortDirection) =>
            updateQuery({
              sortBy: field as PolicyRuleCatalogueQueryState["sortBy"],
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
        emptyMessage="No Policy Rules match the current query."
      />
    </CataloguePattern>
  );
}

function PolicyRuleDetailMode({ ruleRef }: { ruleRef: string }) {
  const [model, setModel] = useState<PolicyRuleDetailScreenModel | null>(null);
  const [state, setState] = useState<DetailState>("loading");
  const [statusMessage, setStatusMessage] = useState<string>();
  const [needRef, setNeedRef] = useState("");

  useEffect(() => {
    let active = true;
    void queryPolicyRule(ruleRef)
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
  }, [ruleRef]);

  async function mutate(
    operation: (
      current: PolicyRuleDetailScreenModel,
    ) => Promise<PolicyRuleDetailScreenModel>,
  ) {
    if (!model) return;
    setState("submitting");
    setStatusMessage(undefined);
    try {
      const next = await operation(model);
      setModel(next);
      setState("loaded");
    } catch (error) {
      const failure = detailFailure(error);
      setState(failure.state);
      setStatusMessage(failure.message);
    }
  }

  const justificationEditor: EditorPatternProps = {
    title: "Justification",
    fields: [
      {
        id: "need-ref",
        label: "Connectivity Need ID",
        value: needRef,
        required: true,
        onChange: setNeedRef,
      },
    ],
    submitLabel: "Attach justification",
    submitDisabled: !needRef,
    onSubmit: () =>
      void mutate((current) => attachPolicyRuleJustification(current, needRef)),
    state: state === "submitting" ? "submitting" : "editing",
  };

  const sections = model
    ? [
        {
          id: "rule",
          title: "Desired access",
          summary: (
            <OutcomePattern
              title="Operational state"
              summary={model.effectState}
              tone={model.effectState === "ACTIVE" ? "success" : "info"}
              details={
                <div>
                  <p>
                    {model.sourceDeploymentRef} →{" "}
                    {model.destinationDeploymentRef}
                  </p>
                  <p>Interaction revision: {model.interactionRevisionRef}</p>
                </div>
              }
            />
          ),
          actions: [
            {
              label:
                model.effectState === "ACTIVE" ? "Set Inactive" : "Set Active",
              onInvoke: () =>
                void mutate((current) => setPolicyRuleEffectState(current)),
            },
          ],
          editors: [justificationEditor],
        },
        {
          id: "provenance",
          title: "Provenance and history",
          summary: (
            <div>
              <h3>Authorization evidence</h3>
              <pre>{JSON.stringify(model.authorizationEvidence, null, 2)}</pre>
              <h3>Justifications</h3>
              <pre>{JSON.stringify(model.justifications, null, 2)}</pre>
              <h3>Operational history</h3>
              <pre>{JSON.stringify(model.operationalHistory, null, 2)}</pre>
            </div>
          ),
        },
      ]
    : [];

  return (
    <DetailPattern
      eyebrow="Desired access"
      title="Policy Rules"
      technicalContext={model?.policyRuleRef ?? ruleRef}
      version={model?.version}
      sections={sections}
      state={state}
      statusMessage={statusMessage}
      onRetry={() => window.location.reload()}
      onReturn={() => navigate("/policy-rules")}
    />
  );
}

export function PolicyRuleScreen({ ruleRef }: { ruleRef?: string }) {
  return ruleRef ? (
    <PolicyRuleDetailMode ruleRef={ruleRef} />
  ) : (
    <PolicyRuleListMode />
  );
}
