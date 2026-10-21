import type { ReactNode } from "react";

export type StateKind = "loading" | "empty" | "error" | "success";

interface Props {
  kind: StateKind;
  className?: string;
  children: ReactNode;
}

// The one pattern for loading, empty, error and success text on every screen (F0004).
// Errors use role="alert" so screen readers announce them at once; the rest use role="status".
export function StateMessage({ kind, className, children }: Props) {
  const role = kind === "error" ? "alert" : kind === "empty" ? undefined : "status";
  const classes = ["state", `state-${kind}`, className].filter(Boolean).join(" ");
  return (
    <p role={role} className={classes}>
      {children}
    </p>
  );
}
