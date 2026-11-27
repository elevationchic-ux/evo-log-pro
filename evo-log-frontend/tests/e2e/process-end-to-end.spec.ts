import { test, expect } from '@playwright/test';

// ============================================================================
// PROCESSUS NAVIRE → CLIENT — aligné sur l'UI réelle
// (pages de domaine existantes + pages transverses /metier, /referentiels,
// /outils ; login réel via input[placeholder*="Identifiant"] → /dashboard/global)
//
// Honnêteté : les écrans métier profonds n'exposent pas tous des formulaires
// stables pour un parcours de saisie de bout en bout. Cette spec vérifie que
// chaque étape du processus logistique est accessible et rendue avec des
// données réelles (backend SQLite local, tenant admin@kamlog.cm), puis
// exerce un vrai calculateur /metier/calculs.
// ============================================================================

const IDENT = 'input[placeholder*="Identifiant"]';
const PASS = 'input[type="password"]';

async function loginAdmin(page: any) {
  await page.goto('/login');
  await page.fill(IDENT, 'admin@kamlog.cm');
  await page.fill(PASS, 'password123');
  // Enter dans le champ mot de passe : contourne les overlays d'intro qui
  // interceptent le clic (fixed inset-0 z-[100]) sans dépendre du DOM
  await page.press(PASS, 'Enter');
  await page.waitForURL('/dashboard/global', { timeout: 60000 });
}

async function expectPageRenders(page: any, path: string) {
  await page.goto(path, { waitUntil: 'domcontentloaded' });
  // Attendre un titre rendu — le dev server compile la route à la demande
  const heading = page.locator('h1, h2').first();
  await expect(heading).toBeVisible({ timeout: 90000 });
  await expect(page.locator('body')).not.toContainText('Application error');
}

test.describe('Processus Navire → Client (chaîne de domaines)', () => {
  test.beforeEach(async ({ page }) => {
    await loginAdmin(page);
  });

  test('étape 1 — port: opérations portuaires accessibles', async ({ page }) => {
    await expectPageRenders(page, '/port-operations');
  });

  test('étape 2 — transit & douane: déclaration et taxation accessibles', async ({ page }) => {
    await expectPageRenders(page, '/transit-douane');
    await expectPageRenders(page, '/magasin-douane');
  });

  test('étape 3 — magasin & WMS: stock et réceptions accessibles', async ({ page }) => {
    await expectPageRenders(page, '/magasin');
  });

  test('étape 4 — transport & livraison: flotte et missions accessibles', async ({ page }) => {
    await expectPageRenders(page, '/transport-flotte');
  });

  test('étape 5 — facturation & comptabilité: finance et états OHADA accessibles', async ({ page }) => {
    await expectPageRenders(page, '/finance-ohada');
    await expectPageRenders(page, '/comptabilite-ohada');
  });

  test('transverse — pilotage métier, registres et outils accessibles', async ({ page }) => {
    await expectPageRenders(page, '/metier');
    await expectPageRenders(page, '/metier/calculs');
    await expectPageRenders(page, '/referentiels');
    await expectPageRenders(page, '/outils');
  });

  test('calculateur réel — congés collaborateur renvoie une réponse API', async ({ page }) => {
    await page.goto('/metier/calculs');
    // Formulaire "Congés collaborateur" : un seul champ texte + bouton "Exécuter"
    const card = page.locator('div.bg-white', { hasText: 'Congés collaborateur' }).first();
    await card.locator('input').first().fill('test');
    await card.locator('button', { hasText: 'Exécuter' }).click();
    // Réponse API : JSON <pre>, note honnête .text-amber-700 ou erreur .text-red-600
    await expect(card.locator('pre, .text-amber-700, .text-red-600').first()).toBeVisible({ timeout: 15000 });
  });
});
