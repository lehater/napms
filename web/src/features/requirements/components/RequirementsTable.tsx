import { ChevronRight } from "lucide-react"

import {
  displayName,
} from "@/features/catalogues/components/CatalogueIdentity"
import type {
  ConnectivityRequirementDto,
  RequirementPolicyAlignmentStatus,
} from "@/features/requirements/api"
import {
  RequirementAlignmentStatus,
  RequirementLifecycleStatus,
  requirementApplicabilityText,
} from "@/features/requirements/components/RequirementStatus"

export function RequirementsTable({
  requirements,
  alignmentById,
  loadingAlignment,
  onOpenRequirement,
}: {
  requirements: ConnectivityRequirementDto[]
  alignmentById: Record<string, RequirementPolicyAlignmentStatus>
  loadingAlignment: boolean
  onOpenRequirement: (requirementId: string) => void
}) {
  return (
    <div className="overflow-x-auto">
      <table className="w-full min-w-[980px] text-left text-sm">
        <thead className="bg-[#F8FAFC] text-xs uppercase tracking-wide text-[#64748B]">
          <tr>
            <th className="px-4 py-3 font-semibold">Interaction</th>
            <th className="px-4 py-3 font-semibold">Dependent</th>
            <th className="px-4 py-3 font-semibold">Scope</th>
            <th className="px-4 py-3 font-semibold">Applicability</th>
            <th className="px-4 py-3 font-semibold">Policy coverage</th>
            <th className="px-4 py-3 font-semibold">Lifecycle</th>
            <th className="w-12 px-4 py-3" aria-label="Open" />
          </tr>
        </thead>
        <tbody>
          {requirements.map((item) => {
            const interaction = item.requiredInteraction
            const dependentName =
              item.dependentComponentDeploymentId ===
              interaction.sourceComponentDeploymentId
                ? displayName(
                    item.catalogue?.sourceDisplayName,
                    interaction.sourceComponentDeploymentId,
                  )
                : displayName(
                    item.catalogue?.destinationDisplayName,
                    interaction.destinationComponentDeploymentId,
                  )
            const alignment = alignmentById[item.requirementId]

            return (
              <tr
                key={item.requirementId}
                className="border-t border-[#E2E8F0] align-top hover:bg-[#F8FAFC]"
              >
                <td className="px-4 py-3">
                  <div className="font-medium text-[#172033]">
                    {displayName(
                      item.catalogue?.sourceDisplayName,
                      interaction.sourceComponentDeploymentId,
                    )}{" "}
                    →{" "}
                    {displayName(
                      item.catalogue?.destinationDisplayName,
                      interaction.destinationComponentDeploymentId,
                    )}
                  </div>
                  <div className="mt-1 text-xs text-[#64748B]">
                    {displayName(
                      item.catalogue?.dcsDisplayName,
                      interaction.dcsContractRevisionId,
                    )}
                  </div>
                </td>
                <td className="px-4 py-3">{dependentName}</td>
                <td className="px-4 py-3">{item.governanceScope}</td>
                <td className="px-4 py-3 text-xs text-[#475569]">
                  {requirementApplicabilityText(item.applicability)}
                </td>
                <td className="px-4 py-3">
                  {alignment ? (
                    <RequirementAlignmentStatus status={alignment} />
                  ) : loadingAlignment ? (
                    <span className="text-xs text-[#64748B]">Loading…</span>
                  ) : (
                    <span className="text-xs text-[#64748B]">—</span>
                  )}
                </td>
                <td className="px-4 py-3">
                  <RequirementLifecycleStatus state={item.lifecycleState} />
                </td>
                <td className="px-4 py-3">
                  <button
                    type="button"
                    aria-label={`Open Requirement ${item.requirementId}`}
                    className="grid size-8 place-items-center rounded-md text-[#64748B] hover:bg-[#E2E8F0]"
                    onClick={() => onOpenRequirement(item.requirementId)}
                  >
                    <ChevronRight className="size-4" aria-hidden="true" />
                  </button>
                </td>
              </tr>
            )
          })}
        </tbody>
      </table>
    </div>
  )
}
