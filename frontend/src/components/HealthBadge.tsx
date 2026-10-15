import type { Health } from "../types";

interface Props {
  health: Health | null;
  error: string | null;
}

export function HealthBadge({ health, error }: Props) {
  if (error) {
    return <p role="alert" className="badge badge-error">Backend unreachable: {error}</p>;
  }
  if (!health) {
    return <p className="badge">Checking backend…</p>;
  }
  const auth =
    health.auth_method === "api_key"
      ? "API key in use. Unset ANTHROPIC_API_KEY to use your subscription."
      : "Claude: subscription login";
  return (
    <p className="badge badge-ok">
      Backend ok. {auth}
    </p>
  );
}
