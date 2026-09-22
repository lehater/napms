import { AccessRequestScreen } from "./AccessRequestScreen";

export function AccessRequestScreens({
  create = false,
  requestRef,
}: {
  create?: boolean;
  requestRef?: string;
}) {
  return <AccessRequestScreen create={create} requestRef={requestRef} />;
}
