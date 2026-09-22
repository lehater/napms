import type { ReactNode } from "react";
import type { NavigationItem } from "../app/navigation";

export type AppShellProps = {
  items: readonly NavigationItem[];
  currentPath: string;
  onNavigate: (path: string) => void;
  children: ReactNode;
};

export type CatalogueState =
  | "loading"
  | "loaded"
  | "empty"
  | "authorization-rejected"
  | "technical-error";

export type CatalogueColumn<Row> = {
  id: string;
  label: string;
  emphasis?: "primary" | "technical" | "default";
  render: (row: Row) => ReactNode;
};

export type CataloguePatternProps<Row> = {
  eyebrow: string;
  title: string;
  description?: string;
  rows: readonly Row[];
  columns: readonly CatalogueColumn<Row>[];
  rowKey: (row: Row) => string;
  openColumnId: string;
  onOpen: (row: Row) => void;
  primaryAction?: {
    label: string;
    onInvoke: () => void;
  };
  state: CatalogueState;
  statusMessage?: string;
  emptyMessage: string;
};
