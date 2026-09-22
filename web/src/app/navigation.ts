export type NavigationItem = {
  path: string;
  label: string;
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
