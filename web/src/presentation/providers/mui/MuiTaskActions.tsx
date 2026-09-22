import { Button, Stack } from "@mui/material";
import type { PresentationAction } from "../../contracts";

export function MuiTaskActions({
  actions,
}: {
  actions: readonly PresentationAction[];
}) {
  if (actions.length === 0) return null;

  return (
    <Stack direction="row" spacing={1} sx={{ flexWrap: "wrap", gap: 1 }}>
      {actions.map((action) => (
        <Button
          key={action.label}
          type="button"
          variant={action.tone === "primary" ? "contained" : "outlined"}
          disabled={action.disabled}
          onClick={action.onInvoke}
        >
          {action.label}
        </Button>
      ))}
    </Stack>
  );
}
