import type { AccessRequestView } from "../../app/api";

export type AccessRequestCatalogueItem = {
  requestRef: string;
  decisionResult: "ALLOWED" | "DENIED" | null;
};

export type AccessRequestDetailScreenModel = AccessRequestView;

export function toAccessRequestCatalogue(
  requests: readonly AccessRequestView[],
): AccessRequestCatalogueItem[] {
  return requests.map((request) => ({
    requestRef: request.requestRef,
    decisionResult: request.decisionResult,
  }));
}
