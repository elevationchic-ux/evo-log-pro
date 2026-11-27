import { test, expect } from '@playwright/test';

// ============================================================================
// TESTS D'AUTHENTIFICATION & AUTORISATION — alignés sur l'UI réelle
// (/login : champ "Identifiant ou email institutionnel" type=text,
//  erreur 401 = "Identifiants incorrects", landing /dashboard/global
//  après DomainLoadingExperience ~2,2 s, logout via menu profil → /logout)
// ============================================================================

const IDENT = 'input[placeholder*="Identifiant"]';
const PASS = 'input[type="password"]';

async function login(page: any, ident: string, pass: string) {
  await page.goto('/login');
  await page.fill(IDENT, ident);
  await page.fill(PASS, pass);
  // Enter : contourne l'overlay d'intro (fixed inset-0 z-[100]) qui
  // intercepte aléatoirement le clic sur le bouton submit
  await page.press(PASS, 'Enter');
  // Filet de sécurité : si aucune navigation ni erreur après 15 s
  // (soumission non déclenchée), recliquer le bouton submit
  await Promise.race([
    page.waitForURL((url) => !url.pathname.includes('/login'), { timeout: 15000 }).catch(() => {}),
    page.locator('text=Identifiants incorrects').waitFor({ timeout: 15000 }).catch(() => {}),
  ]);
  if (page.url().includes('/login') && !(await page.locator('text=Identifiants incorrects').isVisible().catch(() => false))) {
    await page.click('button[type="submit"]', { timeout: 10000 }).catch(() => {});
  }
}

test.describe('Authentication', () => {
  test('should display login page', async ({ page }) => {
    await page.goto('/login');

    await expect(page.locator('text=EVO-LOG').first()).toBeVisible();
    await expect(page.locator(IDENT)).toBeVisible();
    await expect(page.locator(PASS)).toBeVisible();
    await expect(page.locator('button[type="submit"]')).toBeVisible();
  });

  test('should login successfully with valid credentials', async ({ page }) => {
    await login(page, 'admin@kamlog.cm', 'password123');

    // Landing domain ~2,2 s puis /dashboard/global
    await page.waitForURL('/dashboard/global', { timeout: 60000 });
    await expect(page).toHaveURL('/dashboard/global');
  });

  test('should show error with invalid credentials', async ({ page }) => {
    await login(page, 'wrong@kamlog.cm', 'wrongpassword');

    await expect(page.locator('text=Identifiants incorrects')).toBeVisible({ timeout: 15000 });
    await expect(page).toHaveURL('/login');
  });

  test('should logout successfully', async ({ page }) => {
    await login(page, 'admin@kamlog.cm', 'password123');
    await page.waitForURL('/dashboard/global', { timeout: 60000 });

    // Menu profil (aria-haspopup="true") → "Se déconnecter" → /logout → /login
    await page.click('button[aria-haspopup="true"]');
    await page.click('text=Se déconnecter');
    await page.waitForURL('/login', { timeout: 60000 });
    await expect(page).toHaveURL('/login');
  });
});

// ============================================================================
// TESTS DE NIVEAUX D'ACCÈS (RBAC)
// ============================================================================

test.describe('Role-Based Access Control', () => {
  test('ADMIN should land on global dashboard', async ({ page }) => {
    await login(page, 'admin@kamlog.cm', 'password123');
    await page.waitForURL('/dashboard/global', { timeout: 60000 });
    await expect(page).toHaveURL('/dashboard/global');
  });

  test('MAGASINIER should land on magasin dashboard', async ({ page }) => {
    await login(page, 'magasinier@kamlog.cm', 'password123');
    await page.waitForURL('/magasin/dashboard', { timeout: 60000 });
    await expect(page).toHaveURL('/magasin/dashboard');
  });

  test('CLIENT_B2B should land on client portal', async ({ page }) => {
    await login(page, 'client@kamlog.cm', 'password123');
    await page.waitForURL('/client-portal', { timeout: 60000 });
    await expect(page).toHaveURL('/client-portal');
  });
});
