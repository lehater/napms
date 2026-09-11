import { useEffect, useState } from "react"

import { AppShell } from "@/app/AppShell"
import { navigate, readRoute, type Route } from "@/app/routing"
import { getSession, login, logout } from "@/features/auth/api/session"
import type { Actor } from "@/features/auth/model/actor"
import { LoginPage } from "@/features/auth/pages/LoginPage"
import {
  ApplicationCataloguePage,
  type ApplicationCatalogueView,
} from "@/features/catalogues/ApplicationCataloguePage"
import { ApplicationDefinitionPage } from "@/features/catalogues/ApplicationDefinitionPage"
import { ApplicationDeploymentPage } from "@/features/catalogues/ApplicationDeploymentPage"
import { DeploymentResourceSetPage } from "@/features/catalogues/DeploymentResourceSetPage"
import { ResourceDetailsPage } from "@/features/catalogues/ResourceDetailsPage"
import { ResourcesPage } from "@/features/catalogues/ResourcesPage"
import type { DeploymentInteractionSide } from "@/features/catalogues/targetCatalogueApi"
import { CheckerPage } from "@/features/checker/CheckerPage"
import { ConnectivityPage } from "@/features/connectivity/ConnectivityPage"
import { RequestConnectivityPage } from "@/features/connectivity/RequestConnectivityPage"
import type { RequestConnectivityContext } from "@/features/connectivity/model"
import { ConnectivityDecisionDetailsPage } from "@/features/decisions/ConnectivityDecisionDetailsPage"
import { ConnectivityDecisionsPage } from "@/features/decisions/ConnectivityDecisionsPage"
import { EffectivePolicyPage } from "@/features/policy/EffectivePolicyPage"
import { NormalizedPolicyPage } from "@/features/policy/NormalizedPolicyPage"
import { ComposeConnectivityPage } from "@/features/proposals/pages/ComposeConnectivityPage"
import { NetworkOperatorRealizationPage } from "@/features/realization/NetworkOperatorRealizationPage"
import { ConnectivityRequirementDetailsPage } from "@/features/requirements/ConnectivityRequirementDetailsPage"
import { ConnectivityRequirementsPage } from "@/features/requirements/ConnectivityRequirementsPage"
import { AccessRuleDetailsPage } from "@/features/rules/AccessRuleDetailsPage"
import { AccessRulesPage } from "@/features/rules/AccessRulesPage"


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
          route.kind === "application-deployment" ||
          route.kind === "deployment-resources"
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
          onOpenResources={(interactionId, side) =>
            navigate(
              `applications/deployments/${encodeURIComponent(route.deploymentId)}/interactions/${encodeURIComponent(interactionId)}/resources/${side}`,
            )
          }
        />
      ) : route.kind === "deployment-resources" ? (
        <DeploymentResourceSetPage
          deploymentInteractionId={route.deploymentInteractionId}
          side={route.side}
          onBack={() =>
            navigate(`applications/deployments/${encodeURIComponent(route.deploymentId)}`)
          }
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
