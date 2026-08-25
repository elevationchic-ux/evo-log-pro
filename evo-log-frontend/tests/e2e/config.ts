import { defineConfig, devices } from '@playwright/test';

// Configuration des tests E2E pour KAMLOG ERP
export default defineConfig({
  testDir: './tests',
  
  // Configuration du timeout
  timeout: 30 * 1000,
  expect: {
    timeout: 5000,
  },
  
  // Parallélisation
  fullyParallel: true,
  forbidOnly: !!process.env.CI,
  retries: process.env.CI ? 2 : 0,
  workers: process.env.CI ? 1 : undefined,
  
  // Reporter
  reporter: [
    ['html', { outputFile: 'report.html' }],
    ['list'],
  ],
  
  // Configuration des navigateurs
  use: {
    baseURL: process.env.BASE_URL || 'http://localhost:3000',
    trace: 'on-first-retry',
    screenshot: 'only-on-failure',
    video: 'retain-on-failure',
  },

  // Configuration des projets (différents navigateurs)
  projects: [
    {
      name: 'chromium',
      use: { ...devices['Desktop Chrome'] },
    },
    {
      name: 'firefox',
      use: { ...devices['Desktop Firefox'] },
    },
    {
      name: 'webkit',
      use: { ...devices['Desktop Safari'] },
    },
    // Tests mobile
    {
      name: 'Mobile Chrome',
      use: { ...devices['Pixel 5'] },
    },
    {
      name: 'Mobile Safari',
      use: { ...devices['iPhone 12'] },
    },
  ],

  // Configuration du serveur web (pour CI)
  webServer: {
    command: 'npm run dev',
    url: 'http://localhost:3000',
    reuseExistingServer: !process.env.CI,
    timeout: 120 * 1000,
  },
});