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
  StructuredListPattern,
} from "../../presentation";
import {
  createBusinessProcess,
  declareBusinessConnectivityNeed,
  queryBusinessProcess,
  queryBusinessProcesses,
  retireBusinessConnectivityNeed,
  setBusinessProcessCriticality,
  setResponsibleOrganization,
} from "./businessConnectivityApplication";
import type {
  BusinessProcessCatalogueItem,
  BusinessProcessDetailScreenModel,
} from "./businessConnectivityModels";

type CatalogueLoadState =
  | { kind: "loading" }
  | { kind: "loaded"; items: BusinessProcessCatalogueItem[] }
  | { kind: "authorization-rejected"; message: string }
  | { kind: "technical-error"; message: string };

function catalogueFailure(error: unknown): CatalogueLoadState {
  if (
    error instanceof ApiError &&
    (error.kind === "unauthenticated" || error.kind === "forbidden")
  ) {
    return {
      kind: "authorization-rejected",
      message: "Business Process access was rejected by the backend.",
    };
  }
  return {
    kind: "technical-error",
    message: "Business Processes could not be loaded.",
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
        message: "The requested Business Process does not exist.",
      };
    }
    if (error.kind === "unauthenticated" || error.kind === "forbidden") {
      return {
        state: "authorization-rejected",
        message: "Business Process access was rejected by the backend.",
      };
    }
    if (error.kind === "rejected") {
      return {
        state: "validation-rejected",
        message: "Business connectivity values were rejected by the backend.",
      };
    }
    if (error.kind === "conflict") {
      return {
        state: "conflict",
        message:
          "The Business Process changed before this operation could be applied.",
      };
    }
  }
  return {
    state: "technical-error",
    message:
      "The Business Connectivity workspace could not complete the operation.",
  };
}

function editorFailure(error: unknown): {
  state: EditorState;
  message: string;
} {
  const failure = detailFailure(error);
  if (failure.state === "not-found") {
    return {
      state: "technical-error",
      message: failure.message,
    };
  }
  return {
    state: failure.state as EditorState,
    message: failure.message,
  };
}

