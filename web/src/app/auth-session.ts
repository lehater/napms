export interface AuthSession {
  accessToken(): string | null;
}

let runtimeToken: string | null = null;

export const authSession: AuthSession = {
  accessToken: () => runtimeToken,
};

export function setRuntimeAccessToken(token: string | null): void {
  runtimeToken = token;
}
