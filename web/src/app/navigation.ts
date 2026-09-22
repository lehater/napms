import type { Route } from "./router";

export type NavigationItem = {
  path: string;
  label: string;
};

export type BreadcrumbItem = {
  label: string;
  path?: string;
};

export const primaryNavigation: readonly NavigationItem[] = [
  { path: "/resources", label: "Resources" },
  { path: "/applications", label: "Applications" },
  { path: "/deployments", label: "Deployments" },
  { path: "/business-processes", label: "Business connectivity" },
  { path: "/access-requests", label: "Access requests" },
  { path: "/policy-rules", label: "Policy rules" },
  { path: "/policy-materializations/new", label: "Policy export" },
];

export function breadcrumbsForRoute(route: Route): readonly BreadcrumbItem[] {
  switch (route.id) {
    case "resources":
      return [{ label: "Resources" }];
    case "resource-new":
      return [
        { label: "Resources", path: "/resources" },
        { label: "New Resource" },
      ];
    case "resource-detail":
      return [
        { label: "Resources", path: "/resources" },
        { label: "Resource" },
      ];
    case "applications":
      return [{ label: "Applications" }];
    case "application-new":
      return [
        { label: "Applications", path: "/applications" },
        { label: "New Application" },
      ];
    case "application-detail":
      return [
        { label: "Applications", path: "/applications" },
        { label: "Application" },
      ];
    case "component-new":
      return [
        { label: "Applications", path: "/applications" },
        {
          label: "Application",
          path: `/applications/${encodeURIComponent(route.applicationRef)}`,
        },
        { label: "Add Component" },
      ];
    case "interaction-new":
      return [
        { label: "Applications", path: "/applications" },
        { label: "Create Interaction" },
      ];
    case "revision-new":
      return [
        { label: "Applications", path: "/applications" },
        { label: "Publish Interaction Revision" },
      ];
    case "deployments":
      return [{ label: "Deployments" }];
    case "deployment-new":
      return [
        { label: "Deployments", path: "/deployments" },
        { label: "New Deployment" },
      ];
    case "deployment-detail":
      return [
        { label: "Deployments", path: "/deployments" },
        { label: "Deployment" },
      ];
    case "processes":
      return [{ label: "Business connectivity" }];
    case "process-new":
      return [
        { label: "Business connectivity", path: "/business-processes" },
        { label: "New Business Process" },
      ];
    case "process-detail":
      return [
        { label: "Business connectivity", path: "/business-processes" },
        { label: "Business Process" },
      ];
    case "access-requests":
      return [{ label: "Access requests" }];
    case "access-request-new":
      return [
        { label: "Access requests", path: "/access-requests" },
        { label: "New Access Request" },
      ];
    case "access-request-decision":
      return [
        { label: "Access requests", path: "/access-requests" },
        { label: "Access Request" },
      ];
    case "policy-rules":
      return [{ label: "Policy rules" }];
    case "policy-rule-detail":
      return [
        { label: "Policy rules", path: "/policy-rules" },
        { label: "Policy Rule" },
      ];
    case "policy-export":
      return [{ label: "Policy export" }];
  }
}
