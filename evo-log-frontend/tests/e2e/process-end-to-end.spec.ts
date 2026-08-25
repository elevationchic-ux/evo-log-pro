import { test, expect } from '@playwright/test';

// ============================================================================
// TESTS DU PROCESSUS END-TO-END: NAVIRE → CLIENT
// ============================================================================

/**
 * Ce test couvre le processus complet:
 * 1. Arrivée navire & opérations portuaires
 * 2. Dédouanement & transit
 * 3. Magasinage & WMS
 * 4. Transport & livraison
 * 5. Facturation & paiement
 */

test.describe('Processus End-to-End: Navire → Client', () => {
  // Setup: Login avant chaque test
  test.beforeEach(async ({ page }) => {
    await page.goto('/login');
    await page.fill('input[type="email"]', 'admin@kamlog.cm');
    await page.fill('input[type="password"]', 'password123');
    await page.click('button[type="submit"]');
    await page.waitForURL('/dashboard/global', { timeout: 10000 });
  });

  // ============================================================================
  // ÉTAPE 1: OPÉRATIONS PORTUAIRES
  // ============================================================================
  test.describe('Étape 1: Opérations Portuaires', () => {
    test('devrait créer un nouveau manifeste', async ({ page }) => {
      // Naviguer vers Opérations Portuaires
      await page.click('text=Opérations Portuaires');
      await expect(page).toHaveURL(/\/port-operations/);
      
      // Créer un nouveau manifeste
      await page.click('text=Nouveau Manifeste');
      
      // Remplir le formulaire
      await page.fill('input[name="shipName"]', 'MSC LORENA');
      await page.fill('input[name="voyageNumber"]', 'VOY-2024-0847');
      await page.fill('input[name="containerCount"]', '150');
      await page.selectOption('select[name="berth"]', 'Poste 4');
      
      // Soumettre
      await page.click('button:has-text("Créer le manifeste")');
      
      // Vérifier le succès
      await expect(page.locator('text=Manifeste créé avec succès')).toBeVisible();
    });

    test('devrait planifier un accostage', async ({ page }) => {
      await page.click('text=Opérations Portuaires');
      await page.click('text=Planning Accostage');
      
      await page.click('text=Nouveau Poste');
      await page.fill('input[name="berthNumber"]', '5');
      await page.fill('input[name="scheduledDate"]', '2024-08-25');
      await page.fill('input[name="scheduledTime"]', '08:00');
      
      await page.click('button:has-text("Planifier")');
      await expect(page.locator('text=Poste planifié')).toBeVisible();
    });
  });

  // ============================================================================
  // ÉTAPE 2: TRANSIT & DOUANE
  // ============================================================================
  test.describe('Étape 2: Transit & Douane', () => {
    test('devrait créer une déclaration en douane', async ({ page }) => {
      await page.click('text=Transit & Douane');
      await expect(page).toHaveURL(/\/transit/);
      
      await page.click('text=Nouvelle DUM');
      
      // Remplir la déclaration
      await page.fill('input[name="importer"]', 'SABC SARL');
      await page.fill('input[name="containerNumber"]', 'TEMU1234567');
      await page.fill('input[name="goodsDescription"]', 'Marchandises diverses');
      await page.fill('input[name="fobValue"]', '15000000');
      await page.selectOption('select[name="regime"]', 'IMPORT_DEFINITIVE');
      
      await page.click('button:has-text("Soumettre")');
      await expect(page.locator('text=DUM créée avec succès')).toBeVisible();
    });

    test('devrait calculer les droits de douane', async ({ page }) => {
      await page.click('text=Transit & Douane');
      await page.click('text=Taxation Cameroun');
      
      // Saisir les informations
      await page.fill('input[name="fobAmount"]', '10000000');
      await page.selectOption('select[name="originCountry"]', 'CN');
      await page.selectOption('select[name="productCategory"]', 'A');
      
      await page.click('button:has-text("Calculer")');
      
      // Vérifier le calcul
      await expect(page.locator('text=Droit de Douane')).toBeVisible();
      await expect(page.locator('text=TVA')).toBeVisible();
      await expect(page.locator('text=TEC')).toBeVisible();
    });

    test('devrait émettre un BAE', async ({ page }) => {
      await page.click('text=Transit & Douane');
      await page.click('text=Émettre BAE');
      
      await page.fill('input[name="dumNumber"]', 'DUM-CM-2024-08456');
      await page.click('button:has-text("Générer BAE")');
      
      await expect(page.locator('text=BAE émis avec succès')).toBeVisible();
    });
  });

  // ============================================================================
  // ÉTAPE 3: MAGASIN & WMS
  // ============================================================================
  test.describe('Étape 3: Magasin & WMS', () => {
    test('devrait réceptionner des marchandises', async ({ page }) => {
      await page.click('text=Magasin & Stock WMS');
      await expect(page).toHaveURL(/\/magasin/);
      
      await page.click('text=Nouvelle Réception');
      
      // Remplir les détails
      await page.fill('input[name="receptionNumber"]', 'REC-2024-0847');
      await page.fill('input[name="supplier"]', 'Globex Cameroon');
      await page.fill('input[name="articleCount"]', '150');
      
      await page.click('button:has-text("Enregistrer")');
      await expect(page.locator('text=Réception créée')).toBeVisible();
    });

    test('devrait effectuer un inventaire', async ({ page }) => {
      await page.click('text=Magasin & Stock WMS');
      await page.click('text=Inventaire');
      
      await page.selectOption('select[name="location"]', 'Zone A');
      await page.click('button:has-text("Démarrer inventaire")');
      
      // Saisir les quantités
      await page.fill('input[name="qty-ART-001"]', '145');
      await page.fill('input[name="qty-ART-002"]', '78');
      
      await page.click('button:has-text("Valider")');
      await expect(page.locator('text=Inventaire validé')).toBeVisible();
    });

    test('devrait créer un transfert de stock', async ({ page }) => {
      await page.click('text=Magasin & Stock WMS');
      await page.click('text=Transferts');
      
      await page.click('text=Nouveau Transfert');
      await page.fill('input[name="fromZone"]', 'Zone A');
      await page.fill('input[name="toZone"]', 'Zone B');
      await page.fill('input[name="articleId"]', 'ART-001');
      await page.fill('input[name="quantity"]', '50');
      
      await page.click('button:has-text("Exécuter")');
      await expect(page.locator('text=Transfert effectué')).toBeVisible();
    });
  });

  // ============================================================================
  // ÉTAPE 4: TRANSPORT & LIVRAISON
  // ============================================================================
  test.describe('Étape 4: Transport & Livraison', () => {
    test('devrait créer une mission de transport', async ({ page }) => {
      await page.click('text=Transport & Flotte');
      await expect(page).toHaveURL(/\/transport/);
      
      await page.click('text=Nouvelle Mission');
      
      // Remplir les détails
      await page.fill('input[name="client"]', 'SABC');
      await page.fill('input[name="origin"]', 'Port Douala');
      await page.fill('input[name="destination"]', 'Yaoundé');
      await page.selectOption('select[name="vehicle"]', 'CMR-T-4521');
      await page.selectOption('select[name="driver"]', 'M. Kamdem');
      
      await page.click('button:has-text("Créer la mission")');
      await expect(page.locator('text=Mission créée')).toBeVisible();
    });

    test('devrait suivre une livraison en temps réel', async ({ page }) => {
      await page.click('text=Transport & Flotte');
      await page.click('text=Tracking Live');
      
      // Vérifier la carte GPS
      await expect(page.locator('text=Carte GPS Live')).toBeVisible();
      
      // Sélectionner un véhicule
      await page.click('text=CMR-T-4521');
      
      // Vérifier les informations de suivi
      await expect(page.locator('text=Position actuelle')).toBeVisible();
      await expect(page.locator('text=Vitesse')).toBeVisible();
    });

    test('devrait collecter un e-POD', async ({ page }) => {
      await page.click('text=Transport & Flotte');
      await page.click('text=e-POD');
      
      // Rechercher une mission livrée
      await page.fill('input[name="missionSearch"]', 'TR-2024-0847');
      await page.click('button:has-text("Rechercher")');
      
      // Collecter le POD
      await page.click('button:has-text("Signer")');
      
      // Simuler une signature (upload ou dessin)
      await page.click('button:has-text("Confirmer")');
      await expect(page.locator('text=e-POD collecté')).toBeVisible();
    });
  });

  // ============================================================================
  // ÉTAPE 5: FACTURATION & PAIEMENT
  // ============================================================================
  test.describe('Étape 5: Facturation & Paiement', () => {
    test('devrait créer une facture', async ({ page }) => {
      await page.click('text=Finance OHADA');
      await expect(page).toHaveURL(/\/finance/);
      
      await page.click('text=Nouvelle Facture');
      
      // Remplir la facture
      await page.fill('input[name="client"]', 'SABC');
      await page.fill('input[name="service"]', 'Transport maritime');
      await page.fill('input[name="amount"]', '2500000');
      await page.fill('input[name="dueDate"]', '2024-09-15');
      
      await page.click('button:has-text("Générer")');
      await expect(page.locator('text=Facture créée')).toBeVisible();
    });

    test('devrait enregistrer un paiement', async ({ page }) => {
      await page.click('text=Finance OHADA');
      await page.click('text=Encaissements');
      
      await page.click('text=Enregistrer Paiement');
      await page.fill('input[name="invoiceNumber"]', 'FAC-2024-08456');
      await page.fill('input[name="amount"]', '2500000');
      await page.selectOption('select[name="method"]', 'MOBILE_MONEY');
      await page.fill('input[name="reference']", 'OM-20240824-001');
      
      await page.click('button:has-text("Enregistrer")');
      await expect(page.locator('text=Paiement enregistré')).toBeVisible();
    });

    test('devrait générer un état financier OHADA', async ({ page }) => {
      await page.click('text=Comptabilité OHADA');
      await page.click('text=États Financiers');
      
      await page.selectOption('select[name="period"]', '2024-08');
      await page.selectOption('select[name="reportType"]', 'BILAN');
      
      await page.click('button:has-text("Générer")');
      
      // Vérifier le téléchargement ou l'affichage
      await expect(page.locator('text=Bilan généré')).toBeVisible();
    });
  });
});

