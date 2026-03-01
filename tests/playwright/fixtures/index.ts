/**
 * Shared Playwright fixtures for JoinMarket NG E2E tests.
 *
 * The wallet is created ONCE in global setup (global-setup.ts) and
 * its credentials saved to tmp/test-wallet.json. Fixtures here load
 * those credentials and expose helpers for logging in via the UI.
 *
 * All user-facing actions go through the browser. The API helpers are
 * used only for setup/teardown (funding the wallet, mining blocks).
 */

import * as fs from "fs";
import * as path from "path";
import { test as base, type Page } from "@playwright/test";
import * as api from "./jmwalletd-api";
import * as btc from "./bitcoin-rpc";

export interface WalletCredentials {
  walletName: string;
  password: string;
  token: string;
}

const CREDS_FILE = path.join(__dirname, "../../../tmp/test-wallet.json");

export function loadCredentials(): WalletCredentials {
  if (!fs.existsSync(CREDS_FILE)) {
    throw new Error(`Wallet credentials file not found: ${CREDS_FILE}. Run global setup first.`);
  }
  return JSON.parse(fs.readFileSync(CREDS_FILE, "utf-8"));
}

export function saveCredentials(creds: WalletCredentials): void {
  const dir = path.dirname(CREDS_FILE);
  if (!fs.existsSync(dir)) fs.mkdirSync(dir, { recursive: true });
  fs.writeFileSync(CREDS_FILE, JSON.stringify(creds, null, 2));
}

/**
 * Dismiss any overlay dialogs (e.g. the JAM intro/welcome modal) that might
 * block interaction with the underlying page.  We retry a few times because
 * React modals can animate in after the URL has already stabilised.
 */
export async function dismissDialogs(page: Page): Promise<void> {
  // Selector covering Radix dialogs/sheets (have ARIA/data attributes).
  const OVERLAY_SELECTOR = [
    '[role="dialog"]:visible',
    '[data-state="open"][data-slot="dialog-content"]:visible',
    '[data-state="open"][data-slot="sheet-content"]:visible',
  ].join(", ");

  for (let attempt = 0; attempt < 10; attempt++) {
    // Grace-period so an animating-in overlay has time to settle.
    await page.waitForTimeout(500);

    let dismissed = false;

    // --- Strategy 1: Tour/onboarding tooltip — "Skip tour" button. ---
    // Check this first because it appears after login and overlays the UI.
    const skipTourBtn = page.getByRole("button", { name: "Skip tour" }).first();
    if (await skipTourBtn.isVisible().catch(() => false)) {
      console.log(`[dismissDialogs] Clicking "Skip tour" button (attempt ${attempt + 1})`);
      await skipTourBtn.click({ force: true });
      await page.waitForTimeout(600);
      dismissed = true;
    }

    if (!dismissed) {
      // --- Strategy 2: Radix dialog/sheet — click its top-right × corner. ---
      const overlayEl = page.locator(OVERLAY_SELECTOR).first();
      if (await overlayEl.isVisible().catch(() => false)) {
        console.log(`[dismissDialogs] Radix overlay visible (attempt ${attempt + 1})`);
        const box = await overlayEl.boundingBox();
        if (box) {
          await page.mouse.click(box.x + box.width - 20, box.y + 20);
          console.log(`[dismissDialogs] Clicked top-right × via bounding box`);
          await page.waitForTimeout(600);
          dismissed = true;
        }
      }
    }

    if (!dismissed) {
      // --- Strategy 3: Plain-div overlays (JAM Cheatsheet) expose a visible
      // "Close" button.  Only click if the button is within the viewport to
      // avoid hanging on off-screen sidebar close buttons.
      const closeBtns = page
        .getByRole("button", { name: "Close" })
        .filter({ hasNot: page.locator("[data-sidebar]") });
      const count = await closeBtns.count().catch(() => 0);
      for (let i = 0; i < count; i++) {
        const btn = closeBtns.nth(i);
        if (!(await btn.isVisible().catch(() => false))) continue;
        const box = await btn.boundingBox().catch(() => null);
        if (!box) continue;
        const vp = page.viewportSize();
        if (vp && box.x >= 0 && box.y >= 0 && box.x + box.width <= vp.width + 50 && box.y + box.height <= vp.height + 50) {
          console.log(`[dismissDialogs] Clicking in-viewport "Close" button (attempt ${attempt + 1})`);
          await btn.click({ force: true });
          await page.waitForTimeout(600);
          dismissed = true;
          break;
        }
      }
    }

    // Nothing left to dismiss.
    if (!dismissed) break;
  }

  // Final wait: ensure no Radix overlay is still visible.
  await page
    .locator(OVERLAY_SELECTOR)
    .first()
    .waitFor({ state: "hidden", timeout: 3_000 })
    .catch(() => null);
}

