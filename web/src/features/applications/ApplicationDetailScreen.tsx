import { useEffect, useState } from "react";
import { ApiError } from "../../app/api";
import { navigate } from "../../app/router";
import {
  type DataTableColumn,
  DataTablePattern,
  DetailPattern,
  type DetailState,
  type EditorPatternProps,
  StructuredListPattern,
} from "../../presentation";
import {
  addApplicationComponent,
  queryApplicationDetail,
} from "./applicationApplication";
import type { ApplicationDetailScreenModel } from "./applicationModels";

function failureState(error: unknown): {
  state: DetailState;
  message: string;
} {
  if (error instanceof ApiError) {
    if (error.kind === "not-found") {
      return {
        state: "not-found",
        message: "The requested Application does not exist.",
      };
    }
    if (error.kind === "unauthenticated" || error.kind === "forbidden") {
      return {
        state: "authorization-rejected",
        message: "Application access was rejected by the backend.",
      };
    }
    if (error.kind === "rejected") {
      return {
        state: "validation-rejected",
        message: "Application values were rejected by the backend.",
      };
    }
    if (error.kind === "conflict") {
      return {
        state: "conflict",
        message:
          "The Application changed before this operation could be applied.",
      };
    }
  }
  return {
    state: "technical-error",
    message: "The Application workspace could not complete the operation.",
  };
}

const INTERACTION_COLUMNS: readonly DataTableColumn<
  ApplicationDetailScreenModel["interactions"][number]
>[] = [
  {
    id: "source",
    label: "Source",
    emphasis: "technical",
    render: (row) => row.sourceComponentRef,
  },
  {
    id: "destination",
    label: "Destination",
    emphasis: "technical",
    render: (row) => row.destinationComponentRef,
  },
  {
    id: "purpose",
    label: "Purpose",
    render: (row) => row.purpose || "No stated purpose",
  },
  {
    id: "interaction",
    label: "Interaction ID",
    emphasis: "technical",
    render: (row) => row.interactionRef,
  },
  {
    id: "revisions",
    label: "Revisions",
    render: (row) =>
      row.revisions.length === 0 ? (
        "No revisions."
      ) : (
        <div>
          {row.revisions.map((revision) => (
            <div
              key={revision.interactionRevisionRef}
              data-interaction-revision-ref={revision.interactionRevisionRef}
            >
              <strong>Revision {revision.revisionNo}</strong>
              <p data-presentation-technical-context>
                Revision ID: {revision.interactionRevisionRef}
              </p>
              <pre>{JSON.stringify(revision.trafficClauses, null, 2)}</pre>
            </div>
          ))}
        </div>
      ),
  },
];

export function ApplicationDetailScreen({
  applicationRef,
  createComponent = false,
}: {
  applicationRef: string;
  createComponent?: boolean;
}) {
  const [model, setModel] = useState<ApplicationDetailScreenModel | null>(null);
  const [state, setState] = useState<DetailState>("loading");
  const [statusMessage, setStatusMessage] = useState<string>();
  const [componentName, setComponentName] = useState("");

  useEffect(() => {
    let active = true;
    setModel(null);
    setState("loading");
    setStatusMessage(undefined);
    void queryApplicationDetail(applicationRef)
      .then((next) => {
        if (!active) return;
        setModel(next);
        setState("loaded");
      })
      .catch((error) => {
        if (!active) return;
        const failure = failureState(error);
        setState(failure.state);
        setStatusMessage(failure.message);
      });
    return () => {
      active = false;
    };
  }, [applicationRef]);

  async function addComponent() {
    if (!model) return;
    setState("submitting");
    setStatusMessage(undefined);
    try {
      const next = await addApplicationComponent(model, componentName);
      setModel(next);
      setComponentName("");
      setState("loaded");
      navigate(`/applications/${next.applicationRef}`);
    } catch (error) {
      const failure = failureState(error);
      setState(failure.state);
      setStatusMessage(failure.message);
    }
  }

  const componentEditor: EditorPatternProps = {
    title: "Add Component",
    fields: [
      {
        id: "component-name",
        label: "Component name",
        value: componentName,
        required: true,
        onChange: setComponentName,
      },
    ],
    submitLabel: "Add Component",
    submitDisabled: !componentName,
    onSubmit: () => void addComponent(),
    state: state === "submitting" ? "submitting" : "editing",
    embedded: true,
  };

  const sections = model
    ? [
        {
          id: "components",
          title: "Components",
          summary: (
            <StructuredListPattern
              label="Components"
              rows={model.components}
              rowKey={(row) => row.componentRef}
              primary={(row) => (
                <>
                  {row.name} · {row.componentRef}
                </>
              )}
              emptyMessage="No Components."
            />
          ),
          actions: createComponent
            ? undefined
            : [
                {
                  label: "Add Component",
                  onInvoke: () =>
                    navigate(
                      `/applications/${model.applicationRef}/components/new`,
                    ),
                },
              ],
          editors: createComponent ? [componentEditor] : undefined,
        },
        {
          id: "interactions",
          title: "Interactions",
          summary: (
            <DataTablePattern
              label="Interactions"
              rows={model.interactions}
              columns={INTERACTION_COLUMNS}
              rowKey={(row) => row.interactionRef}
              rowAction={(row) => ({
                label: "Publish Revision",
                onInvoke: () =>
                  navigate(`/interactions/${row.interactionRef}/revisions/new`),
              })}
              emptyMessage="No Interactions."
            />
          ),
          actions: [
            {
              label: "Create Interaction",
              onInvoke: () => navigate("/interactions/new"),
            },
          ],
        },
      ]
    : [];

  return (
    <DetailPattern
      eyebrow="Application detail"
      title={model?.name ?? "Application"}
      technicalContext={model?.applicationRef ?? applicationRef}
      version={model?.version}
      sections={sections}
      state={state}
      statusMessage={statusMessage}
      onRetry={() => window.location.reload()}
      onReturn={() => navigate("/applications")}
    />
  );
}
