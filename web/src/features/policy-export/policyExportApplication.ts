import { api, type PolicyMaterializationResult } from "../../app/api";

export async function materializePolicy(
  refs: string,
): Promise<PolicyMaterializationResult> {
  const selected = refs
    .split(",")
    .map((value) => value.trim())
    .filter(Boolean);
  return api.materialize(selected.length ? selected : undefined);
}
