import { render, screen, waitFor, within } from "@testing-library/react";
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

    expect((await screen.findByText(/Backend ok/)).className).toContain("state-success");
    expect(screen.getByRole("button", { name: "CEO" })).toBeTruthy();
  });

  it("warns when the backend cannot be reached", async () => {
    vi.stubGlobal("fetch", vi.fn(async () => {
      throw new TypeError("Failed to fetch");
    }));

    render(<App />);

    expect((await screen.findByText(/Backend unreachable/)).getAttribute("role")).toBe("alert");
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

    expect(await screen.findByRole("button", { name: /Data Engineer/ })).toBeTruthy();
    await waitFor(() =>
      expect(calls.some((call) => call.path === "/positions/data-engineer/chat")).toBe(true),
    );
  });

  it("shows the positions in a sidebar with the open one marked", async () => {
    const user = userEvent.setup();
    mockApi(({ method, path }) => {
      if (path === "/health") return { status: "ok", auth_method: "subscription" };
      if (path === "/positions") return [{ slug: "ceo", title: "CEO" }, { slug: "data", title: "Data engineer" }];
      if (path === "/positions/ceo/chat") return { messages: [], draft: null };
      if (path === "/positions/ceo/job-description") return { slug: "ceo", text: null };
      throw new Error(`unexpected ${method} ${path}`);
    });
    render(<App />);

    expect(await screen.findByRole("heading", { name: "Positions" })).toBeTruthy();
    expect(screen.getByRole("heading", { name: "Choose a position" })).toBeTruthy();
    expect(screen.getByText("Positions", { selector: ".breadcrumb" })).toBeTruthy();

    await user.click(screen.getByRole("button", { name: "CEO" }));

    expect(screen.getByRole("button", { name: /^CEO/ }).getAttribute("aria-pressed")).toBe("true");
    expect(screen.getByRole("button", { name: "Data engineer" }).getAttribute("aria-pressed")).toBe("false");
    expect(screen.getByRole("heading", { level: 1, name: "CEO" })).toBeTruthy();
    expect(screen.getByText("Positions / CEO")).toBeTruthy();
    expect(screen.getByText("Open")).toBeTruthy();
  });

  it("shows the new position form with its placeholder and label", async () => {
    mockApi(({ path }) => {
      if (path === "/health") return { status: "ok", auth_method: "subscription" };
      if (path === "/positions") return [];
      throw new Error(`unexpected ${path}`);
    });
    render(<App />);

    const input = await screen.findByLabelText("New position");
    expect(input.getAttribute("placeholder")).toBe("For example, Head of Sales");
    expect(screen.getByRole("button", { name: "Add position" })).toBeTruthy();
  });

  it("marks the section control with aria-pressed and switches sections", async () => {
    const user = userEvent.setup();
    mockApi(({ method, path }) => {
      if (path === "/health") return { status: "ok", auth_method: "subscription" };
      if (path === "/positions") return [{ slug: "ceo", title: "CEO" }];
      if (path === "/positions/ceo/chat") return { messages: [], draft: null };
      if (path === "/positions/ceo/job-description") return { slug: "ceo", text: null };
      if (path === "/stages") return { stages: ["screening"] };
      if (path === "/positions/ceo/stages/screening/questions") return { stage: "screening", confirmed: false, questions: [] };
      throw new Error(`unexpected ${method} ${path}`);
    });
    render(<App />);
    await user.click(await screen.findByRole("button", { name: "CEO" }));

    const job = screen.getByRole("button", { name: "Job description" });
    const questions = screen.getByRole("button", { name: "Interview questions" });
    expect(within(screen.getByRole("navigation", { name: "Sections" })).getAllByRole("button").map((b) => b.textContent)).toEqual(
      expect.arrayContaining(["Job description", "Interview questions"]),
    );
    expect(job.getAttribute("aria-pressed")).toBe("true");
    expect(questions.getAttribute("aria-pressed")).toBe("false");

    await user.click(questions);

    expect(screen.getByRole("button", { name: "Job description" }).getAttribute("aria-pressed")).toBe("false");
    expect(screen.getByRole("button", { name: "Interview questions" }).getAttribute("aria-pressed")).toBe("true");
  });
});
