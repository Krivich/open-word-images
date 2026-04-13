const { chromium } = require('@playwright/test');

(async () => {
  const browser = await chromium.launch();
  const page = await browser.newPage();

  const logs = [];
  page.on('console', msg => {
    logs.push(msg.text());
    console.log('LOG:', msg.text());
  });

  const start = Date.now();
  await page.goto('http://localhost:8765');

  // Ждём, пока gallery не заполнится
  await page.waitForSelector('.card', { timeout: 30000 });

  const cardsCount = await page.$$eval('.card', els => els.length);
  const elapsed = ((Date.now() - start) / 1000).toFixed(2);

  console.log(`\n📊 Cards rendered: ${cardsCount}`);
  console.log(`⏱️ Total time: ${elapsed}s`);
  console.log('\n📋 Console logs:');
  logs.forEach(l => console.log('  ', l));

  await browser.close();
})();
