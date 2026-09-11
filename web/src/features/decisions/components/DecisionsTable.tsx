import { ChevronRight } from "lucide-react"

import {
  CatalogueIdentity,
  displayName,
  shortId,
} from "@/features/catalogues/components/CatalogueIdentity"
import type { ConnectivityDecisionDto } from "@/features/decisions/api"
import {
  DecisionOutcomeStatus,
  decisionValidityText,
} from "@/features/decisions/components/DecisionStatus"

export function DecisionsTable({
  decisions,
  onOpenDecision,
}: {
  decisions: ConnectivityDecisionDto[]
  onOpenDecision: (decisionId: string) => void
}) {
  return (
    <div className="overflow-x-auto">
      <table className="w-full min-w-[1050px] text-left text-sm">
        <thead className="bg-[#F8FAFC] text-xs uppercase tracking-wide text-[#64748B]">
          <tr>
            <th className="px-4 py-3 font-semibold">Subject</th>
            <th className="px-4 py-3 font-semibold">Scope</th>
            <th className="px-4 py-3 font-semibold">Outcome</th>
            <th className="px-4 py-3 font-semibold">Validity</th>
            <th className="px-4 py-3 font-semibold">Supersession</th>
            <th className="w-12 px-4 py-3" aria-label="Open" />
          </tr>
        </thead>
        <tbody>
          {decisions.map((decision) => (
            <tr
              key={decision.decisionId}
              className="border-t border-[#E2E8F0] align-top hover:bg-[#F8FAFC]"
            >
              <td className="px-4 py-3">
                <div className="grid gap-2">
                  <CatalogueIdentity
                    name={decision.catalogue?.sourceDisplayName}
                    id={decision.subject.sourceComponentDeploymentId}
                  />
                  <div className="text-xs font-semibold text-[#64748B]">to</div>
                  <CatalogueIdentity
                    name={decision.catalogue?.destinationDisplayName}
                    id={decision.subject.destinationComponentDeploymentId}
                  />
                  <div className="text-xs text-[#475569]">
                    Access:{" "}
                    {displayName(
                      decision.catalogue?.dcsDisplayName,
                      decision.subject.dcsContractRevisionId,
                    )}
                  </div>
                </div>
              </td>
              <td className="px-4 py-3">{decision.governanceScope}</td>
              <td className="px-4 py-3">
                <DecisionOutcomeStatus outcome={decision.outcome} />
              </td>
              <td className="px-4 py-3 text-xs text-[#475569]">
                {decisionValidityText(decision)}
              </td>
              <td className="px-4 py-3 text-xs text-[#475569]">
                {decision.supersedesDecisionId
                  ? `Supersedes ${shortId(decision.supersedesDecisionId)}`
                  : "Original"}
              </td>
              <td className="px-4 py-3">
                <button
                  type="button"
                  aria-label={`Open Decision ${decision.decisionId}`}
                  className="grid size-8 place-items-center rounded-md text-[#64748B] hover:bg-[#E2E8F0]"
                  onClick={() => onOpenDecision(decision.decisionId)}
                >
                  <ChevronRight className="size-4" aria-hidden="true" />
                </button>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}
