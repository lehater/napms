import { useEffect, useState } from "react";
import { ApiError } from "../../app/api";
import { navigate } from "../../app/router";
import { EditorPattern, type EditorState } from "../../presentation";
import {
  createApplicationInteraction,
  publishInteractionRevision,
  queryInteractionVersion,
} from "./applicationApplication";

function failureState(error: unknown): {
  state: EditorState;
  message: string;
} {
  if (error instanceof ApiError) {
    if (error.kind === "unauthenticated" || error.kind === "forbidden") {
      return {
        state: "authorization-rejected",
        message: "Interaction authoring was rejected by the backend.",
      };
    }
    if (error.kind === "rejected") {
      return {
        state: "validation-rejected",
        message: "Interaction values were rejected by the backend.",
      };
    }
    if (error.kind === "conflict") {
      return {
        state: "conflict",
        message:
          "The Interaction changed before this operation could be applied.",
      };
    }
  }
  return {
    state: "technical-error",
    message: "Interaction authoring failed.",
  };
}

export function InteractionAuthoringScreen({
  interactionRef,
}: {
  interactionRef?: string;
}) {
  const [source, setSource] = useState("");
  const [destination, setDestination] = useState("");
  const [purpose, setPurpose] = useState("");
  const [protocol, setProtocol] = useState("6");
  const [sourcePorts, setSourcePorts] = useState("");
  const [destinationPorts, setDestinationPorts] = useState("");
  const [version, setVersion] = useState<number | null>(null);
  const [state, setState] = useState<EditorState>(
    interactionRef ? "submitting" : "editing",
  );
  const [statusMessage, setStatusMessage] = useState<string>();

  useEffect(() => {
    if (!interactionRef) return;
    let active = true;
    void queryInteractionVersion(interactionRef)
      .then((nextVersion) => {
        if (!active) return;
        setVersion(nextVersion);
        setState("editing");
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
  }, [interactionRef]);

  async function submit() {
    setState("submitting");
    setStatusMessage(undefined);
    try {
      if (interactionRef) {
        if (version === null) return;
        await publishInteractionRevision({
          interactionRef,
          version,
          protocol,
          sourcePorts,
          destinationPorts,
        });
        setState("editing");
        setStatusMessage("Revision published.");
        return;
      }

      const createdRef = await createApplicationInteraction({
        sourceComponentRef: source,
        destinationComponentRef: destination,
        ...(purpose ? { purpose } : {}),
      });
      navigate(`/interactions/${createdRef}/revisions/new`);
    } catch (error) {
      const failure = failureState(error);
      setState(failure.state);
      setStatusMessage(failure.message);
    }
  }

  return (
    <EditorPattern
      eyebrow="Application detail"
      title={
        interactionRef ? "Publish interaction revision" : "Create interaction"
      }
      description={
        interactionRef
          ? "Publish a new immutable traffic revision for this directed Interaction."
          : "Create a directed Interaction between two existing Components."
      }
      fields={
        interactionRef
          ? [
              {
                id: "interaction-ref",
                label: "Interaction ID",
                value: interactionRef,
                readOnly: true,
              },
              {
                id: "current-version",
                label: "Current version",
                value: version === null ? "" : String(version),
                readOnly: true,
              },
              {
                id: "ip-protocol",
                label: "IP protocol number",
                value: protocol,
                onChange: setProtocol,
              },
              {
                id: "source-ports",
                label: "Source ports",
                value: sourcePorts,
                onChange: setSourcePorts,
              },
              {
                id: "destination-ports",
                label: "Destination ports",
                value: destinationPorts,
                onChange: setDestinationPorts,
              },
            ]
          : [
              {
                id: "source-component-ref",
                label: "Source Component ID",
                value: source,
                required: true,
                onChange: setSource,
              },
              {
                id: "destination-component-ref",
                label: "Destination Component ID",
                value: destination,
                required: true,
                onChange: setDestination,
              },
              {
                id: "purpose",
                label: "Purpose",
                value: purpose,
                onChange: setPurpose,
              },
            ]
      }
      submitLabel={interactionRef ? "Publish revision" : "Create interaction"}
      submitDisabled={
        Boolean(interactionRef && version === null) ||
        (!interactionRef && (!source || !destination))
      }
      onSubmit={() => void submit()}
      state={state}
      statusMessage={statusMessage}
    />
  );
}
