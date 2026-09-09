import { useEffect, useState } from "react"

import { getSession, login, logout, type Actor } from "@/api"
import { AppShell } from "@/components/layout/AppShell"
import { LoginPage } from "@/features/auth/LoginPage"
import { ConnectivityPage } from "@/features/connectivity/ConnectivityPage"
import type { RequestConnectivityContext } from "@/features/connectivity/model"
import { RequestConnectivityPage } from "@/features/connectivity/RequestConnectivityPage"
import { EffectivePolicyPage } from "@/features/policy/EffectivePolicyPage"
import { NormalizedPolicyPage } from "@/features/policy/NormalizedPolicyPage"
import { ComposeConnectivityPage } from "@/features/proposals/ComposeConnectivityPage"
import { ConnectivityRequirementDetailsPage } from "@/features/requirements/ConnectivityRequirementDetailsPage"
import { ConnectivityRequirementsPage } from "@/features/requirements/ConnectivityRequirementsPage"
import { AccessRuleDetailsPage } from "@/features/rules/AccessRuleDetailsPage"
import { AccessRulesPage } from "@/features/rules/AccessRulesPage"

type Route =
  | { kind: "connectivity"; page: number }
  | {
      kind: "request-access"
      context: RequestConnectivityContext
      returnPage: number
    }
  | { kind: "requirements"; page: number }
  | { kind: "requirement"; requirementId: string }
  | { kind: "compose" }
  | { kind: "rules"; page: number }
  | { kind: "rule"; ruleId: string }
  | { kind: "effective" }
  | { kind: "normalized" }

function readRoute(): Route {
  const hash = window.location.hash.replace(/^#/, "")
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
    const query = hash.includes("?") ? hash.split("?")[1] : ""
    const page = Number(new URLSearchParams(query).get("page") ?? "1")
    return {
      kind: "requirements",
      page: Number.isInteger(page) && page > 0 ? page : 1,
    }
  }
  if (hash.startsWith("connectivity")) {
    const query = hash.includes("?") ? hash.split("?")[1] : ""
    const page = Number(new URLSearchParams(query).get("page") ?? "1")
    return {
      kind: "connectivity",
      page: Number.isInteger(page) && page > 0 ? page : 1,
    }
  }
  if (hash.startsWith("request-access")) {
    const query = hash.includes("?") ? hash.split("?")[1] : ""
    const params = new URLSearchParams(query)
    const scope = params.get("scope")
    const dependentComponentDeploymentId = params.get("dependent")
    const sourceComponentDeploymentId = params.get("source")
    const destinationComponentDeploymentId = params.get("destination")
    const dcsContractRevisionId = params.get("dcs")
    const needCurrent = params.get("need")
    const returnPageValue = Number(params.get("returnPage") ?? "1")
    if (
      scope &&
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
  if (hash.startsWith("access-rules/")) {
    const ruleId = hash.slice("access-rules/".length).split("?")[0]
    if (ruleId) return { kind: "rule", ruleId: decodeURIComponent(ruleId) }
  }
  if (hash.startsWith("access-rules")) {
    const query = hash.includes("?") ? hash.split("?")[1] : ""
    const page = Number(new URLSearchParams(query).get("page") ?? "1")
    return {
      kind: "rules",
      page: Number.isInteger(page) && page > 0 ? page : 1,
    }
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
    route.kind === "connectivity" ||
    route.kind === "request-access" ||
    route.kind === "compose"
      ? "connectivity"
      : route.kind === "requirements" || route.kind === "requirement"
        ? "requirements"
        : route.kind === "effective"
          ? "effective"
          : route.kind === "normalized"
            ? "normalized"
            : "rules"

  return (
    <AppShell
      actor={actor}
      activeNav={activeNav}
      onNavigate={(target) =>
        navigate(
          target === "connectivity"
            ? "connectivity?page=1"
            : target === "requirements"
              ? "connectivity-needs?page=1"
              : target === "rules"
                ? "access-rules?page=1"
                : target === "effective"
                  ? "effective-policy"
                  : "normalized-policy",
        )
      }
      onLogout={async () => {
        await logout()
        setActor(null)
      }}
    >
      {route.kind === "connectivity" ? (
        <ConnectivityPage
          page={route.page}
          onPageChange={(page) => navigate(`connectivity?page=${page}`)}
          onRequestAccess={(context) => {
            const params = new URLSearchParams({
              scope: context.scope,
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
          onBack={() =>
            navigate(`connectivity?page=${route.returnPage}`)
          }
        />
      ) : route.kind === "requirements" ? (
        <ConnectivityRequirementsPage
          page={route.page}
          onPageChange={(page) =>
            navigate(`connectivity-needs?page=${page}`)
          }
          onOpenRequirement={(requirementId) =>
            navigate(
              `connectivity-needs/${encodeURIComponent(requirementId)}`,
            )
          }
        />
      ) : route.kind === "requirement" ? (
        <ConnectivityRequirementDetailsPage
          requirementId={route.requirementId}
          onBack={() => navigate("connectivity-needs?page=1")}
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
        />
      )}
    </AppShell>
  )
}
