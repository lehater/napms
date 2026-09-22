import { useState } from "react";
import { EditorPattern, type EditorPatternProps } from "../presentation";
import { setRuntimeAccessToken } from "./auth-session";
import { DevelopmentAuthError, developmentLogin } from "./dev-auth";

type DevelopmentLoginProps = {
  onAuthenticated: () => void;
};

export function DevelopmentLogin({ onAuthenticated }: DevelopmentLoginProps) {
  const [login, setLogin] = useState("admin");
  const [password, setPassword] = useState("admin");
  const [state, setState] = useState<EditorPatternProps["state"]>("editing");
  const [statusMessage, setStatusMessage] = useState<string>();

  async function submit() {
    setState("submitting");
    setStatusMessage(undefined);
    try {
      const token = await developmentLogin(login, password);
      setRuntimeAccessToken(token);
      onAuthenticated();
    } catch (error) {
      if (error instanceof DevelopmentAuthError && error.kind === "rejected") {
        setState("authorization-rejected");
        setStatusMessage("Invalid login or password.");
        return;
      }
      setState("technical-error");
      setStatusMessage("Development authentication is unavailable.");
    }
  }

  return (
    <EditorPattern
      eyebrow="Development authentication"
      title="Sign in"
      description="Local development only. Use admin / admin."
      fields={[
        {
          id: "login",
          label: "Login",
          value: login,
          required: true,
          onChange: setLogin,
        },
        {
          id: "password",
          label: "Password",
          value: password,
          required: true,
          inputType: "password",
          onChange: setPassword,
        },
      ]}
      submitLabel="Sign in"
      submittingLabel="Signing in…"
      onSubmit={() => void submit()}
      state={state}
      statusMessage={statusMessage}
    />
  );
}
