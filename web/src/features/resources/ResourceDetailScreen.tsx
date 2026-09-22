import { useEffect, useState } from "react";
import { ApiError } from "../../app/api";
import { navigate } from "../../app/router";
import {
  DetailPattern,
  type DetailState,
  type EditorPatternProps,
} from "../../presentation";
import {
  addResourceEndpoint,
  clearResourceAddress,
  queryResourceDetail,
  setResourceAddress,
  setResourceResponsibility,
  setResourceSite,
} from "./resourceDetailApplication";
import {
  hasEmptyCurrent,
  type ResourceDetailScreenModel,
} from "./resourceDetailModel";

function loadedState(model: ResourceDetailScreenModel): DetailState {
  return hasEmptyCurrent(model) ? "empty-current" : "loaded";
}

function failureState(
  error: unknown,
  phase: "load" | "mutation",
): { state: DetailState; message: string } {
  if (error instanceof ApiError) {
    if (phase === "load" && error.kind === "not-found") {
      return {
        state: "not-found",
        message: "The requested Resource does not exist.",
      };
    }
    if (error.kind === "unauthenticated" || error.kind === "forbidden") {
      return {
        state: "authorization-rejected",
        message: "Resource access was rejected by the backend.",
      };
    }
    if (phase === "mutation" && error.kind === "rejected") {
      return {
        state: "validation-rejected",
        message: "The submitted Resource values were rejected by the backend.",
      };
    }
    if (phase === "mutation" && error.kind === "conflict") {
      return {
        state: "conflict",
        message: "The Resource changed before this operation could be applied.",
      };
    }
  }
  return {
    state: "technical-error",
    message:
      phase === "load"
        ? "The Resource could not be loaded."
        : "The Resource operation failed.",
  };
}

