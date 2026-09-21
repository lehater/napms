export interface AuthSession {
  accessToken(): string | null;
}

declare global {
  interface Window {
    __NAPMS_RUNTIME_ACCESS_TOKEN__?: string;
  }
}

let runtimeToken: string | null =
  typeof window !== "undefined" && window.__NAPMS_RUNTIME_ACCESS_TOKEN__
    ? window.__NAPMS_RUNTIME_ACCESS_TOKEN__
    : null;

if (typeof window !== "undefined") {
  delete window.__NAPMS_RUNTIME_ACCESS_TOKEN__;
}

export const authSession: AuthSession = {
  accessToken: () => runtimeToken,
};

export function setRuntimeAccessToken(token: string | null): void {
  runtimeToken = token;
}
