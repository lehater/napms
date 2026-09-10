import { useEffect, useState } from "react"

import { getSession, login, logout, type Actor } from "@/api"
import { AppShell } from "@/components/layout/AppShell"
import { LoginPage } from "@/features/auth/LoginPage"
import {
  ApplicationCataloguePage,
  type ApplicationCatalogueView,
} from "@/features/catalogues/ApplicationCataloguePage"
import { ApplicationDefinitionPage } from "@/features/catalogues/ApplicationDefinitionPage"
import { ApplicationDeploymentPage } from "@/features/catalogues/ApplicationDeploymentPage"
import { ResourceDetailsPage } from "@/features/catalogues/ResourceDetailsPage"
import { ResourcesPage } from "@/features/catalogues/ResourcesPage"
import { CheckerPage } from "@/features/checker/CheckerPage"
import { ConnectivityPage } from "@/features/connectivity/ConnectivityPage"
import { RequestConnectivityPage } from "@/features/connectivity/RequestConnectivityPage"
import type { RequestConnectivityContext } from "@/features/connectivity/model"
import { ConnectivityDecisionDetailsPage } from "@/features/decisions/ConnectivityDecisionDetailsPage"
import { ConnectivityDecisionsPage } from "@/features/decisions/ConnectivityDecisionsPage"
import { EffectivePolicyPage } from "@/features/policy/EffectivePolicyPage"
import { NormalizedPolicyPage } from "@/features/policy/NormalizedPolicyPage"
import { ComposeConnectivityPage } from "@/features/proposals/ComposeConnectivityPage"
import { NetworkOperatorRealizationPage } from "@/features/realization/NetworkOperatorRealizationPage"
import { ConnectivityRequirementDetailsPage } from "@/features/requirements/ConnectivityRequirementDetailsPage"
import { ConnectivityRequirementsPage } from "@/features/requirements/ConnectivityRequirementsPage"
import { AccessRuleDetailsPage } from "@/features/rules/AccessRuleDetailsPage"
import { AccessRulesPage } from "@/features/rules/AccessRulesPage"

type Route =
  | { kind: "connectivity"; page: number }
  | { kind: "checker" }
  | { kind: "applications"; page: number; view: ApplicationCatalogueView }
  | { kind: "application-definition"; applicationId: string }
  | { kind: "application-deployment"; deploymentId: string }
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

