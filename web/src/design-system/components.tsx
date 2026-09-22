import { type FormEvent, type ReactNode, useId } from "react";

export function PageHeader({
  eyebrow,
  title,
  actions,
  children,
}: {
  eyebrow: string;
  title: string;
  actions?: ReactNode;
  children?: ReactNode;
}) {
  return (
    <header className="page-header">
      <div className="page-header-copy">
        <p className="eyebrow">{eyebrow}</p>
        <h2>{title}</h2>
        {children}
      </div>
      {actions && <div className="page-header-actions">{actions}</div>}
    </header>
  );
}

export function FormSection({
  children,
  onSubmit,
}: {
  children: ReactNode;
  onSubmit?: (event: FormEvent<HTMLFormElement>) => void;
}) {
  return (
    <form className="panel form-grid" onSubmit={onSubmit}>
      {children}
    </form>
  );
}

export function FieldGroup({
  label,
  children,
}: {
  label: string;
  children: ReactNode;
}) {
  return (
    <div className="field-group">
      <span>{label}</span>
      {children}
    </div>
  );
}

export function ReferenceField({
  label,
  value,
  onChange,
  readOnly = false,
}: {
  label: string;
  value: string;
  onChange?: (value: string) => void;
  readOnly?: boolean;
}) {
  const id = useId();
  return (
    <div className="field-group">
      <label htmlFor={id}>{label}</label>
      <input
        id={id}
        value={value}
        readOnly={readOnly}
        onChange={
          onChange ? (event) => onChange(event.target.value) : undefined
        }
      />
    </div>
  );
}

export function VersionedEditor({
  version,
  children,
}: {
  version: number;
  children: ReactNode;
}) {
  return (
    <section className="panel versioned-editor" data-version={version}>
      <p className="muted">Version {version}</p>
      {children}
    </section>
  );
}

export function StatusBanner({
  kind = "status",
  children,
}: {
  kind?: "status" | "success" | "warning" | "blocked" | "failed";
  children: ReactNode;
}) {
  return (
    <p
      role={kind === "status" ? "status" : "alert"}
      className={`status status-${kind}`}
    >
      {children}
    </p>
  );
}

export function ProvenancePanel({ children }: { children: ReactNode }) {
  return (
    <details className="panel">
      <summary>Provenance and history</summary>
      {children}
    </details>
  );
}

export function EmptyState({ children }: { children: ReactNode }) {
  return <p className="muted">{children}</p>;
}

export function ConfirmationDialog({
  open,
  title,
  children,
  onConfirm,
  onCancel,
}: {
  open: boolean;
  title: string;
  children: ReactNode;
  onConfirm: () => void;
  onCancel: () => void;
}) {
  if (!open) return null;
  return (
    <div
      role="dialog"
      aria-modal="true"
      aria-labelledby="confirmation-title"
      className="panel"
    >
      <h3 id="confirmation-title">{title}</h3>
      {children}
      <button type="button" onClick={onConfirm}>
        Confirm
      </button>
      <button type="button" onClick={onCancel}>
        Cancel
      </button>
    </div>
  );
}

export function DataTable({ children }: { children: ReactNode }) {
  return (
    <div className="data-table-wrap">
      <table className="data-table">{children}</table>
    </div>
  );
}

export function DataTableHeadCell({
  children,
  className = "",
}: {
  children: ReactNode;
  className?: string;
}) {
  return <th className={className}>{children}</th>;
}

export function DataTableCell({
  children,
  className = "",
}: {
  children: ReactNode;
  className?: string;
}) {
  return <td className={className}>{children}</td>;
}

export function PrimaryTableAction({
  children,
  onClick,
}: {
  children: ReactNode;
  onClick: () => void;
}) {
  return (
    <button type="button" className="table-primary-action" onClick={onClick}>
      {children}
    </button>
  );
}
