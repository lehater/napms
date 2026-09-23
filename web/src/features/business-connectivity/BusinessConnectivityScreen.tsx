import { useEffect, useMemo, useState } from "react";
import { ApiError } from "../../app/api";
import {
  queryInteractionParticipantCandidates,
  queryInteractionReferenceCandidates,
  type ReferenceCandidate,
  referenceCandidateFailureMessage,
} from "../../app/referenceCandidates";
import { navigate } from "../../app/router";
import { useReferenceCandidates } from "../../app/useReferenceCandidates";
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
  BusinessProcessCatalogueScreenModel,
  BusinessProcessDetailScreenModel,
} from "./businessConnectivityModels";
import {
  type BusinessProcessCatalogueQueryState,
  defaultBusinessProcessCatalogueQuery,
} from "./businessProcessCatalogueQuery";

type CatalogueLoadState =
  | { kind: "loading" }
  | { kind: "loaded"; model: BusinessProcessCatalogueScreenModel }
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
  const [query, setQuery] = useState<BusinessProcessCatalogueQueryState>(
    defaultBusinessProcessCatalogueQuery,
  );
  const [loadState, setLoadState] = useState<CatalogueLoadState>({
    kind: "loading",
  });

  useEffect(() => {
    let active = true;
    setLoadState({ kind: "loading" });
    void queryBusinessProcesses(query)
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
    patch: Partial<BusinessProcessCatalogueQueryState>,
    resetPage = true,
  ) {
    setQuery((current) => ({
      ...current,
      ...patch,
      page: resetPage ? 1 : (patch.page ?? current.page),
    }));
  }

  const columns = useMemo<
    readonly DataTableColumn<BusinessProcessCatalogueItem>[]
  >(
    () => [
      {
        id: "name",
        label: "Name",
        emphasis: "primary",
        sortKey: "name",
        render: (row) => row.name,
      },
      {
        id: "criticality",
        label: "Criticality",
        sortKey: "criticalityLabel",
        render: (row) => row.criticalityLabel ?? "Unset",
      },
      {
        id: "responsible-organization",
        label: "Responsible organization",
        render: (row) =>
          row.organizationDisplayName ??
          row.organizationExternalReference ??
          "Unassigned",
      },
      {
        id: "process-reference",
        label: "Reference",
        emphasis: "technical",
        sortKey: "processRef",
        render: (row) => row.processRef,
      },
    ],
    [],
  );

  const model = loadState.kind === "loaded" ? loadState.model : undefined;
  const rows = model?.processes ?? [];
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
    query.criticalityLabel !== "" ||
    query.organizationExternalReference !== "" ||
    query.sortBy !== defaultBusinessProcessCatalogueQuery.sortBy ||
    query.sortDirection !==
      defaultBusinessProcessCatalogueQuery.sortDirection ||
    query.pageSize !== defaultBusinessProcessCatalogueQuery.pageSize;

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
      emptyMessage="No Business Processes match the current query."
      queryControls={
        <FilterBarPattern
          search={{
            label: "Search Business Processes",
            value: query.search,
            placeholder: "Name or Process ID",
            onChange: (value) => updateQuery({ search: value }),
          }}
          filters={[
            {
              id: "criticality-label",
              label: "Criticality",
              value: query.criticalityLabel,
              onChange: (value) => updateQuery({ criticalityLabel: value }),
            },
            {
              id: "organization-reference",
              label: "Responsible organization reference",
              value: query.organizationExternalReference,
              onChange: (value) =>
                updateQuery({ organizationExternalReference: value }),
            },
          ]}
          sort={{
            field: query.sortBy,
            fields: [
              { value: "name", label: "Name" },
              { value: "processRef", label: "Reference" },
              { value: "criticalityLabel", label: "Criticality" },
            ],
            direction: query.sortDirection,
            onFieldChange: (field) =>
              updateQuery({
                sortBy: field as BusinessProcessCatalogueQueryState["sortBy"],
              }),
            onDirectionChange: (sortDirection) =>
              updateQuery({ sortDirection }),
          }}
          active={queryActive}
          onClear={() => setQuery(defaultBusinessProcessCatalogueQuery)}
        />
      }
    >
      <DataTablePattern
        label="Business Processes"
        rows={rows}
        columns={columns}
        rowKey={(row) => row.processRef}
        onOpen={(row) => navigate(`/business-processes/${row.processRef}`)}
        sort={{
          field: query.sortBy,
          direction: query.sortDirection,
          onChange: (field, sortDirection) =>
            updateQuery({
              sortBy: field as BusinessProcessCatalogueQueryState["sortBy"],
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
        emptyMessage="No Business Processes match the current query."
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
  const interactionCandidates = useReferenceCandidates(
    queryInteractionReferenceCandidates,
  );
  const [participantCandidates, setParticipantCandidates] = useState<
    ReferenceCandidate[]
  >([]);
  const [participantLoading, setParticipantLoading] = useState(false);
  const [participantError, setParticipantError] = useState<unknown>();

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

  useEffect(() => {
    setComponentRef("");
    setParticipantCandidates([]);
    setParticipantError(undefined);
    if (!interactionRef) {
      setParticipantLoading(false);
      return;
    }
    let active = true;
    setParticipantLoading(true);
    void queryInteractionParticipantCandidates(interactionRef)
      .then((candidates) => {
        if (!active) return;
        setParticipantCandidates(candidates);
        setParticipantLoading(false);
      })
      .catch((error) => {
        if (!active) return;
        setParticipantError(error);
        setParticipantLoading(false);
      });
    return () => {
      active = false;
    };
  }, [interactionRef]);

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
        label: "Interaction",
        value: interactionRef,
        required: true,
        onChange: (value) => {
          setInteractionRef(value);
          setComponentRef("");
        },
        referencePicker: {
          options: interactionCandidates.options,
          loading: interactionCandidates.loading,
          errorMessage: interactionCandidates.error
            ? referenceCandidateFailureMessage(interactionCandidates.error)
            : undefined,
          onSearchChange: interactionCandidates.setSearch,
        },
      },
      {
        id: "participant-component-ref",
        label: "Participant Component",
        value: componentRef,
        required: true,
        onChange: setComponentRef,
        referencePicker: {
          options: participantCandidates,
          loading: participantLoading,
          errorMessage: participantError
            ? referenceCandidateFailureMessage(participantError)
            : undefined,
          noOptionsText: interactionRef
            ? "No endpoint Components available"
            : "Select an Interaction first",
          onSearchChange: () => undefined,
        },
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
              primary={(row) => (
                <span data-connectivity-need-ref={row.needRef}>
                  {row.businessBasis}
                </span>
              )}
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
