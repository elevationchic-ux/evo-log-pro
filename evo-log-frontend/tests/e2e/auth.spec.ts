import { test, expect } from '@playwright/test';

// ============================================================================
// TESTS D'AUTHENTIFICATION & AUTORISATION
// ============================================================================

test.describe('Authentication', () => {
  test('should display login page', async ({ page }) => {
    await page.goto('/login');
    
    // Vérifier les éléments de la page de connexion
    await expect(page.locator('text=EVO-LOG')).toBeVisible();
    await expect(page.locator('input[type="email"]')).toBeVisible();
    await expect(page.locator('input[type="password"]')).toBeVisible();
    await expect(page.locator('button[type="submit"]')).toBeVisible();
  });

  test('should login successfully with valid credentials', async ({ page }) => {
    await page.goto('/login');
    
    // Remplir le formulaire de connexion
    await page.fill('input[type="email"]', 'admin@kamlog.cm');
    await page.fill('input[type="password"]', 'password123');
    
    // Soumettre le formulaire
    await page.click('button[type="submit"]');
    
    // Vérifier la redirection vers le dashboard
    await expect(page).toHaveURL('/dashboard/global', { timeout: 10000 });
    
    // Vérifier que l'utilisateur est connecté
    await expect(page.locator('text=admin@kamlog.cm')).toBeVisible();
  });

  test('should show error with invalid credentials', async ({ page }) => {
    await page.goto('/login');
    
    await page.fill('input[type="email"]', 'wrong@kamlog.cm');
    await page.fill('input[type="password"]', 'wrongpassword');
    await page.click('button[type="submit"]');
    
    // Vérifier le message d'erreur
    await expect(page.locator('text=Identifiants invalides')).toBeVisible();
  });

  test('should logout successfully', async ({ page }) => {
    // Se connecter d'abord
    await page.goto('/login');
    await page.fill('input[type="email"]', 'admin@kamlog.cm');
    await page.fill('input[type="password"]', 'password123');
    await page.click('button[type="submit"]');
    await page.waitForURL('/dashboard/global');
    
    // Ouvrir le menu utilisateur
    await page.click('button[aria-haspopup="menu"]');
    
    // Cliquer sur déconnexion
    await page.click('text=Déconnexion');
    
    // Vérifier la redirection vers login
    await expect(page).toHaveURL('/login');
  });
});

// ============================================================================
// TESTS DE NIVEAUX D'ACCÈS (RBAC)
// ============================================================================

test.describe('Role-Based Access Control', () => {
  test('ADMIN should have access to all modules', async ({ page }) => {
    // Login as admin
    await page.goto('/login');
    await page.fill('input[type="email"]', 'admin@kamlog.cm');
    await page.fill('input[type="password"]', 'password123');
    await page.click('button[type="submit"]');
    await page.waitForURL('/dashboard/global');
    
    // Vérifier l'accès au module Admin
    await page.click('text=Admin');
    await expect(page).toHaveURL(/\/admin/);
    
    // Vérifier l'accès au module Finance
    await page.click('text=Finance');
    await expect(page).toHaveURL(/\/finance/);
  });

  test('MAGASINIER should only access Magasin module', async ({ page }) => {
    // Login as magasinier
    await page.goto('/login');
    await page.fill('input[type="email"]', 'magasinier@kamlog.cm');
    await page.fill('input[type="password"]', 'password123');
    await page.click('button[type="submit"]');
    
    // Devrait être redirigé vers le dashboard
    await expect(page).toHaveURL(/\/dashboard/);
    
    // Le menu Admin ne devrait pas être visible
    await expect(page.locator('text=Administration ERP')).not.toBeVisible();
  });

  test('CLIENT should only access B2B Portal', async ({ page }) => {
    await page.goto('/login');
    await page.fill('input[type="email"]', 'client@kamlog.cm');
    await page.fill('input[type="password"]', 'password123');
    await page.click('button[type="submit"]');
    
    // Devrait être redirigé vers le portail client
    await expect(page).toHaveURL('/client-portal');
    
    // Les modules admin ne doivent pas être accessibles
    await expect(page.locator('text=Admin')).not.toBeVisible();
  });
});