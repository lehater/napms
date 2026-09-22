import {
  Box,
  Button,
  Paper,
  Stack,
  TextField,
  Typography,
} from "@mui/material";
import type { ScopeSelectorPatternProps } from "../../contracts";
import { MuiStatus } from "./MuiStatus";

function failureMessage(
  state: ScopeSelectorPatternProps["state"],
): string | undefined {
  switch (state) {
    case "validation-rejected":
      return "The selected scope was rejected.";
    case "authorization-rejected":
      return "The operation was rejected by the backend.";
    case "technical-error":
      return "The operation could not be completed.";
    default:
      return undefined;
  }
}

export function MuiScopeSelectorPattern({
  eyebrow,
  title,
  description,
  label,
  value,
  onChange,
  executeLabel,
  onExecute,
  state,
  statusMessage,
}: ScopeSelectorPatternProps) {
  const failure = failureMessage(state);

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
          <Typography color="text.secondary" sx={{ mt: 0.75, maxWidth: 760 }}>
            {description}
          </Typography>
        ) : null}
      </Box>

      <Paper variant="outlined" sx={{ p: { xs: 2, sm: 3 }, maxWidth: 760 }}>
        <Stack spacing={2}>
          <TextField
            label={label}
            value={value}
            onChange={(event) => onChange(event.target.value)}
            fullWidth
          />
          {failure ? <MuiStatus message={statusMessage ?? failure} /> : null}
          <Box>
            <Button
              type="button"
              variant="contained"
              disabled={state === "submitting"}
              onClick={onExecute}
            >
              {state === "submitting" ? `${executeLabel}…` : executeLabel}
            </Button>
          </Box>
        </Stack>
      </Paper>
    </Stack>
  );
}
