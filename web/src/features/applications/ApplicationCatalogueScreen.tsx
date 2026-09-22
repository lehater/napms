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
import {
  createApplication,
  queryApplicationCatalogue,
} from "./applicationApplication";
import {
  type ApplicationCatalogueQueryState,
  defaultApplicationCatalogueQuery,
} from "./applicationCatalogueQuery";
import type {
  ApplicationCatalogueItem,
  ApplicationCatalogueScreenModel,
} from "./applicationModels";

type LoadState =
  | { kind: "loading" }
  | { kind: "loaded"; model: ApplicationCatalogueScreenModel }
  | { kind: "authorization-rejected"; message: string }
  | { kind: "technical-error"; message: string };

function loadFailure(error: unknown): LoadState {
  if (
    error instanceof ApiError &&
    (error.kind === "unauthenticated" || error.kind === "forbidden")
  ) {
    return {
      kind: "authorization-rejected",
      message: "Application catalogue access was rejected by the backend.",
    };
  }
  return {
    kind: "technical-error",
    message: "Application catalogue could not be loaded.",
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
        message: "Application creation was rejected by the backend.",
      };
    }
    if (error.kind === "conflict") {
      return {
        state: "conflict",
        message: "Application creation conflicts with current server state.",
      };
    }
  }
  return {
    state: "technical-error",
    message: "Application creation failed.",
  };
}

function ApplicationCatalogueListMode() {
  const [query, setQuery] = useState<ApplicationCatalogueQueryState>(
    defaultApplicationCatalogueQuery,
  );
  const [loadState, setLoadState] = useState<LoadState>({ kind: "loading" });

  useEffect(() => {
    let active = true;
    setLoadState({ kind: "loading" });
    void queryApplicationCatalogue(query)
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
    patch: Partial<ApplicationCatalogueQueryState>,
    resetPage = true,
  ) {
    setQuery((current) => ({
      ...current,
      ...patch,
      page: resetPage ? 1 : (patch.page ?? current.page),
    }));
  }

  const columns = useMemo<readonly DataTableColumn<ApplicationCatalogueItem>[]>(
    () => [
      {
        id: "name",
        label: "Name",
        emphasis: "primary",
        sortKey: "name",
        render: (row) => row.name,
      },
      {
        id: "application-reference",
        label: "Reference",
        emphasis: "technical",
        sortKey: "applicationRef",
        render: (row) => row.applicationRef,
      },
      {
        id: "components",
        label: "Components",
        render: (row) => row.components,
      },
    ],
    [],
  );

  const model = loadState.kind === "loaded" ? loadState.model : undefined;
  const rows = model?.applications ?? [];
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
    query.sortBy !== defaultApplicationCatalogueQuery.sortBy ||
    query.sortDirection !== defaultApplicationCatalogueQuery.sortDirection ||
    query.pageSize !== defaultApplicationCatalogueQuery.pageSize;

  return (
    <CataloguePattern
      eyebrow="Application catalogue"
      title="Applications"
      description="Locate reusable Applications and continue authoring their Components and Interactions."
      primaryAction={{
        label: "Create Application",
        onInvoke: () => navigate("/applications/new"),
      }}
      state={state}
      statusMessage={statusMessage}
      emptyMessage="No Applications match the current query."
      queryControls={
        <FilterBarPattern
          search={{
            label: "Search Applications",
            value: query.search,
            placeholder: "Name or Application ID",
            onChange: (value) => updateQuery({ search: value }),
          }}
          filters={[
            {
              id: "component-ref",
              label: "Component ID",
              value: query.componentRef,
              onChange: (value) => updateQuery({ componentRef: value }),
            },
          ]}
          sort={{
            field: query.sortBy,
            fields: [
              { value: "name", label: "Name" },
              { value: "applicationRef", label: "Reference" },
            ],
            direction: query.sortDirection,
            onFieldChange: (field) =>
              updateQuery({
                sortBy: field as ApplicationCatalogueQueryState["sortBy"],
              }),
            onDirectionChange: (sortDirection) =>
              updateQuery({ sortDirection }),
          }}
          active={queryActive}
          onClear={() => setQuery(defaultApplicationCatalogueQuery)}
        />
      }
    >
      <DataTablePattern
        label="Applications"
        rows={rows}
        columns={columns}
        rowKey={(row) => row.applicationRef}
        onOpen={(row) => navigate(`/applications/${row.applicationRef}`)}
        sort={{
          field: query.sortBy,
          direction: query.sortDirection,
          onChange: (field, sortDirection) =>
            updateQuery({
              sortBy: field as ApplicationCatalogueQueryState["sortBy"],
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
        emptyMessage="No Applications match the current query."
      />
    </CataloguePattern>
  );
}

function ApplicationCatalogueCreateMode() {
  const [name, setName] = useState("");
  const [state, setState] = useState<EditorState>("editing");
  const [statusMessage, setStatusMessage] = useState<string>();

  async function submit() {
    setState("submitting");
    setStatusMessage(undefined);
    try {
      const applicationRef = await createApplication(name);
      navigate(`/applications/${applicationRef}`);
    } catch (error) {
      const failure = createFailure(error);
      setState(failure.state);
      setStatusMessage(failure.message);
    }
  }

  return (
    <EditorPattern
      eyebrow="Create Application"
      title="Applications"
      description="Create a reusable Application before adding Components and directed Interactions."
      fields={[
        {
          id: "name",
          label: "Name",
          value: name,
          required: true,
          onChange: setName,
        },
      ]}
      submitLabel="Create Application"
      submitDisabled={!name}
      onSubmit={() => void submit()}
      state={state}
      statusMessage={statusMessage}
    />
  );
}

export function ApplicationCatalogueScreen({
  create = false,
}: {
  create?: boolean;
}) {
  return create ? (
    <ApplicationCatalogueCreateMode />
  ) : (
    <ApplicationCatalogueListMode />
  );
}
