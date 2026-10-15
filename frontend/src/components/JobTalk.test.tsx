import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { afterEach, describe, expect, it, vi } from "vitest";
import { JobTalk } from "./JobTalk";
import { mockApi, problem } from "../test/mockApi";

afterEach(() => {
  vi.unstubAllGlobals();
});

const emptyChat = { messages: [], draft: null };
const currentJd = { slug: "ceo", text: "# CEO\n\nOld text." };

describe("JobTalk", () => {
  it("shows the assistant's reply and the draft apart from the chat", async () => {
    const user = userEvent.setup();
    mockApi(({ method, path }) => {
      if (path === "/positions/ceo/chat" && method === "GET") return emptyChat;
      if (path === "/positions/ceo/job-description") return currentJd;
      if (path === "/positions/ceo/chat" && method === "POST") {
        return {
          messages: [
            { role: "user", content: "Shorter please", created_at: "" },
            { role: "assistant", content: "Done.", created_at: "" },
          ],
          draft: { id: 3, text: "# CEO\n\nNew text.", status: "pending" },
        };
      }
      throw new Error(`unexpected ${method} ${path}`);
    });
    render(<JobTalk slug="ceo" />);
    await user.type(await screen.findByLabelText("Message"), "Shorter please");
    await user.click(screen.getByRole("button", { name: "Send" }));

    expect(await screen.findByLabelText("Draft")).toBeTruthy();
    expect((screen.getByLabelText("Edit the draft before accepting") as HTMLTextAreaElement).value).toBe("# CEO\n\nNew text.");
    expect(screen.getByText(/Done\./)).toBeTruthy();
  });

  it("sends an edit with the edited text when the hiring manager changes the draft", async () => {
    const user = userEvent.setup();
    const calls = mockApi(({ method, path, body }) => {
      if (path === "/positions/ceo/chat" && method === "GET") return emptyChat;
      if (path === "/positions/ceo/job-description") return currentJd;
      if (path === "/positions/ceo/chat") {
        return { messages: [], draft: { id: 3, text: "Draft.", status: "pending" } };
      }
      if (path === "/drafts/3/decision") {
        expect(body).toEqual({ action: "edit", text: "Edited." });
        return { status: "accepted", path: "hiring/ceo/ceo.md" };
      }
      throw new Error(`unexpected ${method} ${path}`);
    });
    render(<JobTalk slug="ceo" />);
    await user.type(await screen.findByLabelText("Message"), "go");
    await user.click(screen.getByRole("button", { name: "Send" }));
    const editor = await screen.findByLabelText("Edit the draft before accepting");
    await user.clear(editor);
    await user.type(editor, "Edited.");

    await user.click(screen.getByRole("button", { name: "Accept edited draft" }));

    expect((await screen.findByRole("status")).textContent).toContain("Saved to hiring/ceo/ceo.md");
    expect(calls.some((call) => call.path === "/drafts/3/decision")).toBe(true);
  });

  it("rejecting a draft writes nothing and removes it", async () => {
    const user = userEvent.setup();
    mockApi(({ method, path, body }) => {
      if (path === "/positions/ceo/chat" && method === "GET") {
        return { messages: [], draft: { id: 4, text: "Draft.", status: "pending" } };
      }
      if (path === "/positions/ceo/job-description") return currentJd;
      if (path === "/drafts/4/decision") {
        expect(body).toMatchObject({ action: "reject" });
        return { status: "rejected", path: null };
      }
      throw new Error(`unexpected ${method} ${path}`);
    });
    render(<JobTalk slug="ceo" />);

    await user.click(await screen.findByRole("button", { name: "Reject draft" }));

    await waitFor(() => expect(screen.queryByLabelText("Draft")).toBeNull());
    expect(screen.queryByRole("status")).toBeNull();
  });

  it("shows a backend error when the reply cannot be produced", async () => {
    const user = userEvent.setup();
    mockApi(({ method, path }) => {
      if (path === "/positions/ceo/chat" && method === "GET") return emptyChat;
      if (path === "/positions/ceo/job-description") return currentJd;
      if (path === "/positions/ceo/chat") {
        throw problem(409, "ANTHROPIC_API_KEY is set");
      }
      throw new Error(`unexpected ${method} ${path}`);
    });
    render(<JobTalk slug="ceo" />);
    await user.type(await screen.findByLabelText("Message"), "go");
    await user.click(screen.getByRole("button", { name: "Send" }));

    expect((await screen.findByRole("alert")).textContent).toContain("ANTHROPIC_API_KEY is set");
  });
});
