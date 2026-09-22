import type { CataloguePage, ResourceView } from "../../app/api";

export type ResourceCatalogueItem = {
  resourceRef: string;
  displayName: string;
  authorityScopeRef: string;
  site: string;
  endpoints: string;
  responsibilities: string;
};

export type ResourceCatalogueScreenModel = {
  resources: ResourceCatalogueItem[];
  total: number;
  page: number;
  pageSize: number;
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
  page: CataloguePage<ResourceView>,
): ResourceCatalogueScreenModel {
  return {
    resources: page.items.map((resource) => ({
      resourceRef: resource.resourceRef,
      displayName: resource.displayName,
      authorityScopeRef: resource.authorityScopeRef,
      site: resource.current.siteRef ?? "—",
      endpoints: endpointSummary(resource),
      responsibilities: responsibilitySummary(resource),
    })),
    total: page.total,
    page: page.page,
    pageSize: page.pageSize,
  };
}
