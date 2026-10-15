import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { afterEach, describe, expect, it, vi } from "vitest";
import { App } from "./App";
import { mockApi } from "./test/mockApi";

afterEach(() => {
  vi.unstubAllGlobals();
});

describe("App", () => {
  it("shows the backend status and the positions it returns", async () => {
    mockApi(({ path }) => {
      if (path === "/health") return { status: "ok", auth_method: "subscription" };
      if (path === "/positions") return [{ slug: "ceo", title: "CEO" }];
      throw new Error(`unexpected ${path}`);
    });

    render(<App />);

    expect(await screen.findByText(/Backend ok/)).toBeTruthy();
    expect(screen.getByRole("button", { name: "CEO" })).toBeTruthy();
  });

  it("warns when the backend cannot be reached", async () => {
    vi.stubGlobal("fetch", vi.fn(async () => {
      throw new TypeError("Failed to fetch");
    }));

    render(<App />);

    expect((await screen.findAllByRole("alert"))[0].textContent).toContain("Backend unreachable");
  });

  it("adds a position and selects it", async () => {
    const user = userEvent.setup();
    const calls = mockApi(({ method, path, body }) => {
      if (path === "/health") return { status: "ok", auth_method: "subscription" };
      if (path === "/positions" && method === "GET") return [];
      if (path === "/positions" && method === "POST") return { slug: "data-engineer", title: (body as { title: string }).title };
      if (path === "/positions/data-engineer/chat") return { messages: [], draft: null };
      if (path === "/positions/data-engineer/job-description") return { slug: "data-engineer", text: null };
      throw new Error(`unexpected ${method} ${path}`);
    });
    render(<App />);
    await screen.findByText(/Backend ok/);

    await user.type(screen.getByLabelText("New position"), "Data Engineer");
    await user.click(screen.getByRole("button", { name: "Add position" }));

    expect(await screen.findByRole("button", { name: "Data Engineer" })).toBeTruthy();
    await waitFor(() =>
      expect(calls.some((call) => call.path === "/positions/data-engineer/chat")).toBe(true),
    );
  });
});
