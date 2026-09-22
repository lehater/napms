import { useEffect, useMemo, useState } from "react";
import { ApiError } from "../../app/api";
import { navigate } from "../../app/router";
import {
  type CatalogueColumn,
  CataloguePattern,
  type CatalogueState,
} from "../../presentation";
import { queryResourceCatalogue } from "./resourceCatalogueApplication";
import type {
  ResourceCatalogueItem,
  ResourceCatalogueScreenModel,
} from "./resourceCatalogueModel";

type LoadState =
  | { kind: "loading" }
  | { kind: "loaded"; model: ResourceCatalogueScreenModel }
  | { kind: "authorization-rejected"; message: string }
  | { kind: "technical-error"; message: string };

function rejectedState(error: unknown): LoadState {
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

export function ResourceCatalogueScreen() {
  const [loadState, setLoadState] = useState<LoadState>({ kind: "loading" });

  useEffect(() => {
    let active = true;
    void queryResourceCatalogue()
      .then((model) => {
        if (active) setLoadState({ kind: "loaded", model });
      })
      .catch((error) => {
        if (active) setLoadState(rejectedState(error));
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