export function ResourceDetailScreen({ resourceRef }: { resourceRef: string }) {
  const [model, setModel] = useState<ResourceDetailScreenModel | null>(null);
  const [state, setState] = useState<DetailState>("loading");
  const [statusMessage, setStatusMessage] = useState<string>();
  const [siteRef, setSiteRef] = useState("");
  const [endpointRef, setEndpointRef] = useState("");
  const [addressKind, setAddressKind] = useState("HOST");
  const [addressValue, setAddressValue] = useState("");
  const [role, setRole] = useState<"OWNER" | "ADMINISTRATOR">("OWNER");
  const [organizationRef, setOrganizationRef] = useState("");

  useEffect(() => {
    let active = true;
    setModel(null);
    setState("loading");
    setStatusMessage(undefined);

    void queryResourceDetail(resourceRef)
      .then((next) => {
        if (!active) return;
        setModel(next);
        setSiteRef(next.siteRef ?? "");
        setState(loadedState(next));
      })
      .catch((error) => {
        if (!active) return;
        const failure = failureState(error, "load");
        setState(failure.state);
        setStatusMessage(failure.message);
      });

    return () => {
      active = false;
    };
  }, [resourceRef]);

  async function retry() {
    setState("loading");
    setStatusMessage(undefined);
    try {
      const next = await queryResourceDetail(resourceRef);
      setModel(next);
      setSiteRef(next.siteRef ?? "");
      setState(loadedState(next));
    } catch (error) {
      const failure = failureState(error, "load");
      setState(failure.state);
      setStatusMessage(failure.message);
    }
  }

  async function mutate(
    operation: (
      current: ResourceDetailScreenModel,
    ) => Promise<ResourceDetailScreenModel>,
  ) {
    if (!model) return;
    setState("submitting");
    setStatusMessage(undefined);
    try {
      const next = await operation(model);
      setModel(next);
      setSiteRef(next.siteRef ?? "");
      setState(loadedState(next));
    } catch (error) {
      const failure = failureState(error, "mutation");
      setState(failure.state);
      setStatusMessage(failure.message);
    }
  }

  const editorState: EditorPatternProps["state"] =
    state === "submitting" ? "submitting" : "editing";

  const siteEditor: EditorPatternProps = {
    title: "Edit site",
    description: "Leave Site ID blank to clear the current assignment.",
    fields: [
      {
        id: "site-ref",
        label: "Site ID",
        value: siteRef,
        onChange: setSiteRef,
      },
    ],
    submitLabel: "Save site",
    onSubmit: () =>
      void mutate((current) => setResourceSite(current, siteRef || null)),
    state: editorState,
  };

  const addressEditor: EditorPatternProps = {
    title: "Endpoint address",
    fields: [
      {
        id: "endpoint-ref",
        label: "Endpoint ID",
        value: endpointRef,
        required: true,
        onChange: setEndpointRef,
      },
      {
        id: "address-kind",
        label: "Address kind",
        value: addressKind,
        options: [
          { value: "HOST", label: "HOST" },
          { value: "PREFIX", label: "PREFIX" },
        ],
        onChange: setAddressKind,
      },
      {
        id: "address-value",
        label: "Address value",
        value: addressValue,
        required: true,
        onChange: setAddressValue,
      },
    ],
    submitLabel: "Set endpoint address",
    submitDisabled: !endpointRef || !addressValue,
    secondaryAction: {
      label: "Clear endpoint address",
      disabled: !endpointRef,
      onInvoke: () =>
        void mutate((current) => clearResourceAddress(current, endpointRef)),
    },
    onSubmit: () =>
      void mutate((current) =>
        setResourceAddress(current, endpointRef, {
          kind: addressKind,
          value: addressValue,
        }),
      ),
    state: editorState,
  };

  const responsibilityEditor: EditorPatternProps = {
    title: "Responsibility",
    description:
      "Leave Organization ID blank to clear the selected responsibility.",
    fields: [
      {
        id: "responsibility-role",
        label: "Responsibility role",
        value: role,
        options: [
          { value: "OWNER", label: "OWNER" },
          { value: "ADMINISTRATOR", label: "ADMINISTRATOR" },
        ],
        onChange: (value) => setRole(value as "OWNER" | "ADMINISTRATOR"),
      },
      {
        id: "organization-ref",
        label: "Organization ID",
        value: organizationRef,
        onChange: setOrganizationRef,
      },
    ],
    submitLabel: "Save responsibility",
    onSubmit: () =>
      void mutate((current) =>
        setResourceResponsibility(current, role, organizationRef || null),
      ),
    state: editorState,
  };

  const sections = model
    ? [
        {
          id: "site",
          title: "Site",
          summary: <p>{model.siteRef ?? "No site assigned."}</p>,
          editors: [siteEditor],
        },
        {
          id: "endpoints",
          title: "Endpoints",
          summary:
            model.endpoints.length === 0 ? (
              <p>No endpoints.</p>
            ) : (
              model.endpoints.map((endpoint) => (
                <p key={endpoint.endpointRef}>
                  <code>{endpoint.endpointRef}</code>
                  {" · "}
                  {endpoint.addressSummary}
                </p>
              ))
            ),
          actions: [
            {
              label: "Add endpoint",
              onInvoke: () =>
                void mutate((current) => addResourceEndpoint(current)),
            },
          ],
          editors: [addressEditor],
        },
        {
          id: "responsibilities",
          title: "Responsibilities",
          summary:
            model.responsibilities.length === 0 ? (
              <p>No responsibilities.</p>
            ) : (
              model.responsibilities.map((item) => (
                <p key={item.role}>
                  {item.role}: {item.organizationRef}
                </p>
              ))
            ),
          editors: [responsibilityEditor],
        },
      ]
    : [];

  return (
    <DetailPattern
      eyebrow="Resource detail"
      title={model?.displayName ?? "Resource"}
      technicalContext={
        model
          ? `${model.resourceRef} · authority ${model.authorityScopeRef}`
          : resourceRef
      }
      description="Inspect current Resource facts, author supported changes, and review temporal history."
      version={model?.version}
      sections={sections}
      secondary={
        model
          ? {
              label: "Provenance and history",
              content: <pre>{JSON.stringify(model.history, null, 2)}</pre>,
            }
          : undefined
      }
      state={state}
      statusMessage={statusMessage}
      onRetry={() => void retry()}
      onReturn={() => navigate("/resources")}
    />
  );
}
