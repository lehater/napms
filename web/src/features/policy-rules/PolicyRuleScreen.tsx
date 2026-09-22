import { useEffect, useState } from "react";
import { ApiError } from "../../app/api";
import { navigate } from "../../app/router";
import {
  CataloguePattern,
  type CatalogueState,
  DetailPattern,
  type DetailState,
  type EditorPatternProps,
  OutcomePattern,
  StructuredListPattern,
} from "../../presentation";
import {
  attachPolicyRuleJustification,
  queryPolicyRule,
  queryPolicyRules,
  setPolicyRuleEffectState,
} from "./policyRuleApplication";
import type {
  PolicyRuleCatalogueItem,
  PolicyRuleDetailScreenModel,
} from "./policyRuleModels";

type CatalogueLoadState =
  | { kind: "loading" }
  | { kind: "loaded"; items: PolicyRuleCatalogueItem[] }
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
  const [loadState, setLoadState] = useState<CatalogueLoadState>({
    kind: "loading",
  });

  useEffect(() => {
    let active = true;
    void queryPolicyRules()
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
      eyebrow="Desired access"
      title="Policy Rules"
      description="Inspect authoritative desired-access rules and supported operational state."
      primaryAction={{
        label: "Export Effective Policy",
        onInvoke: () => navigate("/policy-materializations/new"),
      }}
      state={state}
      statusMessage={statusMessage}
      emptyMessage="No Policy Rules."
    >
      <StructuredListPattern
        label="Policy Rules"
        rows={rows}
        rowKey={(row) => row.policyRuleRef}
        primary={(row) => row.policyRuleRef}
        secondary={(row) => row.effectState}
        onOpen={(row) => navigate(`/policy-rules/${row.policyRuleRef}`)}
        emptyMessage="No Policy Rules."
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
      void mutate((current) =>
        attachPolicyRuleJustification(current, needRef),
      ),
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
                    {model.sourceDeploymentRef} → {model.destinationDeploymentRef}
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
