import {
  Box,
  Button,
  MenuItem,
  Paper,
  Stack,
  TextField,
  Typography,
} from "@mui/material";
import type { FormEvent } from "react";
import type { EditorPatternProps } from "../../contracts";
import { MuiStatus } from "./MuiStatus";

function statusCopy(state: EditorPatternProps["state"]): string | undefined {
  switch (state) {
    case "validation-rejected":
      return "The submitted values were rejected.";
    case "authorization-rejected":
      return "The operation was rejected by the backend.";
    case "conflict":
      return "The operation conflicts with current server state.";
    case "technical-error":
      return "The operation could not be completed.";
    default:
      return undefined;
  }
}

export function MuiEditorPattern({
  eyebrow,
  title,
  description,
  fields,
  submitLabel,
  submittingLabel,
  submitDisabled = false,
  secondaryAction,
  onSubmit,
  state,
  statusMessage,
  embedded = false,
}: EditorPatternProps) {
  function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    onSubmit();
  }

  const failure = statusCopy(state);

  return (
    <Stack spacing={embedded ? 1.5 : 3}>
      <Box>
        {eyebrow ? (
          <Typography
            variant="overline"
            color="text.secondary"
            sx={{ fontWeight: 700, letterSpacing: "0.08em" }}
          >
            {eyebrow}
          </Typography>
        ) : null}
        <Typography
          variant={embedded ? "subtitle1" : "h4"}
          component={embedded ? "h5" : "h1"}
          sx={embedded ? { fontWeight: 700 } : undefined}
        >
          {title}
        </Typography>
        {description ? (
          <Typography color="text.secondary" sx={{ mt: 0.75, maxWidth: 720 }}>
            {description}
          </Typography>
        ) : null}
      </Box>

      <Paper
        component="form"
        variant="outlined"
        onSubmit={submit}
        sx={{ p: { xs: 2, sm: embedded ? 2 : 3 }, maxWidth: 720 }}
      >
        <Stack spacing={2}>
          {fields.map((field) => (
            <TextField
              key={field.id}
              label={field.label}
              value={field.value}
              required={field.required}
              select={Boolean(field.options?.length)}
              onChange={(event) => field.onChange(event.target.value)}
              fullWidth
            >
              {field.options?.map((option) => (
                <MenuItem key={option.value} value={option.value}>
                  {option.label}
                </MenuItem>
              ))}
            </TextField>
          ))}

          {failure ? (
            <MuiStatus message={statusMessage ?? failure} />
          ) : null}

          <Stack direction="row" spacing={1} sx={{ flexWrap: "wrap", gap: 1 }}>
            <Button
              type="submit"
              variant="contained"
              disabled={submitDisabled || state === "submitting"}
            >
              {state === "submitting"
                ? submittingLabel ?? `${submitLabel}…`
                : submitLabel}
            </Button>
            {secondaryAction ? (
              <Button
                type="button"
                variant="outlined"
                disabled={secondaryAction.disabled || state === "submitting"}
                onClick={secondaryAction.onInvoke}
              >
                {secondaryAction.label}
              </Button>
            ) : null}
          </Stack>
        </Stack>
      </Paper>
    </Stack>
  );
}
