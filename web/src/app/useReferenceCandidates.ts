import { useEffect, useState } from "react";
import type { ReferenceCandidate } from "./referenceCandidates";

export function useReferenceCandidates(
  load: (search: string) => Promise<ReferenceCandidate[]>,
  enabled = true,
) {
  const [search, setSearch] = useState("");
  const [options, setOptions] = useState<ReferenceCandidate[]>([]);
  const [loading, setLoading] = useState(enabled);
  const [error, setError] = useState<unknown>();

  useEffect(() => {
    if (!enabled) {
      setLoading(false);
      return;
    }
    let active = true;
    setLoading(true);
    setError(undefined);
    const timeout = window.setTimeout(() => {
      void load(search)
        .then((next) => {
          if (!active) return;
          setOptions(next);
          setLoading(false);
        })
        .catch((failure) => {
          if (!active) return;
          setOptions([]);
          setError(failure);
          setLoading(false);
        });
    }, 150);
    return () => {
      active = false;
      window.clearTimeout(timeout);
    };
  }, [enabled, load, search]);

  return { search, setSearch, options, loading, error };
}
