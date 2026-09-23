import { ApiError, api } from "./api";

export type ReferenceCandidate = {
  value: string;
  label: string;
};

export async function queryComponentReferenceCandidates(
  search: string,
): Promise<ReferenceCandidate[]> {
  const page = await api.listComponents({
    ...(search.trim() ? { search } : {}),
    page: 1,
    pageSize: 20,
  });
  return page.items.map((item) => ({
    value: item.componentRef,
    label: `${item.name} — ${item.applicationName}`,
  }));
}

export async function queryInteractionReferenceCandidates(
  search: string,
): Promise<ReferenceCandidate[]> {
  const page = await api.listInteractions({
    ...(search.trim() ? { search } : {}),
    page: 1,
    pageSize: 20,
  });
  return page.items.map((item) => {
    const direction =
      `${item.sourceComponentName} — ${item.sourceApplicationName} → ` +
      `${item.destinationComponentName} — ${item.destinationApplicationName}`;
    return {
      value: item.interactionRef,
      label: item.purpose ? `${direction} — ${item.purpose}` : direction,
    };
  });
}

export async function queryInteractionParticipantCandidates(
  interactionRef: string,
): Promise<ReferenceCandidate[]> {
  const interaction = await api.getInteraction(interactionRef);
  const values = [
    {
      value: interaction.sourceComponentRef,
      label: interaction.sourceApplicationName
        ? `${interaction.sourceComponentName ?? interaction.sourceComponentRef} — ` +
          interaction.sourceApplicationName
        : (interaction.sourceComponentName ?? interaction.sourceComponentRef),
    },
    {
      value: interaction.destinationComponentRef,
      label: interaction.destinationApplicationName
        ? `${interaction.destinationComponentName ?? interaction.destinationComponentRef} — ` +
          interaction.destinationApplicationName
        : (interaction.destinationComponentName ??
          interaction.destinationComponentRef),
    },
  ];
  return values.filter(
    (candidate, index) =>
      values.findIndex((item) => item.value === candidate.value) === index,
  );
}

export async function queryResourceReferenceCandidates(
  search: string,
): Promise<ReferenceCandidate[]> {
  const page = await api.listResources({
    ...(search.trim() ? { search } : {}),
    sortBy: "displayName",
    sortDirection: "asc",
    page: 1,
    pageSize: 20,
  });
  return page.items.map((item) => ({
    value: item.resourceRef,
    label: item.displayName,
  }));
}

export function referenceCandidateFailureMessage(error: unknown): string {
  if (
    error instanceof ApiError &&
    (error.kind === "unauthenticated" || error.kind === "forbidden")
  ) {
    return "Candidate access was rejected by the backend.";
  }
  return "Candidates could not be loaded.";
}