function BusinessProcessListMode() {
  const [loadState, setLoadState] = useState<CatalogueLoadState>({
    kind: "loading",
  });

  useEffect(() => {
    let active = true;
    void queryBusinessProcesses()
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
      eyebrow="Business connectivity"
      title="Business Processes"
      description="Manage business justification independently from permission outcomes."
      primaryAction={{
        label: "Create Business Process",
        onInvoke: () => navigate("/business-processes/new"),
      }}
      state={state}
      statusMessage={statusMessage}
      emptyMessage="No Business Processes."
    >
      <StructuredListPattern
        label="Business Processes"
        rows={rows}
        rowKey={(row) => row.processRef}
        primary={(row) => row.name}
        secondary={(row) =>
          `${row.processRef} · criticality ${row.criticalityLabel ?? "unset"}`
        }
        onOpen={(row) => navigate(`/business-processes/${row.processRef}`)}
        emptyMessage="No Business Processes."
      />
    </CataloguePattern>
  );
}

function BusinessProcessCreateMode() {
  const [name, setName] = useState("");
  const [description, setDescription] = useState("");
  const [criticality, setCriticality] = useState("");
  const [state, setState] = useState<EditorState>("editing");
  const [statusMessage, setStatusMessage] = useState<string>();

  async function submit() {
    setState("submitting");
    setStatusMessage(undefined);
    try {
      const processRef = await createBusinessProcess({
        name,
        ...(description ? { description } : {}),
        ...(criticality ? { criticalityLabel: criticality } : {}),
      });
      navigate(`/business-processes/${processRef}`);
    } catch (error) {
      const failure = editorFailure(error);
      setState(failure.state);
      setStatusMessage(failure.message);
    }
  }

  return (
    <EditorPattern
      eyebrow="Business connectivity"
      title="Business Processes"
      fields={[
        {
          id: "name",
          label: "Name",
          value: name,
          required: true,
          onChange: setName,
        },
        {
          id: "description",
          label: "Description",
          value: description,
          onChange: setDescription,
        },
        {
          id: "criticality",
          label: "Criticality",
          value: criticality,
          onChange: setCriticality,
        },
      ]}
      submitLabel="Create Business Process"
      submitDisabled={!name}
      onSubmit={() => void submit()}
      state={state}
      statusMessage={statusMessage}
    />
  );
}

function BusinessProcessDetailMode({ processRef }: { processRef: string }) {
  const [model, setModel] = useState<BusinessProcessDetailScreenModel | null>(
    null,
  );
  const [state, setState] = useState<DetailState>("loading");
  const [statusMessage, setStatusMessage] = useState<string>();
  const [criticality, setCriticality] = useState("");
  const [organizationRef, setOrganizationRef] = useState("");
  const [organizationName, setOrganizationName] = useState("");
  const [interactionRef, setInteractionRef] = useState("");
  const [componentRef, setComponentRef] = useState("");
  const [basis, setBasis] = useState("");

  useEffect(() => {
    let active = true;
    void queryBusinessProcess(processRef)
      .then((next) => {
        if (!active) return;
        setModel(next);
        setCriticality(next.criticalityLabel ?? "");
        setOrganizationRef(next.organizationExternalReference ?? "");
        setOrganizationName(next.organizationDisplayName ?? "");
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
  }, [processRef]);

  async function mutate(
    operation: (
      current: BusinessProcessDetailScreenModel,
    ) => Promise<BusinessProcessDetailScreenModel>,
  ) {
    if (!model) return;
    setState("submitting");
    setStatusMessage(undefined);
    try {
      const next = await operation(model);
      setModel(next);
      setCriticality(next.criticalityLabel ?? "");
      setOrganizationRef(next.organizationExternalReference ?? "");
      setOrganizationName(next.organizationDisplayName ?? "");
      setState("loaded");
    } catch (error) {
      const failure = detailFailure(error);
      setState(failure.state);
      setStatusMessage(failure.message);
    }
  }

  const editorState: EditorPatternProps["state"] =
    state === "submitting" ? "submitting" : "editing";

  const organizationEditor: EditorPatternProps = {
    title: "Responsible organization",
    fields: [
      {
        id: "organization-ref",
        label: "Responsible organization reference",
        value: organizationRef,
        onChange: setOrganizationRef,
      },
      {
        id: "organization-name",
        label: "Responsible organization name",
        value: organizationName,
        onChange: setOrganizationName,
      },
    ],
    submitLabel: "Save responsible organization",
    onSubmit: () =>
      void mutate((current) =>
        setResponsibleOrganization(
          current,
          organizationRef || null,
          organizationName || null,
        ),
      ),
    state: editorState,
  };

  const criticalityEditor: EditorPatternProps = {
    title: "Criticality",
    fields: [
      {
        id: "criticality",
        label: "Criticality",
        value: criticality,
        onChange: setCriticality,
      },
    ],
    submitLabel: "Save criticality",
    onSubmit: () =>
      void mutate((current) =>
        setBusinessProcessCriticality(current, criticality || null),
      ),
    state: editorState,
  };

  const needEditor: EditorPatternProps = {
    title: "Declare Connectivity Need",
    fields: [
      {
        id: "interaction-ref",
        label: "Interaction ID",
        value: interactionRef,
        required: true,
        onChange: setInteractionRef,
      },
      {
        id: "participant-component-ref",
        label: "Participant Component ID",
        value: componentRef,
        required: true,
        onChange: setComponentRef,
      },
      {
        id: "business-basis",
        label: "Business basis",
        value: basis,
        required: true,
        onChange: setBasis,
      },
    ],
    submitLabel: "Declare Connectivity Need",
    submitDisabled: !interactionRef || !componentRef || !basis,
    onSubmit: () =>
      void mutate((current) =>
        declareBusinessConnectivityNeed(current, {
          interactionRef,
          participantComponentRef: componentRef,
          businessBasis: basis,
        }),
      ),
    state: editorState,
  };

  const sections = model
    ? [
        {
          id: "process",
          title: model.name,
          summary: (
            <p>
              {model.description || "No description"} · criticality{" "}
              {model.criticalityLabel || "unset"}
            </p>
          ),
          editors: [organizationEditor, criticalityEditor],
        },
        {
          id: "needs",
          title: "Connectivity Needs",
          summary: (
            <StructuredListPattern
              label="Connectivity Needs"
              rows={model.needs}
              rowKey={(row) => row.needRef}
              primary={(row) => row.businessBasis}
              secondary={(row) =>
                `${row.needRef} · ${row.status} · Interaction ${row.interactionRef} · Participant ${row.participantComponentRef}`
              }
              rowAction={(row) => ({
                label: "Retire Connectivity Need",
                disabled: row.status !== "ACTIVE",
                onInvoke: () =>
                  void mutate((current) =>
                    retireBusinessConnectivityNeed(current, row.needRef),
                  ),
              })}
              emptyMessage="No Connectivity Needs."
            />
          ),
          editors: [needEditor],
        },
      ]
    : [];

  return (
    <DetailPattern
      eyebrow="Business connectivity"
      title="Business Processes"
      technicalContext={model?.processRef ?? processRef}
      version={model?.version}
      sections={sections}
      state={state}
      statusMessage={statusMessage}
      onRetry={() => window.location.reload()}
      onReturn={() => navigate("/business-processes")}
    />
  );
}

export function BusinessConnectivityScreen({
  create = false,
  processRef,
}: {
  create?: boolean;
  processRef?: string;
}) {
  if (processRef) {
    return <BusinessProcessDetailMode processRef={processRef} />;
  }
  return create ? <BusinessProcessCreateMode /> : <BusinessProcessListMode />;
}
