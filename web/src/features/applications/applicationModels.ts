import type {
  ApplicationView,
  CataloguePage,
  InteractionView,
} from "../../app/api";

export type ApplicationCatalogueItem = {
  applicationRef: string;
  name: string;
  components: string;
};

export type ApplicationCatalogueScreenModel = {
  applications: ApplicationCatalogueItem[];
  total: number;
  page: number;
  pageSize: number;
};

export type ApplicationDetailScreenModel = {
  applicationRef: string;
  name: string;
  version: number;
  components: readonly {
    componentRef: string;
    name: string;
  }[];
  interactions: readonly InteractionView[];
};

export function toApplicationCatalogueScreenModel(
  page: CataloguePage<ApplicationView>,
): ApplicationCatalogueScreenModel {
  return {
    applications: page.items.map((application) => ({
      applicationRef: application.applicationRef,
      name: application.name,
      components:
        application.components.length > 0
          ? application.components.map((component) => component.name).join(", ")
          : "No components",
    })),
    total: page.total,
    page: page.page,
    pageSize: page.pageSize,
  };
}

export function toApplicationDetailScreenModel(
  application: ApplicationView,
): ApplicationDetailScreenModel {
  return {
    applicationRef: application.applicationRef,
    name: application.name,
    version: application.version,
    components: application.components.map((component) => ({
      componentRef: component.componentRef,
      name: component.name,
    })),
    interactions: application.interactions ?? [],
  };
}
