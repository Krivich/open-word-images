// @ts-check
const { defineConfig } = require('@playwright/test');

module.exports = defineConfig({
  testDir: './tests',
  timeout: 30000,
  expect: {
    timeout: 5000
  },
  use: {
    baseURL: 'http://localhost:8080',
    browserName: 'chromium',
    headless: true,
    viewport: { width: 1280, height: 720 },
  },
  webServer: {
    command: 'python -m http.server 8080',
    port: 8080,
    reuseExistingServer: true,
    cwd: process.cwd(),
  },
});
