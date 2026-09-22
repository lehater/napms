import { useEffect, useMemo, useState } from "react";
import { ApiError } from "../../app/api";
import { navigate } from "../../app/router";
import {
  CataloguePattern,
  type CatalogueState,
  type DataTableColumn,
  DataTablePattern,
  type EditorField,
  EditorPattern,
  type EditorState,
  FilterBarPattern,
} from "../../presentation";
import {
  createResource,
  queryResourceCatalogue,
} from "./resourceCatalogueApplication";
import {
  defaultResourceCatalogueQuery,
  type ResourceCatalogueQueryState,
} from "./resourceCatalogueQuery";
import type {
  ResourceCatalogueItem,
  ResourceCatalogueScreenModel,
} from "./resourceCatalogueModel";

type LoadState =
  | { kind: "loading" }
  | { kind: "loaded"; model: ResourceCatalogueScreenModel }
  | { kind: "authorization-rejected"; message: string }
  | { kind: "technical-error"; message: string };

function rejectedLoadState(error: unknown): LoadState {
  if (
    error instanceof ApiError &&
    (error.kind === "forbidden" || error.kind === "unauthenticated")
  ) {
    return {
      kind: "authorization-rejected",
      message: "Resource catalogue access was rejected by the backend.",
    };
  }
  return {
    kind: "technical-error",
    message: "Resource catalogue could not be loaded.",
  };
}

function createFailureState(error: unknown): {
  state: EditorState;
  message: string;
} {
  if (error instanceof ApiError) {
    if (error.kind === "rejected") {
      return {
        state: "validation-rejected",
        message: "Resource values were rejected by the backend.",
      };
    }
    if (error.kind === "forbidden" || error.kind === "unauthenticated") {
      return {
        state: "authorization-rejected",
        message: "Resource creation was rejected by the backend.",
      };
    }
    if (error.kind === "conflict") {
      return {
        state: "conflict",
        message: "Resource creation conflicts with current server state.",
      };
    }
  }
  return {
    state: "technical-error",
    message: "Resource creation failed.",
  };
}

