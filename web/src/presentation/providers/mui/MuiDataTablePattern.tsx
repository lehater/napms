import {
  ButtonBase,
  Paper,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TablePagination,
  TableRow,
  TableSortLabel,
  Typography,
} from "@mui/material";
import type { DataTablePatternProps } from "../../contracts";

export function MuiDataTablePattern<Row>({
  label,
  rows,
  columns,
  rowKey,
  onOpen,
  rowAction,
  sort,
  paging,
  emptyMessage = "No records.",
}: DataTablePatternProps<Row>) {
  return (
    <Paper variant="outlined">
      <TableContainer>
        <Table size="small" aria-label={label}>
          <TableHead>
            <TableRow>
              {columns.map((column) => {
                const sortKey = column.sortKey;
                const activeSort = Boolean(
                  sort && sortKey && sort.field === sortKey,
                );
                return (
                  <TableCell
                    key={column.id}
                    sortDirection={
                      activeSort && sort ? sort.direction : false
                    }
                  >
                    {sort && sortKey ? (
                      <TableSortLabel
                        active={activeSort}
                        direction={activeSort ? sort.direction : "asc"}
                        onClick={() =>
                          sort.onChange(
                            sortKey,
                            activeSort && sort.direction === "asc"
                              ? "desc"
                              : "asc",
                          )
                        }
                      >
                        {column.label}
                      </TableSortLabel>
                    ) : (
                      column.label
                    )}
                  </TableCell>
                );
              })}
              {rowAction ? <TableCell>Actions</TableCell> : null}
            </TableRow>
          </TableHead>
          <TableBody>
            {rows.length === 0 ? (
              <TableRow>
                <TableCell
                  colSpan={columns.length + (rowAction ? 1 : 0)}
                  sx={{ color: "text.secondary" }}
                >
                  <Typography color="text.secondary">{emptyMessage}</Typography>
                </TableCell>
              </TableRow>
            ) : (
              rows.map((row) => (
                <TableRow
                  key={rowKey(row)}
                  hover={Boolean(onOpen)}
                  tabIndex={onOpen ? 0 : undefined}
                  onClick={onOpen ? () => onOpen(row) : undefined}
                  onKeyDown={
                    onOpen
                      ? (event) => {
                          if (event.key === "Enter" || event.key === " ") {
                            event.preventDefault();
                            onOpen(row);
                          }
                        }
                      : undefined
                  }
                  sx={
                    onOpen
                      ? {
                          cursor: "pointer",
                          "&:focus-visible": {
                            outline: 2,
                            outlineColor: "primary.main",
                            outlineOffset: -2,
                          },
                        }
                      : undefined
                  }
                >
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
                          : column.emphasis === "primary"
                            ? { color: "primary.main", fontWeight: 650 }
                            : undefined
                      }
                    >
                      {column.render(row)}
                    </TableCell>
                  ))}
                  {rowAction ? (
                    <TableCell>
                      <ButtonBase
                        disabled={rowAction(row).disabled}
                        onClick={(event) => {
                          event.stopPropagation();
                          rowAction(row).onInvoke();
                        }}
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
              ))
            )}
          </TableBody>
        </Table>
      </TableContainer>
      {paging ? (
        <TablePagination
          component="div"
          count={paging.total}
          page={Math.max(0, paging.page - 1)}
          rowsPerPage={paging.pageSize}
          rowsPerPageOptions={[...(paging.pageSizeOptions ?? [10, 25, 50, 100])]}
          onPageChange={(_event, page) => paging.onPageChange(page + 1)}
          onRowsPerPageChange={(event) =>
            paging.onPageSizeChange(Number(event.target.value))
          }
        />
      ) : null}
    </Paper>
  );
}
