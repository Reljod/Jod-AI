import { test, expect } from "@playwright/test";

test.describe("Landing page", () => {
  test("renders the app logo and heading", async ({ page }) => {
    await page.goto("/");

    await expect(page.locator("h1").first()).toHaveText("Jod-AI");
    await expect(page.locator("text=Welcome to Jod-AI")).toBeVisible();
  });

  test("displays the favicon SVG logo", async ({ page }) => {
    await page.goto("/");
    await expect(page.locator("svg").first()).toBeVisible();
  });

  test("has correct page title", async ({ page }) => {
    await page.goto("/");
    await expect(page).toHaveTitle("Jod-AI");
  });

  test("matches the visual snapshot", async ({ page }) => {
    await page.goto("/");
    await page.waitForLoadState("networkidle");
    await expect(page).toHaveScreenshot("landing-page.png", {
      maxDiffPixelRatio: 0.05,
    });
  });
});
