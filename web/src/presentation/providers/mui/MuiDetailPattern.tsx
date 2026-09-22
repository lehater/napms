import {
  Accordion,
  AccordionDetails,
  AccordionSummary,
  Box,
  Paper,
  Stack,
  Typography,
} from "@mui/material";
import type { DetailPatternProps } from "../../contracts";
import { MuiEditorPattern } from "./MuiEditorPattern";
import { MuiStatus } from "./MuiStatus";
import { MuiTaskActions } from "./MuiTaskActions";

function failureMessage(
  state: DetailPatternProps["state"],
): string | undefined {
  switch (state) {
    case "not-found":
      return "The Resource could not be found.";
    case "validation-rejected":
      return "The submitted Resource values were rejected.";
    case "authorization-rejected":
      return "The Resource operation was rejected by the backend.";
    case "conflict":
      return "The Resource changed before this operation could be applied.";
    case "technical-error":
      return "The Resource workspace could not complete the operation.";
    default:
      return undefined;
  }
}

export function MuiDetailPattern({
  eyebrow,
  title,
  description,
  technicalContext,
  version,
  sections,
  secondary,
  state,
  statusMessage,
  onRetry,
  onReturn,
}: DetailPatternProps) {
  const failure = failureMessage(state);
  const loaded = sections.length > 0;

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
        {technicalContext ? (
          <Typography
            data-presentation-technical-context
            color="text.secondary"
            sx={{ mt: 0.5, fontFamily: "monospace", fontSize: "0.78rem" }}
          >
            {technicalContext}
          </Typography>
        ) : null}
        {description ? (
          <Typography color="text.secondary" sx={{ mt: 0.75, maxWidth: 760 }}>
            {description}
          </Typography>
        ) : null}
      </Box>

      {state === "loading" ? (
        <MuiStatus loading message="Loading Resource…" />
      ) : null}

      {state === "submitting" ? (
        <MuiStatus loading message="Saving Resource changes…" />
      ) : null}

      {state === "empty-current" ? (
        <MuiStatus
          severity="info"
          message="One or more current Resource fact categories have no effective value."
        />
      ) : null}

      {failure ? <MuiStatus message={statusMessage ?? failure} /> : null}

      {!loaded && state !== "loading" ? (
        <MuiTaskActions
          actions={[
            ...(onRetry
              ? [
                  {
                    label: "Retry",
                    onInvoke: onRetry,
                    tone: "primary" as const,
                  },
                ]
              : []),
            ...(onReturn
              ? [{ label: "Back to Resources", onInvoke: onReturn }]
              : []),
          ]}
        />
      ) : null}

      {loaded ? (
        <Paper
          variant="outlined"
          data-presentation-pattern="detail"
          data-version={version}
          sx={{ p: { xs: 2, sm: 3 } }}
        >
          <Stack spacing={3}>
            <Typography variant="h6" component="h3">
              Current facts
            </Typography>

            {sections.map((section) => (
              <Box
                key={section.id}
                component="section"
                sx={{
                  "& + section": {
                    borderTop: 1,
                    borderColor: "divider",
                    pt: 3,
                  },
                  "& > p": {
                    color: "text.secondary",
                    mb: 1,
                  },
                }}
              >
                <Typography
                  variant="subtitle1"
                  component="h4"
                  sx={{ fontWeight: 700, mb: 1 }}
                >
                  {section.title}
                </Typography>

                {section.summary}
                {section.actions ? (
                  <Box sx={{ my: 1.5 }}>
                    <MuiTaskActions actions={section.actions} />
                  </Box>
                ) : null}
                {section.editors?.map((editor) => (
                  <Box key={editor.title} sx={{ mt: 2 }}>
                    <MuiEditorPattern {...editor} embedded />
                  </Box>
                ))}
              </Box>
            ))}
          </Stack>
        </Paper>
      ) : null}

      {loaded && secondary ? (
        <Accordion disableGutters>
          <AccordionSummary>
            <Typography sx={{ fontWeight: 650 }}>{secondary.label}</Typography>
          </AccordionSummary>
          <AccordionDetails>{secondary.content}</AccordionDetails>
        </Accordion>
      ) : null}
    </Stack>
  );
}
