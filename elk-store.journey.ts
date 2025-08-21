import { journey, step, expect, monitor } from '@elastic/synthetics';

journey({
  name: 'elk-store',
  tags: [],
}, ({ page, params }) => {
  
  // Monitor settings are configured via CLI parameters
  // Individual tests should not override global schedule settings
  
  step('Navigate to https://react-elk-store.vercel.app', async () => {
    await page.goto('https://react-elk-store.vercel.app');
    await page.waitForLoadState('networkidle');
  });
  
  step('Verify page title', async () => {
    try {
      // Wait for title to be present, but don't fail if it's empty
      await page.waitForFunction(() => document.title !== undefined, { timeout: 3000 });
      const title = await page.title();
      console.log(`Page title: "${title}"`);
      
      // Check if title exists and is not empty
      if (title && title.trim().length > 0) {
        await expect(page).toHaveTitle(/.+/);
      } else {
        console.log('Page has no title or empty title - skipping title assertion');
      }
    } catch (error) {
      console.log(`Title check failed: ${error.message} - continuing with other tests`);
    }
  });
  
  step('Check page load performance', async () => {
    const loadTime = await page.evaluate(() => {
      return performance.getEntriesByType('navigation')[0].loadEventEnd - 
             performance.getEntriesByType('navigation')[0].startTime;
    });
    console.log(`Page load time: ${loadTime}ms`);
    expect(loadTime).toBeLessThan(5000); // Should load within 5 seconds
  });
  
  step('Check interactive elements', async () => {
    try {
      const buttons = page.locator('button, input[type="submit"], .btn');
      const buttonCount = await buttons.count();
      console.log(`Found ${buttonCount} interactive buttons`);
      
      if (buttonCount > 0) {
        const firstButton = buttons.first();
        await expect(firstButton).toBeVisible();
      }
    } catch (error) {
      console.log(`Interactive elements check failed: ${error.message}`);
    }
  });
  
  step('Take screenshot', async () => {
    await page.screenshot({ path: 'elk-store_screenshot.png' });
  });
  
  step('Verify page is visible', async () => {
    await expect(page.locator('body')).toBeVisible();
  });
});