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