function readRoute(): Route {
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
    const deploymentId = hash.slice("applications/deployments/".length).split("?")[0]
    if (deploymentId) {
      return {
        kind: "application-deployment",
        deploymentId: decodeURIComponent(deploymentId),
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

function navigate(hash: string) {
  window.location.hash = hash
}

export function App() {
  const [actor, setActor] = useState<Actor | null>(null)
  const [bootstrapping, setBootstrapping] = useState(true)
  const [route, setRoute] = useState<Route>(() => readRoute())

  useEffect(() => {
    const onHashChange = () => setRoute(readRoute())
    window.addEventListener("hashchange", onHashChange)
    return () => window.removeEventListener("hashchange", onHashChange)
  }, [])

  useEffect(() => {
    let active = true
    void getSession()
      .then((current) => {
        if (active) setActor(current)
      })
      .finally(() => {
        if (active) setBootstrapping(false)
      })
    return () => {
      active = false
    }
  }, [])

  if (bootstrapping) {
    return (
      <main className="grid min-h-screen place-items-center bg-[#F5F7FA] text-sm text-[#64748B]">
        Loading NAPMS…
      </main>
    )
  }

  if (!actor) {
    return (
      <LoginPage
        onLogin={async (loginName, password) => {
          const authenticated = await login(loginName, password)
          setActor(authenticated)
        }}
      />
    )
  }

  const activeNav =
    route.kind === "checker"
      ? "checker"
      : route.kind === "applications" ||
          route.kind === "application-definition" ||
          route.kind === "application-deployment"
        ? "applications"
        : route.kind === "resources" || route.kind === "resource"
          ? "resources"
          : route.kind === "connectivity" ||
              route.kind === "request-access" ||
              route.kind === "compose"
            ? "connectivity"
            : route.kind === "requirements" || route.kind === "requirement"
              ? "requirements"
              : route.kind === "decisions" || route.kind === "decision"
                ? "decisions"
                : route.kind === "effective"
                  ? "effective"
                  : route.kind === "normalized"
                    ? "normalized"
                    : route.kind === "realization"
                      ? "realization"
                      : "rules"

  return (
    <AppShell
      actor={actor}
      activeNav={activeNav}
      onNavigate={(target) =>
        navigate(
          target === "connectivity"
            ? "connectivity?page=1"
            : target === "checker"
              ? "checker"
              : target === "applications"
                ? "applications?view=definitions&page=1"
                : target === "resources"
                  ? "resources?page=1"
                  : target === "requirements"
                    ? "connectivity-needs?page=1"
                    : target === "decisions"
                      ? "connectivity-decisions?page=1"
                      : target === "rules"
                        ? "access-rules?page=1"
                        : target === "effective"
                          ? "effective-policy"
                          : target === "normalized"
                            ? "normalized-policy"
                            : "realization",
        )
      }
      onLogout={async () => {
        await logout()
        setActor(null)
      }}
    >
      {route.kind === "checker" ? (
        <CheckerPage />
      ) : route.kind === "applications" ? (
        <ApplicationCataloguePage
          view={route.view}
          page={route.page}
          onViewChange={(view) => navigate(`applications?view=${view}&page=1`)}
          onPageChange={(page) =>
            navigate(`applications?view=${route.view}&page=${page}`)
          }
          onOpenDefinition={(applicationId) =>
            navigate(`applications/definitions/${encodeURIComponent(applicationId)}`)
          }
          onOpenDeployment={(deploymentId) =>
            navigate(`applications/deployments/${encodeURIComponent(deploymentId)}`)
          }
        />
      ) : route.kind === "application-definition" ? (
        <ApplicationDefinitionPage
          applicationId={route.applicationId}
          onBack={() => navigate("applications?view=definitions&page=1")}
          onOpenDeployment={(deploymentId) =>
            navigate(`applications/deployments/${encodeURIComponent(deploymentId)}`)
          }
        />
      ) : route.kind === "application-deployment" ? (
        <ApplicationDeploymentPage
          deploymentId={route.deploymentId}
          onBack={() => navigate("applications?view=deployments&page=1")}
        />
      ) : route.kind === "resources" ? (
        <ResourcesPage
          page={route.page}
          onPageChange={(page) => navigate(`resources?page=${page}`)}
          onOpenResource={(resourceReference) =>
            navigate(`resources/${encodeURIComponent(resourceReference)}`)
          }
        />
      ) : route.kind === "resource" ? (
        <ResourceDetailsPage
          resourceReference={route.resourceReference}
          onBack={() => navigate("resources?page=1")}
        />
      ) : route.kind === "connectivity" ? (
        <ConnectivityPage
          page={route.page}
          onPageChange={(page) => navigate(`connectivity?page=${page}`)}
          onRequestAccess={(context) => {
            const params = new URLSearchParams({
              scope: context.scope,
              localResource: context.localResourceReference,
              dependent: context.dependentComponentDeploymentId,
              source: context.sourceComponentDeploymentId,
              destination: context.destinationComponentDeploymentId,
              dcs: context.dcsContractRevisionId,
              need: context.needCurrent,
              returnPage: String(route.page),
            })
            navigate(`request-access?${params}`)
          }}
        />
      ) : route.kind === "request-access" ? (
        <RequestConnectivityPage
          context={route.context}
          onBack={() => navigate(`connectivity?page=${route.returnPage}`)}
        />
      ) : route.kind === "requirements" ? (
        <ConnectivityRequirementsPage
          page={route.page}
          onPageChange={(page) => navigate(`connectivity-needs?page=${page}`)}
          onOpenRequirement={(requirementId) =>
            navigate(`connectivity-needs/${encodeURIComponent(requirementId)}`)
          }
        />
      ) : route.kind === "requirement" ? (
        <ConnectivityRequirementDetailsPage
          requirementId={route.requirementId}
          onBack={() => navigate("connectivity-needs?page=1")}
        />
      ) : route.kind === "decisions" ? (
        <ConnectivityDecisionsPage
          page={route.page}
          onPageChange={(page) => navigate(`connectivity-decisions?page=${page}`)}
          onOpenDecision={(decisionId) =>
            navigate(`connectivity-decisions/${encodeURIComponent(decisionId)}`)
          }
        />
      ) : route.kind === "decision" ? (
        <ConnectivityDecisionDetailsPage
          decisionId={route.decisionId}
          onBack={() => navigate("connectivity-decisions?page=1")}
          onOpenDecision={(decisionId) =>
            navigate(`connectivity-decisions/${encodeURIComponent(decisionId)}`)
          }
          onOpenRequirement={(requirementId) =>
            navigate(`connectivity-needs/${encodeURIComponent(requirementId)}`)
          }
        />
      ) : route.kind === "compose" ? (
        <ComposeConnectivityPage />
      ) : route.kind === "effective" ? (
        <EffectivePolicyPage
          onOpenRule={(ruleId) =>
            navigate(`access-rules/${encodeURIComponent(ruleId)}`)
          }
        />
      ) : route.kind === "normalized" ? (
        <NormalizedPolicyPage />
      ) : route.kind === "realization" ? (
        <NetworkOperatorRealizationPage
          onOpenRule={(ruleId) =>
            navigate(`access-rules/${encodeURIComponent(ruleId)}`)
          }
        />
      ) : route.kind === "rules" ? (
        <AccessRulesPage
          page={route.page}
          onPageChange={(page) => navigate(`access-rules?page=${page}`)}
          onOpenRule={(ruleId) =>
            navigate(`access-rules/${encodeURIComponent(ruleId)}`)
          }
        />
      ) : (
        <AccessRuleDetailsPage
          ruleId={route.ruleId}
          onBack={() => navigate("access-rules?page=1")}
          onOpenDecision={(decisionId) =>
            navigate(`connectivity-decisions/${encodeURIComponent(decisionId)}`)
          }
        />
      )}
    </AppShell>
  )
}
