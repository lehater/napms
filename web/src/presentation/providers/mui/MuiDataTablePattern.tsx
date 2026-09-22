import {
  ButtonBase,
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
                  <ButtonBase
                    disabled={rowAction(row).disabled}
                    onClick={rowAction(row).onInvoke}
                    sx={{
                      border: 1,
                      borderColor: "divider",
                      borderRadius: 1,
                      px: 1,
                      py: 0.25,
                      color: "primary.main",
                      "&.Mui-disabled": {
                        color: "text.disabled",
                      },
                    }}
                  >
                    {rowAction(row).label}
                  </ButtonBase>
                </TableCell>
              ) : null}
            </TableRow>
          ))}
        </TableBody>
      </Table>
    </TableContainer>
  );
}
