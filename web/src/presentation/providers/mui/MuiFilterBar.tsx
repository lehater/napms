import { Button, MenuItem, Stack, TextField } from "@mui/material";
import type { FilterBarPatternProps } from "../../contracts";

export function MuiFilterBar({
  search,
  filters,
  sort,
  active,
  onClear,
}: FilterBarPatternProps) {
  return (
    <Stack
      data-presentation-pattern="filter-bar"
      direction={{ xs: "column", md: "row" }}
      spacing={1}
      sx={{ alignItems: { xs: "stretch", md: "center" } }}
    >
      <TextField
        size="small"
        label={search.label}
        value={search.value}
        placeholder={search.placeholder}
        onChange={(event) => search.onChange(event.target.value)}
        sx={{ minWidth: { md: 240 } }}
      />
      {filters.map((filter) => (
        <TextField
          key={filter.id}
          size="small"
          label={filter.label}
          value={filter.value}
          placeholder={filter.placeholder}
          select={Boolean(filter.options)}
          onChange={(event) => filter.onChange(event.target.value)}
          sx={{ minWidth: { md: 180 } }}
        >
          {filter.options?.map((option) => (
            <MenuItem key={option.value} value={option.value}>
              {option.label}
            </MenuItem>
          ))}
        </TextField>
      ))}
      <TextField
        size="small"
        select
        label="Sort by"
        value={sort.field}
        onChange={(event) => sort.onFieldChange(event.target.value)}
        sx={{ minWidth: { md: 180 } }}
      >
        {sort.fields.map((field) => (
          <MenuItem key={field.value} value={field.value}>
            {field.label}
          </MenuItem>
        ))}
      </TextField>
      <TextField
        size="small"
        select
        label="Sort direction"
        value={sort.direction}
        onChange={(event) =>
          sort.onDirectionChange(event.target.value as "asc" | "desc")
        }
        sx={{ minWidth: { md: 150 } }}
      >
        <MenuItem value="asc">Ascending</MenuItem>
        <MenuItem value="desc">Descending</MenuItem>
      </TextField>
      <Button type="button" variant="outlined" disabled={!active} onClick={onClear}>
        Clear
      </Button>
    </Stack>
  );
}
