import {
  Button,
  List,
  ListItem,
  ListItemButton,
  ListItemText,
  Paper,
  Stack,
  Typography,
} from "@mui/material";
import type { StructuredListPatternProps } from "../../contracts";

export function MuiStructuredListPattern<Row>({
  label,
  rows,
  rowKey,
  primary,
  secondary,
  onOpen,
  rowAction,
  emptyMessage,
}: StructuredListPatternProps<Row>) {
  if (rows.length === 0) {
    return (
      <Paper variant="outlined" sx={{ p: 3 }}>
        <Typography color="text.secondary">{emptyMessage}</Typography>
      </Paper>
    );
  }

  return (
    <Paper variant="outlined">
      <List aria-label={label} disablePadding>
        {rows.map((row) => {
          const content = (
            <ListItemText
              primary={primary(row)}
              secondary={secondary ? secondary(row) : undefined}
            />
          );
          const action = rowAction?.(row);
          return (
            <ListItem
              key={rowKey(row)}
              divider
              disablePadding={Boolean(onOpen)}
              secondaryAction={
                action ? (
                  <Button
                    type="button"
                    size="small"
                    variant="outlined"
                    disabled={action.disabled}
                    onClick={action.onInvoke}
                  >
                    {action.label}
                  </Button>
                ) : undefined
              }
            >
              {onOpen ? (
                <ListItemButton onClick={() => onOpen(row)}>
                  {content}
                </ListItemButton>
              ) : (
                <Stack sx={{ width: "100%", px: 2, py: 1.5 }}>{content}</Stack>
              )}
            </ListItem>
          );
        })}
      </List>
    </Paper>
  );
}