/** Navigate to /login and log in with the test wallet. */
export async function loginViaUI(
  page: Page,
  walletName: string,
  password: string,
): Promise<void> {
  await page.goto("/");

  // If already on main wallet page, no login needed.
  if (page.url().match(/\/$/)) {
    const jarsVisible = await page.getByText("Wallet distribution").isVisible().catch(() => false);
    if (jarsVisible) return;
  }

  // Should be redirected to /login.
  await page.waitForURL(/login/, { timeout: 15_000 });

  // Dismiss any overlay dialogs (e.g. JAM intro/welcome modal).
  await dismissDialogs(page);

  // Open the wallet select dropdown.
  await page.locator('[role="combobox"]').click();
  const displayName = walletName.replace(".jmdat", "");
  await page.getByRole("option", { name: displayName }).click();

  await page.locator("#login-password").fill(password);
  await page.getByRole("button", { name: "Unlock" }).click();

  await page.waitForURL("/", { timeout: 30_000 });
  await page.getByText("Wallet distribution").waitFor({ timeout: 30_000 });

  // After login, JAM may show a post-login overlay/modal (e.g. "Welcome back!").
  // Dismiss it so navigation links are clickable.
  await dismissDialogs(page);

  // Wait for any full-page Radix Sheet/Dialog backdrop to fully disappear.
  // The backdrop is a `div.fixed.inset-0.z-50` wrapper that may persist through
  // CSS exit animations after the inner [role=dialog] closes.
  // We wait up to 3s. If still present, force-click through it in tests.
  for (const sel of ["div.fixed.inset-0.z-50"]) {
    await page
      .locator(sel)
      .first()
      .waitFor({ state: "hidden", timeout: 3_000 })
      .catch(() => null);
  }
  // Small grace period for animation to fully complete.
  await page.waitForTimeout(300);
}

interface TestFixtures {
  /** Credentials for the single shared test wallet. */
  wallet: WalletCredentials;
  /** Credentials for the single shared test wallet (alias for wallet). */
  fundedWallet: WalletCredentials;
  /** Bitcoin RPC helpers (for mining/funding in setup). */
  btcRpc: typeof btc;
  /** Bitcoin RPC helpers (alias for btcRpc). */
  bitcoinRpc: typeof btc;
  /** jmwalletd API helpers (for setup/assertions). */
  walletApi: typeof api;
}

export const test = base.extend<TestFixtures>({
  wallet: async ({}, use) => {
    await use(loadCredentials());
  },

  fundedWallet: async ({}, use) => {
    // Always re-unlock to get a fresh, valid token regardless of what previous
    // tests may have done to the session.  unlockWallet handles all cases:
    //   - same wallet open → re-issues token (no error)
    //   - different wallet open → locks it first, then unlocks ours
    const creds = loadCredentials();
    let freshToken = creds.token;
    try {
      const result = await api.unlockWallet(creds.walletName, creds.password);
      freshToken = result.token;
      // Ensure the descriptor wallet scan has completed before the test runs.
      await api.waitForBalance(freshToken);
    } catch (err) {
      console.warn("[fundedWallet] unlock/balance check failed, using saved token:", err);
    }
    await use({ ...creds, token: freshToken });
  },

  btcRpc: async ({}, use) => {
    await use(btc);
  },

  bitcoinRpc: async ({}, use) => {
    await use(btc);
  },

  walletApi: async ({}, use) => {
    await use(api);
  },
});

export { expect } from "@playwright/test";
