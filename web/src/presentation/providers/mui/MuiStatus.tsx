import { Alert, CircularProgress, Stack, Typography } from "@mui/material";

export function MuiStatus({
  loading = false,
  message,
  severity = "error",
}: {
  loading?: boolean;
  message: string;
  severity?: "error" | "warning" | "info" | "success";
}) {
  if (loading) {
    return (
      <Stack
        role="status"
        direction="row"
        spacing={1.5}
        sx={{ alignItems: "center", minHeight: 48 }}
      >
        <CircularProgress size={20} />
        <Typography>{message}</Typography>
      </Stack>
    );
  }

  return <Alert severity={severity}>{message}</Alert>;
}
