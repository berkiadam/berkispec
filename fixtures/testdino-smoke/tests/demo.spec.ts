import { test, expect } from '@playwright/test';

const PAGE = `<!doctype html><html><body>
  <h1 id="title">Berki-spec smoke</h1>
  <button id="go">Indítás</button>
  <p id="out"></p>
  <script>
    document.getElementById('go').onclick = () => {
      document.getElementById('out').textContent = 'OK';
    };
  </script>
</body></html>`;

test.describe('TestDino smoke', () => {
  test('SM-01 a cím megjelenik', async ({ page }) => {
    await page.setContent(PAGE);
    await expect(page.locator('#title')).toHaveText('Berki-spec smoke');
  });

  test('SM-02 a gomb kiírja az eredményt', async ({ page }) => {
    await page.setContent(PAGE);
    await page.click('#go');
    await expect(page.locator('#out')).toHaveText('OK');
  });

  test('SM-03 a kiinduló állapot üres', async ({ page }) => {
    await page.setContent(PAGE);
    await expect(page.locator('#out')).toHaveText('');
  });

  test('SM-04 SZÁNDÉKOSAN bukó teszt', async ({ page }) => {
    await page.setContent(PAGE);
    await expect(page.locator('#title')).toHaveText('ez nem ez a szöveg');
  });

  test.skip('SM-05 szándékosan kihagyott teszt', async () => {
    expect(true).toBe(true);
  });
});
