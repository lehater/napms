import type { ResourceView } from "../../app/api";

export type ResourceCatalogueItem = {
  resourceRef: string;
  displayName: string;
  site: string;
  endpoints: string;
  responsibilities: string;
};

export type ResourceCatalogueScreenModel = {
  resources: ResourceCatalogueItem[];
};

function endpointSummary(resource: ResourceView): string {
  const values = resource.current.endpoints.map((endpoint) =>
    endpoint.address
      ? `${endpoint.address.kind} ${endpoint.address.value}`
      : `${endpoint.endpointRef}: no address`,
  );
  return values.length > 0 ? values.join(", ") : "No endpoints";
}

function responsibilitySummary(resource: ResourceView): string {
  const values = resource.current.responsibilities.map(
    (item) => `${item.role}: ${item.organizationRef}`,
  );
  return values.length > 0 ? values.join(", ") : "No responsibility";
}

export function toResourceCatalogueScreenModel(
  resources: readonly ResourceView[],
): ResourceCatalogueScreenModel {
  return {
    resources: resources.map((resource) => ({
      resourceRef: resource.resourceRef,
      displayName: resource.displayName,
      site: resource.current.siteRef ?? "—",
      endpoints: endpointSummary(resource),
      responsibilities: responsibilitySummary(resource),
    })),
  };
}
