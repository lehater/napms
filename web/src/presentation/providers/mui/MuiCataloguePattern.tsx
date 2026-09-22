import { Box, Paper, Stack, Typography } from "@mui/material";
import type { CataloguePatternProps } from "../../contracts";
import { MuiStatus } from "./MuiStatus";
import { MuiTaskActions } from "./MuiTaskActions";

export function MuiCataloguePattern({
  eyebrow,
  title,
  description,
  primaryAction,
  state,
  statusMessage,
  emptyMessage,
  queryControls,
  children,
}: CataloguePatternProps) {
  return (
    <Stack spacing={3}>
      <Stack
        direction={{ xs: "column", sm: "row" }}
        sx={{
          justifyContent: "space-between",
          alignItems: { xs: "stretch", sm: "flex-start" },
          gap: 2,
        }}
      >
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
        {primaryAction ? (
          <MuiTaskActions actions={[{ ...primaryAction, tone: "primary" }]} />
        ) : null}
      </Stack>

      {queryControls &&
      state !== "authorization-rejected" &&
      state !== "technical-error"
        ? queryControls
        : null}

      {state === "loading" ? <MuiStatus loading message="Loading…" /> : null}

      {state === "authorization-rejected" ? (
        <MuiStatus
          message={
            statusMessage ?? "You are not authorized to view this catalogue."
          }
        />
      ) : null}

      {state === "technical-error" ? (
        <MuiStatus
          message={statusMessage ?? "The catalogue could not be loaded."}
        />
      ) : null}

      {state === "empty" && !children ? (
        <Paper variant="outlined" sx={{ p: 3 }}>
          <Typography color="text.secondary">{emptyMessage}</Typography>
        </Paper>
      ) : null}

      {state === "loaded" || state === "empty" ? children : null}
    </Stack>
  );
}
