import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { afterEach, describe, expect, it, vi } from "vitest";
import { QuestionReview } from "./QuestionReview";
import { mockApi } from "../test/mockApi";

afterEach(() => {
  vi.unstubAllGlobals();
});

const question = (id: number, status = "proposed", text = `Question ${id}?`) => ({
  id,
  question: text,
  purpose: `Purpose ${id}`,
  good_answer: `Good answer ${id}`,
  status,
});

describe("QuestionReview", () => {
  it("proposes questions for a stage and lists each one with its purpose", async () => {
    const user = userEvent.setup();
    mockApi(({ method, path }) => {
      if (path === "/stages") return { stages: ["screening", "technical"] };
      if (path === "/positions/ceo/stages/screening/questions" && method === "GET") {
        return { stage: "screening", confirmed: false, questions: [] };
      }
      if (path === "/positions/ceo/stages/screening/questions" && method === "POST") {
        return { stage: "screening", confirmed: false, questions: [question(1), question(2)] };
      }
      throw new Error(`unexpected ${method} ${path}`);
    });
    render(<QuestionReview slug="ceo" />);

    await user.click(await screen.findByRole("button", { name: "Propose questions" }));

    expect(await screen.findByText("Question 1?")).toBeTruthy();
    expect(screen.getByText("Purpose: Purpose 2")).toBeTruthy();
  });

  it("approves one question on its own and confirms the approved set", async () => {
    const user = userEvent.setup();
    let approved = false;
    const calls = mockApi(({ method, path, body }) => {
      if (path === "/stages") return { stages: ["screening"] };
      if (path === "/positions/ceo/stages/screening/questions" && method === "GET") {
        return { stage: "screening", confirmed: false, questions: [question(1, approved ? "approved" : "proposed"), question(2)] };
      }
      if (path === "/questions/1/decision") {
        expect(body).toEqual({ action: "approve" });
        approved = true;
        return question(1, "approved");
      }
      if (path === "/positions/ceo/stages/screening/confirm") {
        return { stage: "screening", confirmed: true, questions: [question(1, "approved")] };
      }
      throw new Error(`unexpected ${method} ${path}`);
    });
    render(<QuestionReview slug="ceo" />);

    const approve = await screen.findAllByRole("button", { name: "Approve" });
    await user.click(approve[0]);
    await screen.findByRole("button", { name: "Confirm approved set (1)" });
    await user.click(screen.getByRole("button", { name: "Confirm approved set (1)" }));

    expect((await screen.findByRole("status")).textContent).toContain("The screening set is confirmed.");
    expect(calls.map((call) => call.path)).toContain("/positions/ceo/stages/screening/confirm");
  });

  it("confirm stays disabled until at least one question is approved", async () => {
    mockApi(({ path }) => {
      if (path === "/stages") return { stages: ["screening"] };
      if (path === "/positions/ceo/stages/screening/questions") {
        return { stage: "screening", confirmed: false, questions: [question(1)] };
      }
      throw new Error(`unexpected ${path}`);
    });
    render(<QuestionReview slug="ceo" />);

    expect((await screen.findByRole("button", { name: "Confirm approved set (0)" }) as HTMLButtonElement).disabled).toBe(true);
  });

  it("counts approved and waiting questions in the footer and on the confirm button", async () => {
    const user = userEvent.setup();
    let statuses = ["approved", "proposed", "rejected"];
    mockApi(({ method, path, body }) => {
      if (path === "/stages") return { stages: ["screening"] };
      if (path === "/positions/ceo/stages/screening/questions" && method === "GET") {
        return { stage: "screening", confirmed: false, questions: statuses.map((status, index) => question(index + 1, status)) };
      }
      if (path === "/questions/2/decision") {
        expect(body).toEqual({ action: "approve" });
        statuses = ["approved", "approved", "rejected"];
        return question(2, "approved");
      }
      throw new Error(`unexpected ${method} ${path}`);
    });
    render(<QuestionReview slug="ceo" />);

    expect(await screen.findByText("1 approved · 1 waiting for your decision")).toBeTruthy();
    expect(screen.getByRole("button", { name: "Confirm approved set (1)" })).toBeTruthy();

    await user.click(screen.getAllByRole("button", { name: "Approve" })[0]);

    expect(await screen.findByText("2 approved · 0 waiting for your decision")).toBeTruthy();
    expect(screen.getByRole("button", { name: "Confirm approved set (2)" })).toBeTruthy();
  });
});
