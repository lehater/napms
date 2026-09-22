import {
  Alert,
  Box,
  Button,
  Paper,
  Stack,
  TextField,
  Typography,
} from "@mui/material";
import type { FormEvent } from "react";
import type { EditorPatternProps } from "../../contracts";

function statusCopy(state: EditorPatternProps["state"]): string | undefined {
  switch (state) {
    case "validation-rejected":
      return "The submitted values were rejected.";
    case "authorization-rejected":
      return "The operation was rejected by the backend.";
    case "conflict":
      return "The resource could not be created because the request conflicts with current state.";
    case "technical-error":
      return "The resource could not be created.";
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
  submitDisabled = false,
  onSubmit,
  state,
  statusMessage,
}: EditorPatternProps) {
  function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    onSubmit();
  }

  const failure = statusCopy(state);

  return (
    <Stack spacing={3}>
      <Box>
        <Typography
          variant="overline"
          color="text.secondary"
          sx={{ fontWeight: 700, letterSpacing: "0.08em" }}
        >
          {eyebrow}
        </Typography>
        <Typography variant="h4" component="h1">
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
        sx={{ p: { xs: 2, sm: 3 }, maxWidth: 720 }}
      >
        <Stack spacing={2}>
          {fields.map((field) => (
            <TextField
              key={field.id}
              label={field.label}
              value={field.value}
              required={field.required}
              onChange={(event) => field.onChange(event.target.value)}
              fullWidth
            />
          ))}

          {failure ? (
            <Alert severity="error">{statusMessage ?? failure}</Alert>
          ) : null}

          <Box>
            <Button
              type="submit"
              variant="contained"
              disabled={submitDisabled || state === "submitting"}
            >
              {state === "submitting" ? "Creating…" : submitLabel}
            </Button>
          </Box>
        </Stack>
      </Paper>
    </Stack>
  );
}
