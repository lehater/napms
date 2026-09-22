export type ApiErrorKind =
  | "not-found"
  | "rejected"
  | "conflict"
  | "unauthenticated"
  | "forbidden"
  | "unavailable"
  | "technical";

export function statusToErrorKind(status: number): ApiErrorKind {
  switch (status) {
    case 404:
      return "not-found";
    case 401:
      return "unauthenticated";
    case 403:
      return "forbidden";
    case 409:
      return "conflict";
    case 422:
      return "rejected";
    case 503:
      return "unavailable";
    default:
      return "technical";
  }
}
