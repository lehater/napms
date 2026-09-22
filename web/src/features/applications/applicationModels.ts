import type { ApplicationView, InteractionView } from "../../app/api";

export type ApplicationCatalogueItem = {
  applicationRef: string;
  name: string;
};

export type ApplicationCatalogueScreenModel = {
  applications: ApplicationCatalogueItem[];
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
  applications: readonly ApplicationView[],
): ApplicationCatalogueScreenModel {
  return {
    applications: applications.map((application) => ({
      applicationRef: application.applicationRef,
      name: application.name,
    })),
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
