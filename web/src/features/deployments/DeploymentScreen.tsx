import { useEffect, useMemo, useState } from "react";
import { ApiError } from "../../app/api";
import { navigate } from "../../app/router";
import {
  CataloguePattern,
  type CatalogueState,
  type DataTableColumn,
  DataTablePattern,
  EditorPattern,
  type EditorState,
  FilterBarPattern,
} from "../../presentation";
import { createDeployment, queryDeployments } from "./deploymentApplication";
import {
  type DeploymentCatalogueQueryState,
  defaultDeploymentCatalogueQuery,
} from "./deploymentCatalogueQuery";
import type {
  DeploymentCatalogueItem,
  DeploymentScreenModel,
} from "./deploymentModels";

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
  const [query, setQuery] = useState<DeploymentCatalogueQueryState>(
    defaultDeploymentCatalogueQuery,
  );
  const [loadState, setLoadState] = useState<LoadState>({ kind: "loading" });

  useEffect(() => {
    let active = true;
    setLoadState({ kind: "loading" });
    void queryDeployments(query)
      .then((model) => {
        if (active) setLoadState({ kind: "loaded", model });
      })
      .catch((error) => {
        if (active) setLoadState(loadFailure(error));
      });
    return () => {
      active = false;
    };
  }, [query]);

  function updateQuery(
    patch: Partial<DeploymentCatalogueQueryState>,
    resetPage = true,
  ) {
    setQuery((current) => ({
      ...current,
      ...patch,
      page: resetPage ? 1 : (patch.page ?? current.page),
    }));
  }

  const columns = useMemo<readonly DataTableColumn<DeploymentCatalogueItem>[]>(
    () => [
      {
        id: "deployment-reference",
        label: "Deployment",
        emphasis: "primary",
        sortKey: "deploymentRef",
        render: (row) => row.deploymentRef,
      },
      {
        id: "component-reference",
        label: "Component",
        emphasis: "technical",
        sortKey: "componentRef",
        render: (row) => row.componentRef,
      },
      {
        id: "resource-reference",
        label: "Resource",
        emphasis: "technical",
        sortKey: "resourceRef",
        render: (row) => row.resourceRef,
      },
    ],
    [],
  );

  const model = loadState.kind === "loaded" ? loadState.model : undefined;
  const rows = model?.deployments ?? [];
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
    query.componentRef !== "" ||
    query.resourceRef !== "" ||
    query.sortBy !== defaultDeploymentCatalogueQuery.sortBy ||
    query.sortDirection !== defaultDeploymentCatalogueQuery.sortDirection ||
    query.pageSize !== defaultDeploymentCatalogueQuery.pageSize;

  return (
    <CataloguePattern
      eyebrow="Deployment management"
      title="Deployments"
      description="Locate Component deployments and inspect the Resource realizing each deployment."
      primaryAction={{
        label: "Create Deployment",
        onInvoke: () => navigate("/deployments/new"),
      }}
      state={state}
      statusMessage={statusMessage}
      emptyMessage="No Deployments match the current query."
      queryControls={
        <FilterBarPattern
          search={{
            label: "Search Deployments",
            value: query.search,
            placeholder: "Deployment, Component, or Resource ID",
            onChange: (value) => updateQuery({ search: value }),
          }}
          filters={[
            {
              id: "component-ref",
              label: "Component ID",
              value: query.componentRef,
              onChange: (value) => updateQuery({ componentRef: value }),
            },
            {
              id: "resource-ref",
              label: "Resource ID",
              value: query.resourceRef,
              onChange: (value) => updateQuery({ resourceRef: value }),
            },
          ]}
          sort={{
            field: query.sortBy,
            fields: [
              { value: "deploymentRef", label: "Deployment" },
              { value: "componentRef", label: "Component" },
              { value: "resourceRef", label: "Resource" },
            ],
            direction: query.sortDirection,
            onFieldChange: (field) =>
              updateQuery({
                sortBy: field as DeploymentCatalogueQueryState["sortBy"],
              }),
            onDirectionChange: (sortDirection) =>
              updateQuery({ sortDirection }),
          }}
          active={queryActive}
          onClear={() => setQuery(defaultDeploymentCatalogueQuery)}
        />
      }
    >
      <DataTablePattern
        label="Deployments"
        rows={rows}
        columns={columns}
        rowKey={(row) => row.deploymentRef}
        onOpen={(row) => navigate(`/deployments/${row.deploymentRef}`)}
        sort={{
          field: query.sortBy,
          direction: query.sortDirection,
          onChange: (field, sortDirection) =>
            updateQuery({
              sortBy: field as DeploymentCatalogueQueryState["sortBy"],
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
        emptyMessage="No Deployments match the current query."
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
      const deploymentRef = await createDeployment({
        componentRef,
        resourceRef,
      });
      navigate(`/deployments/${deploymentRef}`);
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

export function DeploymentScreen({ create = false }: { create?: boolean }) {
  return create ? <DeploymentCreateMode /> : <DeploymentListMode />;
}
