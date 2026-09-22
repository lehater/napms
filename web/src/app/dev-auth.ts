export type DevelopmentAuthErrorKind = "rejected" | "unavailable";

export class DevelopmentAuthError extends Error {
  readonly kind: DevelopmentAuthErrorKind;

  constructor(kind: DevelopmentAuthErrorKind) {
    super(kind);
    this.kind = kind;
  }
}

export async function developmentLogin(
  login: string,
  password: string,
): Promise<string> {
  const response = await fetch("/dev-auth/login", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ login, password }),
  });

  if (response.status === 401) {
    throw new DevelopmentAuthError("rejected");
  }
  if (!response.ok) {
    throw new DevelopmentAuthError("unavailable");
  }

  const payload: unknown = await response.json();
  if (
    typeof payload !== "object" ||
    payload === null ||
    !("accessToken" in payload) ||
    typeof payload.accessToken !== "string" ||
    payload.accessToken.length === 0
  ) {
    throw new DevelopmentAuthError("unavailable");
  }
  return payload.accessToken;
}
