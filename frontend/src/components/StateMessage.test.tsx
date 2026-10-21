import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { StateMessage } from "./StateMessage";

describe("StateMessage", () => {
  it("announces errors as alerts", () => {
    render(<StateMessage kind="error">Something failed</StateMessage>);

    const message = screen.getByRole("alert");
    expect(message.textContent).toBe("Something failed");
    expect(message.className).toContain("state-error");
  });

  it("announces loading and success as status", () => {
    render(<StateMessage kind="loading">Loading…</StateMessage>);
    render(<StateMessage kind="success">Saved.</StateMessage>);

    expect(screen.getByText("Loading…").getAttribute("role")).toBe("status");
    expect(screen.getByText("Saved.").getAttribute("role")).toBe("status");
  });

  it("shows an empty state without a live region", () => {
    render(<StateMessage kind="empty">No questions yet.</StateMessage>);

    const message = screen.getByText("No questions yet.");
    expect(message.getAttribute("role")).toBeNull();
    expect(message.className).toContain("state-empty");
  });
});
