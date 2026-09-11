import type { ApplicationCatalogueView } from "@/features/catalogues/ApplicationCataloguePage"
import type { DeploymentInteractionSide } from "@/features/catalogues/targetCatalogueApi"
import type { RequestConnectivityContext } from "@/features/connectivity/model"

export type Route =
  | { kind: "connectivity"; page: number }
  | { kind: "checker" }
  | { kind: "applications"; page: number; view: ApplicationCatalogueView }
  | { kind: "application-definition"; applicationId: string }
  | { kind: "application-deployment"; deploymentId: string }
  | {
      kind: "deployment-resources"
      deploymentId: string
      deploymentInteractionId: string
      side: DeploymentInteractionSide
    }
  | { kind: "resources"; page: number }
  | { kind: "resource"; resourceReference: string }
  | {
      kind: "request-access"
      context: RequestConnectivityContext
      returnPage: number
    }
  | { kind: "requirements"; page: number }
  | { kind: "requirement"; requirementId: string }
  | { kind: "decisions"; page: number }
  | { kind: "decision"; decisionId: string }
  | { kind: "compose" }
  | { kind: "rules"; page: number }
  | { kind: "rule"; ruleId: string }
  | { kind: "effective" }
  | { kind: "normalized" }
  | { kind: "realization" }

function queryFromHash(hash: string) {
  return hash.includes("?") ? hash.split("?")[1] : ""
}

function pageFromHash(hash: string) {
  const page = Number(new URLSearchParams(queryFromHash(hash)).get("page") ?? "1")
  return Number.isInteger(page) && page > 0 ? page : 1
}

function catalogueViewFromHash(hash: string): ApplicationCatalogueView {
  return new URLSearchParams(queryFromHash(hash)).get("view") === "deployments"
    ? "deployments"
    : "definitions"
}

export function readRoute(): Route {
  const hash = window.location.hash.replace(/^#/, "")
  if (hash.startsWith("checker")) return { kind: "checker" }

  if (hash.startsWith("applications/definitions/")) {
    const applicationId = hash.slice("applications/definitions/".length).split("?")[0]
    if (applicationId) {
      return {
        kind: "application-definition",
        applicationId: decodeURIComponent(applicationId),
      }
    }
  }
  if (hash.startsWith("applications/deployments/")) {
    const tail = hash.slice("applications/deployments/".length).split("?")[0]
    const parts = tail.split("/").map(decodeURIComponent)
    if (
      parts.length === 5 &&
      parts[0] &&
      parts[1] === "interactions" &&
      parts[2] &&
      parts[3] === "resources" &&
      (parts[4] === "Source" || parts[4] === "Destination")
    ) {
      return {
        kind: "deployment-resources",
        deploymentId: parts[0],
        deploymentInteractionId: parts[2],
        side: parts[4],
      }
    }
    if (parts[0]) {
      return {
        kind: "application-deployment",
        deploymentId: parts[0],
      }
    }
  }
  if (hash.startsWith("applications")) {
    return {
      kind: "applications",
      page: pageFromHash(hash),
      view: catalogueViewFromHash(hash),
    }
  }

  if (hash.startsWith("resources/")) {
    const resourceReference = hash.slice("resources/".length).split("?")[0]
    if (resourceReference) {
      return {
        kind: "resource",
        resourceReference: decodeURIComponent(resourceReference),
      }
    }
  }
  if (hash.startsWith("resources")) {
    return { kind: "resources", page: pageFromHash(hash) }
  }

  if (hash.startsWith("connectivity-decisions/")) {
    const decisionId = hash.slice("connectivity-decisions/".length).split("?")[0]
    if (decisionId) {
      return {
        kind: "decision",
        decisionId: decodeURIComponent(decisionId),
      }
    }
  }
  if (hash.startsWith("connectivity-decisions")) {
    return { kind: "decisions", page: pageFromHash(hash) }
  }
  if (hash.startsWith("connectivity-needs/")) {
    const requirementId = hash.slice("connectivity-needs/".length).split("?")[0]
    if (requirementId) {
      return {
        kind: "requirement",
        requirementId: decodeURIComponent(requirementId),
      }
    }
  }
  if (hash.startsWith("connectivity-needs")) {
    return { kind: "requirements", page: pageFromHash(hash) }
  }
  if (hash.startsWith("connectivity")) {
    return { kind: "connectivity", page: pageFromHash(hash) }
  }
  if (hash.startsWith("request-access")) {
    const params = new URLSearchParams(queryFromHash(hash))
    const scope = params.get("scope")
    const localResourceReference = params.get("localResource")
    const dependentComponentDeploymentId = params.get("dependent")
    const sourceComponentDeploymentId = params.get("source")
    const destinationComponentDeploymentId = params.get("destination")
    const dcsContractRevisionId = params.get("dcs")
    const needCurrent = params.get("need")
    const returnPageValue = Number(params.get("returnPage") ?? "1")
    if (
      scope &&
      localResourceReference &&
      dependentComponentDeploymentId &&
      sourceComponentDeploymentId &&
      destinationComponentDeploymentId &&
      dcsContractRevisionId &&
      (needCurrent === "Required" || needCurrent === "None")
    ) {
      return {
        kind: "request-access",
        context: {
          scope,
          localResourceReference,
          dependentComponentDeploymentId,
          sourceComponentDeploymentId,
          destinationComponentDeploymentId,
          dcsContractRevisionId,
          needCurrent,
        },
        returnPage:
          Number.isInteger(returnPageValue) && returnPageValue > 0
            ? returnPageValue
            : 1,
      }
    }
    return { kind: "connectivity", page: 1 }
  }
  if (hash.startsWith("compose")) return { kind: "compose" }
  if (hash.startsWith("effective-policy")) return { kind: "effective" }
  if (hash.startsWith("normalized-policy")) return { kind: "normalized" }
  if (hash.startsWith("realization")) return { kind: "realization" }
  if (hash.startsWith("access-rules/")) {
    const ruleId = hash.slice("access-rules/".length).split("?")[0]
    if (ruleId) return { kind: "rule", ruleId: decodeURIComponent(ruleId) }
  }
  if (hash.startsWith("access-rules")) {
    return { kind: "rules", page: pageFromHash(hash) }
  }
  return { kind: "connectivity", page: 1 }
}

export function navigate(hash: string) {
  window.location.hash = hash
}
