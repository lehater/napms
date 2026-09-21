import type { ReactNode } from "react";

export function PageHeader({ eyebrow, title, children }: { eyebrow: string; title: string; children?: ReactNode }) {
  return <header><p className="eyebrow">{eyebrow}</p><h2>{title}</h2>{children}</header>;
}
export function FormSection({ children, onSubmit }: { children: ReactNode; onSubmit?: (event: React.FormEvent<HTMLFormElement>) => void }) {
  return <form className="panel form-grid" onSubmit={onSubmit}>{children}</form>;
}
export function FieldGroup({ label, children }: { label: string; children: ReactNode }) {
  return <label>{label}{children}</label>;
}
export function ReferenceField({ label, value, onChange, readOnly = false }: { label: string; value: string; onChange?: (value: string) => void; readOnly?: boolean }) {
  return <FieldGroup label={label}><input value={value} readOnly={readOnly} onChange={onChange ? (event) => onChange(event.target.value) : undefined} /></FieldGroup>;
}
export function VersionedEditor({ version, children }: { version: number; children: ReactNode }) {
  return <section className="panel" data-version={version}><p className="muted">Version {version}</p>{children}</section>;
}
export function StatusBanner({ kind = "status", children }: { kind?: "status" | "warning" | "blocked" | "failed"; children: ReactNode }) {
  return <p role={kind === "status" ? "status" : "alert"} className={`status status-${kind}`}>{children}</p>;
}
export function ProvenancePanel({ children }: { children: ReactNode }) {
  return <details className="panel"><summary>Provenance and history</summary>{children}</details>;
}
export function EmptyState({ children }: { children: ReactNode }) {
  return <p className="muted">{children}</p>;
}
export function ConfirmationDialog({ open, title, children, onConfirm, onCancel }: { open: boolean; title: string; children: ReactNode; onConfirm: () => void; onCancel: () => void }) {
  if (!open) return null;
  return <div role="dialog" aria-modal="true" aria-labelledby="confirmation-title" className="panel"><h3 id="confirmation-title">{title}</h3>{children}<button type="button" onClick={onConfirm}>Confirm</button><button type="button" onClick={onCancel}>Cancel</button></div>;
}
