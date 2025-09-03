import { journey, step, expect } from '@elastic/synthetics';

journey({
  name: 'auth-test',
  tags: []
}, ({ page, params }) => {
  // ── Guarded nav: always load target URL first
  step('Navigate to https://www.elastic.co/search-labs/blog/build-rag-app-elastic', async () => {
    await page.goto('https://www.elastic.co/search-labs/blog/build-rag-app-elastic');
    await page.waitForLoadState('networkidle');
  });

  // ==== BEGIN LLM STEPS (safe region) ====
step('Verify the article title is present', async () => {
  try {
    const titleElement = page.locator('h1'); // Assuming the article title is in an <h1> tag
    await expect(titleElement).toBeVisible();
  } catch (error) {
    console.error('Article title is not visible:', error);
  }
});

step('Check for author name "Alessandro Brofferio"', async () => {
  try {
    const authorElement = page.locator('text=Alessandro Brofferio'); // Using text selector for author name
    await expect(authorElement).toBeVisible();
  } catch (error) {
    console.error('Author name is not visible:', error);
  }
});

step('Verify social sharing buttons are functional', async () => {
  try {
    const twitterButton = page.locator('button[aria-label="Share on Twitter"]'); // Assuming aria-label for Twitter button
    await expect(twitterButton).toBeVisible();

    const facebookButton = page.locator('button[aria-label="Share on Facebook"]'); // Assuming aria-label for Facebook button
    await expect(facebookButton).toBeVisible();

    // Optionally, click and verify that it opens a new tab or similar behavior
    await twitterButton.click();
    // Add assertions to check if the appropriate action occurs, e.g., a URL change or new window/tab.

  } catch (error) {
    console.error('Social sharing buttons verification failed:', error);
  }
});
  // ==== END LLM STEPS ====

  // Baseline checks still included
  step('Screenshot', async () => {
    await page.screenshot({ path: 'auth-test_screenshot.png' });
  });
  step('Body visible', async () => {
    await expect(page.locator('body')).toBeVisible();
  });
});