// ============================================================================
// TESTS DES PARCOURS UTILISATEURS SPÉCIFIQUES
// ============================================================================

test.describe('Parcours Utilisateurs', () => {
  test('parcours chauffeur: login → mission → POD → logout', async ({ page }) => {
    // Login chauffeur
    await page.goto('/login');
    await page.fill('input[type="email"]', 'chauffeur@kamlog.cm');
    await page.fill('input[type="password"]', 'password123');
    await page.click('button[type="submit"]');
    
    // Voir ses missions
    await expect(page).toHaveURL(/\/transport/);
    await expect(page.locator('text=Mes Missions')).toBeVisible();
    
    // Accepter une mission
    await page.click('button:has-text("Accepter")');
    await expect(page.locator('text=Mission acceptée')).toBeVisible();
    
    // Terminer avec POD
    await page.click('text=Livrer');
    await page.click('button:has-text("Signer")');
    await expect(page.locator('text=Livraison confirmée')).toBeVisible();
    
    // Logout
    await page.click('button[aria-haspopup="menu"]');
    await page.click('text=Déconnexion');
    await expect(page).toHaveURL('/login');
  });

  test('parcours client B2B: login → suivi → factures', async ({ page }) => {
    // Login client
    await page.goto('/login');
    await page.fill('input[type="email"]', 'client@kamlog.cm');
    await page.fill('input[type="password"]', 'password123');
    await page.click('button[type="submit"]');
    
    // Voir ses expéditions
    await expect(page).toHaveURL('/client-portal');
    await expect(page.locator('text=Mes Expéditions')).toBeVisible();
    
    // Suivre une expédition
    await page.fill('input[name="trackingNumber"]', 'TR-2024-0847');
    await page.click('button:has-text("Suivre")');
    await expect(page.locator('text=Statut: Livré')).toBeVisible();
    
    // Voir ses factures
    await page.click('text=Mes Factures');
    await expect(page.locator('text=Historique')).toBeVisible();
  });
});