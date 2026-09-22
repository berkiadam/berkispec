import { defineConfig } from '@playwright/test';

// A lényeg a reporter-lánc: a keret JUnit+HTML riportja ÉS a TestDino riporter
// EGYSZERRE van bekötve — pontosan ezt az együttélést akarjuk mérni (TM2).
export default defineConfig({
  testDir: './tests',
  reporter: [
    ['list'],
    ['junit', { outputFile: 'test-report/junit.xml' }],
    ['html', { outputFolder: 'test-report/html', open: 'never' }],
    ['@testdino/playwright', { token: process.env.TESTDINO_TOKEN }],
  ],
  use: { screenshot: 'only-on-failure', trace: 'retain-on-failure' },
});
