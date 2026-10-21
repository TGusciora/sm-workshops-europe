import type { Health } from "../types";
import { StateMessage } from "./StateMessage";

interface Props {
  health: Health | null;
  error: string | null;
}

// The backend status pill in the page header (F0005). Green on success, error style on failure.
export function HealthBadge({ health, error }: Props) {
  if (error) {
    return <StateMessage kind="error" className="pill">Backend unreachable: {error}</StateMessage>;
  }
  if (!health) {
    return <StateMessage kind="loading" className="pill">Checking backend…</StateMessage>;
  }
  const auth =
    health.auth_method === "api_key"
      ? "API key in use. Unset ANTHROPIC_API_KEY to use your subscription."
      : "subscription login";
  return (
    <StateMessage kind="success" className="pill">
      Backend ok · {auth}
    </StateMessage>
  );
}
