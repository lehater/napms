import type { RuleDto } from "@/features/rules/model/rule"

export type ProposalResult =
  | { outcome: "Materialized" | "Resolved"; rule: RuleDto }
  | { outcome: "NotAllowed"; rule: null }
