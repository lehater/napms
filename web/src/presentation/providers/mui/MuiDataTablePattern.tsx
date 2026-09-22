import {
  Button,
  Paper,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Typography,
} from "@mui/material";
import type { DataTablePatternProps } from "../../contracts";

export function MuiDataTablePattern<Row>({
  label,
  rows,
  columns,
  rowKey,
  openColumnId,
  onOpen,
  rowAction,
  emptyMessage = "No records.",
}: DataTablePatternProps<Row>) {
  if (rows.length === 0) {
    return (
      <Paper variant="outlined" sx={{ p: 3 }}>
        <Typography color="text.secondary">{emptyMessage}</Typography>
      </Paper>
    );
  }

  return (
    <TableContainer component={Paper} variant="outlined">
      <Table size="small" aria-label={label}>
        <TableHead>
          <TableRow>
            {columns.map((column) => (
              <TableCell key={column.id}>{column.label}</TableCell>
            ))}
            {rowAction ? <TableCell>Actions</TableCell> : null}
          </TableRow>
        </TableHead>
        <TableBody>
          {rows.map((row) => (
            <TableRow key={rowKey(row)} hover>
              {columns.map((column) => (
                <TableCell
                  key={column.id}
                  data-emphasis={column.emphasis}
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
                  {column.id === openColumnId && onOpen ? (
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
              {rowAction ? (
                <TableCell>
                  <Button
                    type="button"
                    size="small"
                    variant="outlined"
                    disabled={rowAction(row).disabled}
                    onClick={rowAction(row).onInvoke}
                    sx={{ minHeight: 0, py: 0.25 }}
                  >
                    {rowAction(row).label}
                  </Button>
                </TableCell>
              ) : null}
            </TableRow>
          ))}
        </TableBody>
      </Table>
    </TableContainer>
  );
}
