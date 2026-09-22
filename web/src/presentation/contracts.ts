import type { ReactNode } from "react";
import type { BreadcrumbItem, NavigationItem } from "../app/navigation";

export type AppShellProps = {
  items: readonly NavigationItem[];
  currentPath: string;
  breadcrumbs: readonly BreadcrumbItem[];
  onNavigate: (path: string) => void;
  children: ReactNode;
};

export type PresentationAction = {
  label: string;
  onInvoke: () => void;
  disabled?: boolean;
  tone?: "primary" | "secondary";
};

export type CatalogueState =
  | "loading"
  | "loaded"
  | "empty"
  | "authorization-rejected"
  | "technical-error";

export type CataloguePatternProps = {
  eyebrow: string;
  title: string;
  description?: string;
  primaryAction?: PresentationAction;
  state: CatalogueState;
  statusMessage?: string;
  emptyMessage: string;
  queryControls?: ReactNode;
  children?: ReactNode;
};

export type FilterBarField = {
  id: string;
  label: string;
  value: string;
  placeholder?: string;
  options?: readonly EditorOption[];
  onChange: (value: string) => void;
};

export type FilterBarSort = {
  field: string;
  fields: readonly EditorOption[];
  direction: "asc" | "desc";
  onFieldChange: (field: string) => void;
  onDirectionChange: (direction: "asc" | "desc") => void;
};

export type FilterBarPatternProps = {
  search: {
    label: string;
    value: string;
    placeholder?: string;
    onChange: (value: string) => void;
  };
  filters: readonly FilterBarField[];
  sort: FilterBarSort;
  active: boolean;
  onClear: () => void;
};

export type DataTableColumn<Row> = {
  id: string;
  label: string;
  emphasis?: "primary" | "technical" | "default";
  sortKey?: string;
  render: (row: Row) => ReactNode;
};

export type DataTablePatternProps<Row> = {
  label: string;
  rows: readonly Row[];
  columns: readonly DataTableColumn<Row>[];
  rowKey: (row: Row) => string;
  openColumnId?: string;
  onOpen?: (row: Row) => void;
  rowAction?: (row: Row) => PresentationAction;
  sort?: {
    field: string;
    direction: "asc" | "desc";
    onChange: (field: string, direction: "asc" | "desc") => void;
  };
  paging?: {
    page: number;
    pageSize: number;
    total: number;
    pageSizeOptions?: readonly number[];
    onPageChange: (page: number) => void;
    onPageSizeChange: (pageSize: number) => void;
  };
  emptyMessage?: string;
};

export type StructuredListPatternProps<Row> = {
  label: string;
  rows: readonly Row[];
  rowKey: (row: Row) => string;
  primary: (row: Row) => ReactNode;
  secondary?: (row: Row) => ReactNode;
  onOpen?: (row: Row) => void;
  rowAction?: (row: Row) => PresentationAction;
  emptyMessage: string;
};

export type EditorState =
  | "editing"
  | "submitting"
  | "validation-rejected"
  | "authorization-rejected"
  | "conflict"
  | "technical-error";

export type EditorOption = {
  value: string;
  label: string;
};

export type EditorField = {
  id: string;
  label: string;
  value: string;
  required?: boolean;
  readOnly?: boolean;
  inputType?: "text" | "password";
  options?: readonly EditorOption[];
  onChange?: (value: string) => void;
};

export type EditorPatternProps = {
  eyebrow?: string;
  title: string;
  description?: string;
  fields: readonly EditorField[];
  submitLabel: string;
  submittingLabel?: string;
  submitDisabled?: boolean;
  secondaryAction?: PresentationAction;
  onSubmit: () => void;
  state: EditorState;
  statusMessage?: string;
  embedded?: boolean;
};

export type DetailState =
  | "loading"
  | "loaded"
  | "empty-current"
  | "not-found"
  | "submitting"
  | "validation-rejected"
  | "authorization-rejected"
  | "conflict"
  | "technical-error";

export type DetailSection = {
  id: string;
  title: string;
  summary?: ReactNode;
  actions?: readonly PresentationAction[];
  editors?: readonly EditorPatternProps[];
};

export type DetailPatternProps = {
  eyebrow: string;
  title: string;
  description?: string;
  technicalContext?: string;
  version?: number;
  sections: readonly DetailSection[];
  secondary?: {
    label: string;
    content: ReactNode;
  };
  state: DetailState;
  statusMessage?: string;
  onRetry?: () => void;
  onReturn?: () => void;
};

export type OutcomeTone = "success" | "warning" | "info" | "error";

export type OutcomePatternProps = {
  title: string;
  summary: ReactNode;
  tone?: OutcomeTone;
  details?: ReactNode;
  provenance?: ReactNode;
};

export type ScopeSelectorState =
  | "editing"
  | "submitting"
  | "validation-rejected"
  | "authorization-rejected"
  | "technical-error";

export type ScopeSelectorPatternProps = {
  eyebrow: string;
  title: string;
  description?: string;
  label: string;
  value: string;
  onChange: (value: string) => void;
  executeLabel: string;
  onExecute: () => void;
  state: ScopeSelectorState;
  statusMessage?: string;
};
