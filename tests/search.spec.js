// @ts-check
const { test, expect } = require('@playwright/test');

test.describe('Word search and image display', () => {
  test('searching for "cat" should display cat image in gallery', async ({ page }) => {
    await page.goto('/');

    // Проверяем что страница загрузилась
    await expect(page.locator('h1')).toContainText('open-word-images');

    // Ждём загрузки manifest.json и рендера галереи
    await page.waitForTimeout(1000);

    // Проверяем что галерея не пустая
    const cards = page.locator('.grid .card');
    const count = await cards.count();
    expect(count).toBeGreaterThanOrEqual(1);

    // Вводим "cat" в поиск
    const searchInput = page.locator('#search');
    await searchInput.fill('cat');

    // Ждём обработки поиска
    await page.waitForTimeout(500);

    // Проверяем что галерея отфильтрована — только одна карточка "cat"
    const filteredCards = page.locator('.grid .card');
    const filteredCount = await filteredCards.count();
    expect(filteredCount).toBe(1);

    // Проверяем что карточка содержит текст "CAT"
    const catCardWord = page.locator('.card .word', { hasText: 'CAT' });
    await expect(catCardWord).toBeVisible();

    // Проверяем что на карточке есть картинка с правильным src
    const catImg = page.locator('.grid .card img');
    await expect(catImg).toBeVisible();
    const imgSrc = await catImg.getAttribute('src');
    expect(imgSrc).toContain('cat_v1.png');

    // Проверяем что картинка реально загрузилась (не битая)
    const naturalWidth = await catImg.evaluate(img => img.naturalWidth);
    expect(naturalWidth).toBeGreaterThan(0);

    // Проверяем мету с количеством версий
    const catMeta = page.locator('.card .meta');
    await expect(catMeta).toBeVisible();
  });

  test('searching for unknown word should show generator', async ({ page }) => {
    await page.goto('/');
    await page.waitForTimeout(1000);

    const searchInput = page.locator('#search');
    await searchInput.fill('nonexistentword');
    await page.waitForTimeout(500);

    // Генератор должен появиться
    const generator = page.locator('#generator');
    await expect(generator).toBeVisible();
  });
});
