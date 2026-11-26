# GUIDE INTEGRATION MENU SIDEBAR

## 📋 Instructions pour intégrer le menu-config dans ModuleSidebar.tsx

### Étape 1: Importer la configuration

Ajoutez en haut du fichier `src/components/layout/ModuleSidebar.tsx`:

```typescript
import { MENU_ITEMS, MENU_CATEGORIES } from '@/lib/menu-config'
```

### Étape 2: Fusionner avec les items existants

Dans votre configuration de menu existante, ajoutez les items Cameroun/CEMAC:

```typescript
const menuItems = [
  // ... vos items existants ...
  
  // Ajouter ces items
  ...MENU_ITEMS,
]
```

### Étape 3: Ajouter la catégorie Cameroun

Dans votre configuration de catégories, ajoutez:

```typescript
const categories = [
  // ... vos catégories existantes ...
  
  // Ajouter cette catégorie
  ...MENU_CATEGORIES,
]
```

### Étape 4: Adapter selon votre structure

Si votre sidebar utilise une structure différente, adaptez les entrées MENU_ITEMS de `menu-config.ts` pour correspondre à votre format.

---

## 🎯 Alternative: Ajout direct dans le fichier

Si vous préférez modifier directement le fichier sans utiliser menu-config.ts, ajoutez ces entrées directement dans votre configuration de menu:

```typescript
{
  name: "Intégration Cameroun",
  path: "/integration-cameroun",
  icon: "🇨🇲",
  color: "#FF6B6B"
},
{
  name: "Paiements Locaux",
  path: "/paiement-local",
  icon: "💳",
  color: "#4ECDC4"
},
{
  name: "Fiscalité Cameroun",
  path: "/fiscalite-cameroun",
  icon: "📊",
  color: "#96CEB4"
}
```

---

## ✅ Vérification

Après l'intégration:
1. Redémarrez le serveur frontend
2. Vérifiez que les 3 nouvelles pages apparaissent dans le menu
3. Testez la navigation vers chaque page
4. Vérifiez que les icônes et couleurs s'affichent correctement
