import {
  Alert,
  Box,
  Button,
  CircularProgress,
  Paper,
  Stack,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Typography,
} from "@mui/material";
import type { CataloguePatternProps } from "../../contracts";

export function MuiCataloguePattern<Row>({
  eyebrow,
  title,
  description,
  rows,
  columns,
  rowKey,
  openColumnId,
  onOpen,
  primaryAction,
  state,
  statusMessage,
  emptyMessage,
}: CataloguePatternProps<Row>) {
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
          <Button variant="contained" onClick={primaryAction.onInvoke}>
            {primaryAction.label}
          </Button>
        ) : null}
      </Stack>

      {state === "loading" ? (
        <Stack
          role="status"
          direction="row"
          spacing={1.5}
          sx={{ alignItems: "center", minHeight: 72 }}
        >
          <CircularProgress size={20} />
          <Typography>Loading…</Typography>
        </Stack>
      ) : null}

      {state === "authorization-rejected" ? (
        <Alert severity="error">
          {statusMessage ?? "You are not authorized to view this catalogue."}
        </Alert>
      ) : null}

      {state === "technical-error" ? (
        <Alert severity="error">
          {statusMessage ?? "The catalogue could not be loaded."}
        </Alert>
      ) : null}

      {state === "empty" ? (
        <Paper variant="outlined" sx={{ p: 3 }}>
          <Typography color="text.secondary">{emptyMessage}</Typography>
        </Paper>
      ) : null}

      {state === "loaded" ? (
        <TableContainer component={Paper} variant="outlined">
          <Table size="small" aria-label={title}>
            <TableHead>
              <TableRow>
                {columns.map((column) => (
                  <TableCell key={column.id}>{column.label}</TableCell>
                ))}
              </TableRow>
            </TableHead>
            <TableBody>
              {rows.map((row) => (
                <TableRow key={rowKey(row)} hover>
                  {columns.map((column) => (
                    <TableCell
                      key={column.id}
                      sx={
                        column.emphasis === "technical"
                          ? {
                              color: "text.secondary",
                              fontFamily: "monospace",
                              fontSize: "0.78rem",
                            }
                          : undefined
                      }
                    >
                      {column.id === openColumnId ? (
                        <Button
                          variant="text"
                          size="small"
                          onClick={() => onOpen(row)}
                          sx={{
                            minWidth: 0,
                            p: 0,
                            justifyContent: "flex-start",
                            fontWeight: 650,
                          }}
                        >
                          {column.render(row)}
                        </Button>
                      ) : (
                        column.render(row)
                      )}
                    </TableCell>
                  ))}
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </TableContainer>
      ) : null}
    </Stack>
  );
}
