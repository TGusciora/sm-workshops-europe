import { render, screen, within } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { afterEach, describe, expect, it, vi } from "vitest";
import { InterviewCalendar } from "./InterviewCalendar";
import { mockApi, problem } from "../test/mockApi";

afterEach(() => {
  vi.unstubAllGlobals();
});

const interview = (overrides: Record<string, unknown> = {}) => ({
  id: 1,
  stage: "technical",
  starts_at: "2026-11-03T10:00",
  duration_minutes: 60,
  interviewer: "Anna Kowalska",
  location: "Room 2",
  candidate_ref: "C-14",
  status: "planned",
  ...overrides,
});

function baseRoutes(interviews: unknown[]) {
  return ({ method, path }: { method: string; path: string }) => {
    if (path === "/stages") return { stages: ["screening", "technical"] };
    if (path === "/positions/head-of-sales/interviews" && method === "GET") return interviews;
    throw new Error(`unexpected ${method} ${path}`);
  };
}

describe("InterviewCalendar", () => {
  it("groups the agenda by day in time order and marks cancelled interviews", async () => {
    mockApi(
      baseRoutes([
        interview({ id: 1, starts_at: "2026-11-03T09:00" }),
        interview({ id: 2, starts_at: "2026-11-03T14:00", status: "cancelled" }),
        interview({ id: 3, starts_at: "2026-11-04T10:00" }),
      ]),
    );

    render(<InterviewCalendar slug="head-of-sales" />);

    const day = await screen.findByRole("region", { name: "2026-11-03" });
    const times = within(day).getAllByText(/^\d\d:\d\d$/).map((node) => node.textContent);
    expect(times).toEqual(["09:00", "14:00"]);
    expect(within(day).getByText("Cancelled")).toBeTruthy();
    expect(screen.getByRole("region", { name: "2026-11-04" })).toBeTruthy();
  });

  it("plans an interview with the entered date, time and duration", async () => {
    const user = userEvent.setup();
    const calls = mockApi((call) => {
      if (call.method === "POST" && call.path === "/positions/head-of-sales/interviews") {
        return interview();
      }
      return baseRoutes([])(call);
    });
    render(<InterviewCalendar slug="head-of-sales" />);

    await user.click(await screen.findByRole("button", { name: "Plan interview" }));
    await user.type(await screen.findByLabelText("Date"), "2026-11-03");
    await user.type(screen.getByLabelText("Start time"), "10:00");
    await user.type(screen.getByLabelText("Interviewer"), "Anna Kowalska");
    await user.type(screen.getByLabelText("Candidate reference"), "C-14");
    await user.click(screen.getByRole("button", { name: "Save interview" }));

    const post = calls.find((call) => call.method === "POST");
    expect(post?.body).toEqual({
      stage: "screening",
      starts_at: "2026-11-03T10:00",
      duration_minutes: 60,
      interviewer: "Anna Kowalska",
      location: "",
      candidate_ref: "C-14",
    });
  });

  it("edits a planned interview, and offers no edit for a cancelled one", async () => {
    const user = userEvent.setup();
    const calls = mockApi((call) => {
      if (call.method === "PUT" && call.path === "/interviews/1") return interview({ starts_at: "2026-11-03T11:00" });
      if (call.method === "GET" && call.path === "/positions/head-of-sales/interviews") {
        return [interview({ id: 1, starts_at: "2026-11-03T11:00" }), interview({ id: 2, status: "cancelled" })];
      }
      return baseRoutes([interview({ id: 1 }), interview({ id: 2, status: "cancelled" })])(call);
    });
    render(<InterviewCalendar slug="head-of-sales" />);

    const edits = await screen.findAllByRole("button", { name: "Edit" });
    expect(edits).toHaveLength(1);
    await user.click(edits[0]);
    const time = screen.getByLabelText("Start time");
    await user.clear(time);
    await user.type(time, "11:00");
    await user.click(screen.getByRole("button", { name: "Save changes" }));

    expect(calls.find((call) => call.method === "PUT")?.body).toMatchObject({ starts_at: "2026-11-03T11:00" });
  });

  it("cancels only after the hiring manager confirms", async () => {
    const user = userEvent.setup();
    let cancelled = false;
    const calls = mockApi((call) => {
      if (call.method === "POST" && call.path === "/interviews/1/cancel") {
        cancelled = true;
        return interview({ status: "cancelled" });
      }
      if (call.method === "GET" && call.path === "/positions/head-of-sales/interviews") {
        return [interview({ status: cancelled ? "cancelled" : "planned" })];
      }
      return baseRoutes([])(call);
    });
    render(<InterviewCalendar slug="head-of-sales" />);

    await user.click(await screen.findByRole("button", { name: "Cancel interview" }));
    expect(calls.some((call) => call.path.endsWith("/cancel"))).toBe(false);

    await user.click(screen.getByRole("button", { name: "Yes, cancel it" }));

    expect(calls.some((call) => call.method === "POST" && call.path === "/interviews/1/cancel")).toBe(true);
  });

  it("shows the server's message and keeps the form when a save is refused", async () => {
    const user = userEvent.setup();
    mockApi((call) => {
      if (call.method === "POST" && call.path === "/positions/head-of-sales/interviews") {
        throw problem(422, "duration must be between 5 and 480 minutes");
      }
      return baseRoutes([])(call);
    });
    render(<InterviewCalendar slug="head-of-sales" />);

    await user.click(await screen.findByRole("button", { name: "Plan interview" }));
    await user.type(screen.getByLabelText("Date"), "2026-11-03");
    await user.type(screen.getByLabelText("Start time"), "10:00");
    await user.type(screen.getByLabelText("Interviewer"), "Anna");
    await user.type(screen.getByLabelText("Candidate reference"), "C-14");
    await user.click(screen.getByRole("button", { name: "Save interview" }));

    expect(await screen.findByText("duration must be between 5 and 480 minutes")).toBeTruthy();
    expect(screen.getByRole("button", { name: "Save interview" })).toBeTruthy();
  });
});
