import type { CataloguePresentation, ProposalInteraction } from "@/features/catalogues/model/interaction"

export type RuleDto = {
  ruleId: string
  semanticIdentity: ProposalInteraction
  governanceScope: string
  operationalState: "Active" | "Inactive"
  effectiveWindow: { start: string; end: string } | null
  decisionReference: string | null
  catalogue?: CataloguePresentation | null
}
