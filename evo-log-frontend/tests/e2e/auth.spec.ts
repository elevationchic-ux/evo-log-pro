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
  await page.click('button[type="submit"]');
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
    await page.waitForURL('/dashboard/global', { timeout: 30000 });
    await expect(page).toHaveURL('/dashboard/global');
  });

  test('should show error with invalid credentials', async ({ page }) => {
    await login(page, 'wrong@kamlog.cm', 'wrongpassword');

    await expect(page.locator('text=Identifiants incorrects')).toBeVisible({ timeout: 15000 });
    await expect(page).toHaveURL('/login');
  });

  test('should logout successfully', async ({ page }) => {
    await login(page, 'admin@kamlog.cm', 'password123');
    await page.waitForURL('/dashboard/global', { timeout: 30000 });

    // Menu profil (aria-haspopup="true") → "Se déconnecter" → /logout → /login
    await page.click('button[aria-haspopup="true"]');
    await page.click('text=Se déconnecter');
    await page.waitForURL('/login', { timeout: 20000 });
    await expect(page).toHaveURL('/login');
  });
});

// ============================================================================
// TESTS DE NIVEAUX D'ACCÈS (RBAC)
// ============================================================================

test.describe('Role-Based Access Control', () => {
  test('ADMIN should land on global dashboard', async ({ page }) => {
    await login(page, 'admin@kamlog.cm', 'password123');
    await page.waitForURL('/dashboard/global', { timeout: 30000 });
    await expect(page).toHaveURL('/dashboard/global');
  });

  test('MAGASINIER should land on magasin dashboard', async ({ page }) => {
    await login(page, 'magasinier@kamlog.cm', 'password123');
    await page.waitForURL('/magasin/dashboard', { timeout: 30000 });
    await expect(page).toHaveURL('/magasin/dashboard');
  });

  test.fixme('CLIENT should only access B2B Portal — aucun rôle CLIENT seedé (portail B2B = flux dédié à aligner)', async ({ page }) => {
    await login(page, 'client@kamlog.cm', 'password123');
    await expect(page).toHaveURL('/client-portal');
  });
});
