import { useEffect, useMemo, useState } from "react";
import { ApiError } from "../../app/api";
import { navigate } from "../../app/router";
import {
  type CatalogueColumn,
  CataloguePattern,
  type CatalogueState,
  type EditorField,
  EditorPattern,
  type EditorState,
} from "../../presentation";
import {
  createResource,
  queryResourceCatalogue,
} from "./resourceCatalogueApplication";
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
  const [loadState, setLoadState] = useState<LoadState>({ kind: "loading" });

  useEffect(() => {
    let active = true;
    void queryResourceCatalogue()
      .then((model) => {
        if (active) setLoadState({ kind: "loaded", model });
      })
      .catch((error) => {
        if (active) setLoadState(rejectedLoadState(error));
      });
    return () => {
      active = false;
    };
  }, []);

  const columns = useMemo<readonly CatalogueColumn<ResourceCatalogueItem>[]>(
    () => [
      {
        id: "display-name",
        label: "Name",
        emphasis: "primary",
        render: (row) => row.displayName,
      },
      {
        id: "resource-reference",
        label: "Reference",
        emphasis: "technical",
        render: (row) => row.resourceRef,
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

  const rows = loadState.kind === "loaded" ? loadState.model.resources : [];
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
      eyebrow="Resource catalogue"
      title="Resources"
      description="Locate a Resource by stable identity and inspect current facts before history."
      rows={rows}
      columns={columns}
      rowKey={(row) => row.resourceRef}
      openColumnId="display-name"
      onOpen={(row) => navigate(`/resources/${row.resourceRef}`)}
      primaryAction={{
        label: "Create Resource",
        onInvoke: () => navigate("/resources/new"),
      }}
      state={state}
      statusMessage={statusMessage}
      emptyMessage="No Resources."
    />
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
      eyebrow="Resource catalogue"
      title="Create Resource"
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
