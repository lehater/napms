import { useEffect, useState } from "react";
import { ApiError } from "../../app/api";
import { navigate } from "../../app/router";
import {
  CataloguePattern,
  type CatalogueState,
  EditorPattern,
  type EditorState,
  StructuredListPattern,
} from "../../presentation";
import {
  createApplication,
  queryApplicationCatalogue,
} from "./applicationApplication";
import type { ApplicationCatalogueScreenModel } from "./applicationModels";

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
  const [loadState, setLoadState] = useState<LoadState>({ kind: "loading" });

  useEffect(() => {
    let active = true;
    void queryApplicationCatalogue()
      .then((model) => {
        if (active) setLoadState({ kind: "loaded", model });
      })
      .catch((error) => {
        if (active) setLoadState(loadFailure(error));
      });
    return () => {
      active = false;
    };
  }, []);

  const rows =
    loadState.kind === "loaded" ? loadState.model.applications : [];
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
      eyebrow="Application catalogue"
      title="Applications"
      description="Locate reusable Applications and continue authoring their Components and Interactions."
      primaryAction={{
        label: "Create Application",
        onInvoke: () => navigate("/applications/new"),
      }}
      state={state}
      statusMessage={statusMessage}
      emptyMessage="No Applications."
    >
      <StructuredListPattern
        label="Applications"
        rows={rows}
        rowKey={(row) => row.applicationRef}
        primary={(row) => row.name}
        secondary={(row) => row.applicationRef}
        onOpen={(row) => navigate(`/applications/${row.applicationRef}`)}
        emptyMessage="No Applications."
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
