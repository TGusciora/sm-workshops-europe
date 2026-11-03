// Playwright end-to-end configuration (ADR-0013). Run with `npm run e2e` from frontend/.
// Playwright starts the backend with a scripted LLM and a fresh data folder, then the Vite
// dev server, and records a video of every test under test-results/.
import { defineConfig, devices } from "@playwright/test";
import { fileURLToPath } from "node:url";
import path from "node:path";

const frontendDir = fileURLToPath(new URL(".", import.meta.url));
const backendDir = path.resolve(frontendDir, "..", "backend");
const e2eRoot = path.join(frontendDir, "test-results", "e2e-data");

export default defineConfig({
  testDir: "e2e",
  outputDir: "test-results",
  // One backend with one database, so the tests run one after another.
  fullyParallel: false,
  // The walkthrough is one long journey with slow motion, so it gets more than the default 30s.
  timeout: 180_000,
  workers: 1,
  retries: 0,
  reporter: [
    ["list"],
    ["html", { open: "never", outputFolder: "playwright-report" }],
  ],
  use: {
    baseURL: "http://127.0.0.1:5173",
    viewport: { width: 1280, height: 900 },
    video: "on",
    trace: "retain-on-failure",
    screenshot: "only-on-failure",
  },
  projects: [
    {
      name: "chromium",
      // slowMo pauses between actions so the recorded video can be followed by a person.
      use: { ...devices["Desktop Chrome"], launchOptions: { slowMo: 700 } },
    },
  ],
  webServer: [
    {
      command: "uv run uvicorn --app-dir . tests.e2e_app:create_app --factory --host 127.0.0.1 --port 8001",
      cwd: backendDir,
      url: "http://127.0.0.1:8001/api/health",
      env: { E2E_ROOT: e2eRoot },
      reuseExistingServer: false,
      timeout: 120_000,
    },
    {
      command: "npm run dev -- --strictPort",
      cwd: frontendDir,
      url: "http://127.0.0.1:5173",
      reuseExistingServer: false,
      timeout: 120_000,
    },
  ],
});
