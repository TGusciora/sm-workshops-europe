// End-to-end walkthrough of every screen the hiring manager uses today (F0002, F0003, F0005,
// F0010). One test, so one video shows the whole journey. The LLM is scripted (ADR-0013).
import { expect, test, type Page } from "@playwright/test";

const POSITION = "Head of Sales";
const SECOND_POSITION = "Head of Marketing";

// The sidebar button also contains the "Open" badge, so match it by its class and its title.
function sidebarPosition(page: Page, title: string) {
  return page.locator("button.position").filter({ hasText: title });
}

test("hiring manager runs the whole process for a position", async ({ page }) => {
  await test.step("open the app and check the backend", async () => {
    await page.goto("/");
    await expect(page.getByRole("heading", { name: "Choose a position" })).toBeVisible();
    await expect(page.getByText(/Backend ok/)).toBeVisible();
  });

  await test.step("add a position", async () => {
    await page.getByLabel("New position", { exact: true }).fill(POSITION);
    await page.getByRole("button", { name: "Add position" }).click();
    await expect(page.getByRole("heading", { name: POSITION, level: 1 })).toBeVisible();
    await expect(sidebarPosition(page, POSITION)).toHaveAttribute("aria-pressed", "true");
  });

  await test.step("job description: the chat proposes a draft and it is accepted", async () => {
    await page.getByLabel("Message", { exact: true }).fill("We need a head of sales who grows the team.");
    await page.getByRole("button", { name: "Send" }).click();
    const draft = page.getByLabel("Draft", { exact: true });
    await expect(draft).toBeVisible();
    await expect(page.getByRole("heading", { name: "Draft · not saved" })).toBeVisible();
    await page.getByRole("button", { name: "Accept draft" }).click();
    await expect(page.getByText(/Saved to /)).toBeVisible();
    await page.getByText("Current job description").click();
    await expect(page.locator("pre.code-block")).toContainText("We need a head of sales");
  });

  await test.step("job description: a changed draft is accepted as an edit", async () => {
    await page.getByLabel("Message", { exact: true }).fill("Add a line about travel.");
    await page.getByRole("button", { name: "Send" }).click();
    await page.getByLabel("Edit the draft before accepting", { exact: true }).fill("# Job description\n\nEdited by hand.\n");
    await expect(page.getByRole("button", { name: "Accept edited draft" })).toBeVisible();
    await page.getByRole("button", { name: "Accept edited draft" }).click();
    await expect(page.getByText(/Saved to /)).toBeVisible();
    await expect(page.locator("pre.code-block")).toContainText("Edited by hand.");
  });

  await test.step("job description: a draft can be rejected and nothing is saved", async () => {
    await page.getByLabel("Message", { exact: true }).fill("Make it shorter.");
    await page.getByRole("button", { name: "Send" }).click();
    await expect(page.getByRole("heading", { name: "Draft · not saved" })).toBeVisible();
    await page.getByRole("button", { name: "Reject draft" }).click();
    await expect(page.getByRole("heading", { name: "Draft · not saved" })).toHaveCount(0);
    await expect(page.locator("pre.code-block")).toContainText("Edited by hand.");
  });

  await test.step("interview questions: propose, edit, approve, reject and confirm", async () => {
    await page.getByRole("button", { name: "Interview questions" }).click();
    await page.getByLabel("Stage", { exact: true }).selectOption("technical");
    await page.getByRole("button", { name: "Propose questions" }).click();
    const cards = page.locator("ul.questions > li.card");
    await expect(cards).toHaveCount(5);

    await cards.nth(0).getByRole("button", { name: "Approve" }).click();
    await cards.nth(1).getByRole("button", { name: "Approve" }).click();

    await cards.nth(2).getByRole("button", { name: "Edit" }).click();
    await page.getByLabel("Question", { exact: true }).fill("Edited question for the technical stage?");
    await page.getByRole("button", { name: "Save edit" }).click();
    await expect(page.getByText("Edited question for the technical stage?")).toBeVisible();

    await cards.nth(3).getByRole("button", { name: "Reject" }).click();

    await expect(page.getByRole("button", { name: "Confirm approved set (3)" })).toBeEnabled();
    await page.getByRole("button", { name: "Confirm approved set (3)" }).click();
    await expect(page.getByText("The technical set is confirmed.")).toBeVisible();
  });

  await test.step("interviews: plan, edit, cancel and keep the record", async () => {
    await page.getByRole("button", { name: "Interviews" }).click();
    await page.getByRole("button", { name: "Plan interview" }).click();
    const form = page.getByRole("form", { name: "Plan interview" });
    await form.getByLabel("Stage", { exact: true }).selectOption("technical");
    await form.getByLabel("Date", { exact: true }).fill("2026-11-10");
    await form.getByLabel("Start time", { exact: true }).fill("10:00");
    await form.getByLabel("Duration (minutes)", { exact: true }).fill("60");
    await form.getByLabel("Interviewer", { exact: true }).fill("Anna Kowalska");
    await form.getByLabel("Place or meeting link", { exact: true }).fill("Room 2");
    await form.getByLabel("Candidate reference", { exact: true }).fill("C-14");
    await form.getByRole("button", { name: "Save interview" }).click();

    const day = page.getByRole("region", { name: "2026-11-10" });
    await expect(day.getByText("10:00")).toBeVisible();
    await expect(day.getByText("Anna Kowalska")).toBeVisible();

    await day.getByRole("button", { name: "Edit" }).click();
    await page.getByRole("form", { name: "Edit interview" }).getByLabel("Start time", { exact: true }).fill("11:00");
    await page.getByRole("button", { name: "Save changes" }).click();
    await expect(day.getByText("11:00")).toBeVisible();

    await day.getByRole("button", { name: "Cancel interview" }).click();
    await page.getByRole("button", { name: "Yes, cancel it" }).click();
    await expect(day.getByText("Cancelled")).toBeVisible();
    await expect(day.getByRole("button", { name: "Edit" })).toHaveCount(0);
  });

  await test.step("interviews: an invalid duration is refused and nothing is saved", async () => {
    await page.getByRole("button", { name: "Plan interview" }).click();
    const form = page.getByRole("form", { name: "Plan interview" });
    await form.getByLabel("Date", { exact: true }).fill("2026-11-11");
    await form.getByLabel("Start time", { exact: true }).fill("09:30");
    await form.getByLabel("Duration (minutes)", { exact: true }).fill("2");
    await form.getByLabel("Interviewer", { exact: true }).fill("Anna Kowalska");
    await form.getByLabel("Candidate reference", { exact: true }).fill("C-15");
    await form.getByRole("button", { name: "Save interview" }).click();
    await expect(form.getByLabel("Duration (minutes)", { exact: true })).toHaveJSProperty("validity.valid", false);
    await form.getByRole("button", { name: "Discard" }).click();
    await expect(page.getByRole("region", { name: "2026-11-11" })).toHaveCount(0);
  });

  await test.step("a second position keeps its own data", async () => {
    await page.getByLabel("New position", { exact: true }).fill(SECOND_POSITION);
    await page.getByRole("button", { name: "Add position" }).click();
    await expect(page.getByRole("heading", { name: SECOND_POSITION, level: 1 })).toBeVisible();
    await page.getByRole("button", { name: "Interviews" }).click();
    await expect(page.getByText("No interviews planned for this position yet.")).toBeVisible();

    await sidebarPosition(page, POSITION).click();
    await page.getByRole("button", { name: "Interviews" }).click();
    await expect(page.getByRole("region", { name: "2026-11-10" })).toBeVisible();
  });

  await test.step("everything is still there after a reload", async () => {
    await page.reload();
    await sidebarPosition(page, POSITION).click();
    await page.getByRole("button", { name: "Job description" }).click();
    await expect(page.locator("pre.code-block")).toContainText("Edited by hand.");
    await page.getByRole("button", { name: "Interview questions" }).click();
    await page.getByLabel("Stage", { exact: true }).selectOption("technical");
    await expect(page.getByText("The technical set is confirmed.")).toBeVisible();
    await page.getByRole("button", { name: "Interviews" }).click();
    await expect(page.getByRole("region", { name: "2026-11-10" }).getByText("Cancelled")).toBeVisible();
  });
});