function ResourceCatalogueListMode() {
  const [query, setQuery] = useState<ResourceCatalogueQueryState>(
    defaultResourceCatalogueQuery,
  );
  const [loadState, setLoadState] = useState<LoadState>({ kind: "loading" });

  useEffect(() => {
    let active = true;
    setLoadState({ kind: "loading" });
    void queryResourceCatalogue(query)
      .then((model) => {
        if (active) setLoadState({ kind: "loaded", model });
      })
      .catch((error) => {
        if (active) setLoadState(rejectedLoadState(error));
      });
    return () => {
      active = false;
    };
  }, [query]);

  function updateQuery(
    patch: Partial<ResourceCatalogueQueryState>,
    resetPage = true,
  ) {
    setQuery((current) => ({
      ...current,
      ...patch,
      page: resetPage ? 1 : (patch.page ?? current.page),
    }));
  }

  const columns = useMemo<readonly DataTableColumn<ResourceCatalogueItem>[]>(
    () => [
      {
        id: "display-name",
        label: "Name",
        emphasis: "primary",
        sortKey: "displayName",
        render: (row) => row.displayName,
      },
      {
        id: "resource-reference",
        label: "Reference",
        emphasis: "technical",
        sortKey: "resourceRef",
        render: (row) => row.resourceRef,
      },
      {
        id: "authority-scope",
        label: "Authority scope",
        sortKey: "authorityScopeRef",
        render: (row) => row.authorityScopeRef,
      },
      { id: "site", label: "Site", render: (row) => row.site },
      { id: "endpoints", label: "Endpoints", render: (row) => row.endpoints },
      {
        id: "responsibilities",
        label: "Responsibilities",
        render: (row) => row.responsibilities,
      },
    ],
    [],
  );

  const model = loadState.kind === "loaded" ? loadState.model : undefined;
  const rows = model?.resources ?? [];
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
    query.authorityScopeRef !== "" ||
    query.siteRef !== "" ||
    query.sortBy !== defaultResourceCatalogueQuery.sortBy ||
    query.sortDirection !== defaultResourceCatalogueQuery.sortDirection ||
    query.pageSize !== defaultResourceCatalogueQuery.pageSize;

  return (
    <CataloguePattern
      eyebrow="Resource catalogue"
      title="Resources"
      description="Locate a Resource by stable identity and inspect current facts before history."
      primaryAction={{
        label: "Create Resource",
        onInvoke: () => navigate("/resources/new"),
      }}
      state={state}
      statusMessage={statusMessage}
      emptyMessage="No Resources match the current query."
      queryControls={
        <FilterBarPattern
          search={{
            label: "Search Resources",
            value: query.search,
            placeholder: "Name or Resource ID",
            onChange: (value) => updateQuery({ search: value }),
          }}
          filters={[
            {
              id: "authority-scope-ref",
              label: "Authority scope",
              value: query.authorityScopeRef,
              onChange: (value) => updateQuery({ authorityScopeRef: value }),
            },
            {
              id: "site-ref",
              label: "Site ID",
              value: query.siteRef,
              onChange: (value) => updateQuery({ siteRef: value }),
            },
          ]}
          sort={{
            field: query.sortBy,
            fields: [
              { value: "displayName", label: "Name" },
              { value: "resourceRef", label: "Reference" },
              { value: "authorityScopeRef", label: "Authority scope" },
            ],
            direction: query.sortDirection,
            onFieldChange: (field) =>
              updateQuery({
                sortBy: field as ResourceCatalogueQueryState["sortBy"],
              }),
            onDirectionChange: (sortDirection) =>
              updateQuery({ sortDirection }),
          }}
          active={queryActive}
          onClear={() => setQuery(defaultResourceCatalogueQuery)}
        />
      }
    >
      <DataTablePattern
        label="Resources"
        rows={rows}
        columns={columns}
        rowKey={(row) => row.resourceRef}
        onOpen={(row) => navigate(`/resources/${row.resourceRef}`)}
        sort={{
          field: query.sortBy,
          direction: query.sortDirection,
          onChange: (field, sortDirection) =>
            updateQuery({
              sortBy: field as ResourceCatalogueQueryState["sortBy"],
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
        emptyMessage="No Resources match the current query."
      />
    </CataloguePattern>
  );
}

function ResourceCatalogueCreateMode() {
  const [displayName, setDisplayName] = useState("");
  const [authorityScopeRef, setAuthorityScopeRef] = useState("");
  const [siteRef, setSiteRef] = useState("");
  const [state, setState] = useState<EditorState>("editing");
  const [statusMessage, setStatusMessage] = useState<string>();

  const fields = useMemo<readonly EditorField[]>(
    () => [
      {
        id: "display-name",
        label: "Display name",
        value: displayName,
        required: true,
        onChange: setDisplayName,
      },
      {
        id: "authority-scope-ref",
        label: "Authority scope",
        value: authorityScopeRef,
        required: true,
        onChange: setAuthorityScopeRef,
      },
      {
        id: "site-ref",
        label: "Initial site ID",
        value: siteRef,
        onChange: setSiteRef,
      },
    ],
    [authorityScopeRef, displayName, siteRef],
  );

  async function submit() {
    setState("submitting");
    setStatusMessage(undefined);
    try {
      const resourceRef = await createResource({
        displayName,
        authorityScopeRef,
        ...(siteRef ? { siteRef } : {}),
      });
      navigate(`/resources/${resourceRef}`);
    } catch (error) {
      const failure = createFailureState(error);
      setState(failure.state);
      setStatusMessage(failure.message);
    }
  }

  return (
    <EditorPattern
      eyebrow="Create Resource"
      title="Resources"
      description="Create a Resource using the accepted catalogue contract."
      fields={fields}
      submitLabel="Create Resource"
      submitDisabled={!displayName || !authorityScopeRef}
      onSubmit={() => void submit()}
      state={state}
      statusMessage={statusMessage}
    />
  );
}

export function ResourceCatalogueScreen({
  create = false,
}: {
  create?: boolean;
}) {
  return create ? (
    <ResourceCatalogueCreateMode />
  ) : (
    <ResourceCatalogueListMode />
  );
}
