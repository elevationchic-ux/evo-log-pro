ement":
        case "ForOfStatement":
            state.pushLoopContext(node.type, getLabel(node));
            break;

        case "LabeledStatement":
            if (!breakableTypePattern.test(node.body.type)) {
                state.pushBreakContext(false, node.label.name);
            }
            break;

        default:
            break;
    }

    // Emits onCodePathSegmentStart events if updated.
    forwardCurrentToHead(analyzer, node);
    debug.dumpState(node, state, false);
}

/**
 * Updates the code path due to the type of a given node in leaving.
 * @param {CodePathAnalyzer} analyzer The instance.
 * @param {ASTNode} node The current AST node.
 * @returns {void}
 */
function processCodePathToExit(analyzer, node) {

    const codePath = analyzer.codePath;
    const state = CodePath.getState(codePath);
    let dontForward = false;

    switch (node.type) {
        case "ChainExpression":
            state.popChainContext();
            break;

        case "IfStatement":
        case "ConditionalExpression":
            state.popChoiceContext();
            break;

        case "LogicalExpression":
            if (isHandledLogicalOperator(node.operator)) {
                state.popChoiceContext();
            }
            break;

        case "AssignmentExpression":
            if (isLogicalAssignmentOperator(node.operator)) {
                state.popChoiceContext();
            }
            break;

        case "SwitchStatement":
            state.popSwitchContext();
            break;

        case "SwitchCase":

            /*
             * This is the same as the process at the 1st `consequent` node in
             * `preprocess` function.
             * Must do if this `consequent` is empty.
             */
            if (node.consequent.length === 0) {
                state.makeSwitchCaseBody(true, !node.test);
            }
            if (state.forkContext.reachable) {
                dontForward = true;
            }
            break;

        case "TryStatement":
            state.popTryContext();
            break;

        case "BreakStatement":
            forwardCurrentToHead(analyzer, node);
            state.makeBreak(node.label && node.label.name);
            dontForward = true;
            break;

        case "ContinueStatement":
            forwardCurrentToHead(analyzer, node);
            state.makeContinue(node.label && node.label.name);
            dontForward = true;
            break;

        case "ReturnStatement":
            forwardCurrentToHead(analyzer, node);
            state.makeReturn();
            dontForward = true;
            break;

        case "ThrowStatement":
            forwardCurrentToHead(analyzer, node);
            state.makeThrow();
            dontForward = true;
            break;

        case "Identifier":
            if (isIdentifierReference(node)) {
                state.makeFirstThrowablePathInTryBlock();
                dontForward = true;
            }
            break;

        case "CallExpression":
        case "ImportExpression":
        case "MemberExpression":
        case "NewExpression":
        case "YieldExpression":
            state.makeFirstThrowablePathInTryBlock();
            break;

        case "WhileStatement":
        case "DoWhileStatement":
        case "ForStatement":
        case "ForInStatement":
        case "ForOfStatement":
            state.popLoopContext();
            break;

        case "AssignmentPattern":
            state.popForkContext();
            break;

        case "LabeledStatement":
            if (!breakableTypePattern.test(node.body.type)) {
                state.popBreakContext();
            }
            break;

        default:
            break;
    }

    // Emits onCodePathSegmentStart events if updated.
    if (!dontForward) {
        forwardCurrentToHead(analyzer, node);
    }
    debug.dumpState(node, state, true);
}

/**
 * Updates the code path to finalize the current code path.
 * @param {CodePathAnalyzer} analyzer The instance.
 * @param {ASTNode} node The current AST node.
 * @returns {void}
 */
function postprocess(analyzer, node) {

    /**
     * Ends the code path for the current node.
     * @returns {void}
     */
    function endCodePath() {
        let codePath = analyzer.codePath;

        // Mark the current path as the final node.
        CodePath.getState(codePath).makeFinal();

        // Emits onCodePathSegmentEnd event of the current segments.
        leaveFromCurrentSegment(analyzer, node);

        // Emits onCodePathEnd event of this code path.
        debug.dump(`onCodePathEnd ${codePath.id}`);
        analyzer.emitter.emit("onCodePathEnd", codePath, node);
        debug.dumpDot(codePath);

        codePath = analyzer.codePath = analyzer.codePath.upper;
        if (codePath) {
            debug.dumpState(node, CodePath.getState(codePath), true);
        }

    }

    switch (node.type) {
        case "Program":
        case "FunctionDeclaration":
        case "FunctionExpression":
        case "ArrowFunctionExpression":
        case "StaticBlock": {
            endCodePath();
            break;
        }

        // The `arguments.length >= 1` case is in `preprocess` function.
        case "CallExpression":
            if (node.optional === true && node.arguments.length === 0) {
                CodePath.getState(analyzer.codePath).makeOptionalRight();
            }
            break;

        default:
            break;
    }

    /*
     * Special case: The right side of class field initializer is considered
     * to be its own function, so we need to end a code path in this
     * case.
     *
     * We need to check after the other checks in order to close the
     * code paths in the correct order for code like this:
     *
     *
     * class Foo {
     *     a = () => {}
     * }
     *
     * In this case, The ArrowFunctionExpression code path is closed first
     * and then we need to close the code path for the PropertyDefinition
     * value.
     */
    if (isPropertyDefinitionValue(node)) {
        endCodePath();
    }
}

//------------------------------------------------------------------------------
// Public Interface
//------------------------------------------------------------------------------

/**
 * The class to analyze code paths.
 * This class implements the EventGenerator interface.
 */
class CodePathAnalyzer {

    /**
     * @param {EventGenerator} eventGenerator An event generator to wrap.
     */
    constructor(eventGenerator) {
        this.original = eventGenerator;
        this.emitter = eventGenerator.emitter;
        this.codePath = null;
        this.idGenerator = new IdGenerator("s");
        this.currentNode = null;
        this.onLooped = this.onLooped.bind(this);
    }

    /**
     * Does the process to enter a given AST node.
     * This updates state of analysis and calls `enterNode` of the wrapped.
     * @param {ASTNode} node A node which is entering.
     * @returns {void}
     */
    enterNode(node) {
        this.currentNode = node;

        // Updates the code path due to node's position in its parent node.
        if (node.parent) {
            preprocess(this, node);
        }

        /*
         * Updates the code path.
         * And emits onCodePathStart/onCodePathSegmentStart events.
         */
        processCodePathToEnter(this, node);

        // Emits node events.
        this.original.enterNode(node);

        this.currentNode = null;
    }

    /**
     * Does the process to leave a given AST node.
     * This updates state of analysis and calls `leaveNode` of the wrapped.
     * @param {ASTNode} node A node which is leaving.
     * @returns {void}
     */
    leaveNode(node) {
        this.currentNode = node;

        /*
         * Updates the code path.
         * And emits onCodePathStart/onCodePathSegmentStart events.
         */
        processCodePathToExit(this, node);

        // Emits node events.
        this.original.leaveNode(node);

        // Emits the last onCodePathStart/onCodePathSegmentStart events.
        postprocess(this, node);

        this.currentNode = null;
    }

    /**
     * This is called on a code path looped.
     * Then this raises a looped event.
     * @param {CodePathSegment} fromSegment A segment of prev.
     * @param {CodePathSegment} toSegment A segment of next.
     * @returns {void}
     */
    onLooped(fromSegment, toSegment) {
        if (fromSegment.reachable && toSegment.reachable) {
            debug.dump(`onCodePathSegmentLoop ${fromSegment.id} -> ${toSegment.id}`);
            this.emitter.emit(
                "onCodePathSegmentLoop",
                fromSegment,
                toSegment,
                this.currentNode
            );
        }
    }
}

module.exports = CodePathAnalyzer;
tance** - Per km pricing
- **Tarification par temps** - Per hour pricing
- **Suppléments** - Night, weekend, urgent
- **Frais annexes** - Toll, parking, fuel
- **Facturation automatique** - Auto-invoicing

### 🔧 AMÉLIORATIONS NÉCESSAIRES

#### Haute Priorité
1. **Types de véhicules** spécialisés (bennes, citernes, frigo)
2. **Gestion des chauffeurs** complète (compétences, planning)
3. **Route optimization** avec multi-pickup/delivery
4. **Maintenance préventive** et corrective
5. **Carburant management** avec fraud detection

#### Moyenne Priorité
1. **Safety checks** et compliance réglementaire
2. **GPS tracking** avec géofencing
3. **Facturation automatique** avec suppléments
4. **Proof of delivery** électronique

#### Basse Priorité
1. **AI-based assignment** des missions
2. **Predictive maintenance** avec IoT
3. **Electric vehicles** management

---

## 💰 MODULE 5: FINANCE (Gestion Financière)

### ✅ Fonctionnalités Actuelles
- Gestion financière
- Facturation
- Encaissements

### ❌ LACUNES CRITIQUES IDENTIFIÉES

#### 1. Comptabilité OHADA
- **Plan comptable SYSCOHADA** - Complètement implémenté
- **Journalisation automatique** - Auto-journal entries
- **Balance et reporting** - Balance sheet, P&L
- **Audit trail** - Complete audit trail
- **Multi-devises** - Currency conversion

#### 2. Gestion des Clients (Accounts Receivable)
- **Credit limits** - Limites de crédit par client
- **Aging analysis** - Analyse des créances par âge
- **Collection management** - Processus de recouvrement
- **Provisions** - Provisions pour créances douteuses
- **Statements** - Relevés de compte mensuels

#### 3. Gestion des Fournisseurs (Accounts Payable)
- **Approval workflow** - Validation des factures
- **Payment terms** - Conditions de paiement
- **Cash flow planning** - Planification des décaissements
- **Vendor analysis** - Performance des fournisseurs
- **Proforma invoices** - Factures proforma

#### 4. Budgeting et Forecasting
- **Budget par département** - Departmental budgets
- **Budget par projet** - Project budgets
- **Variance analysis** - Analyse des écarts
- **Forecasting** - Prévisions financières
- **Rolling forecasts** - Prévisions glissantes

#### 5. Treasury Management
- **Cash management** - Gestion de la trésorerie
- **Bank accounts** - Gestion des comptes bancaires
- **Investments** - Gestion des placements
- **Loans and credit** - Gestion des emprunts
- **Forex management** - Gestion des changes

#### 6. Reporting Financier
- **Financial statements** - Bilan, compte de résultat
- **Management reports** - Rapports de gestion
- **KPIs financiers** - Indicateurs de performance
- **Comparaison periodique** - Mois vs mois, année vs année
- **Drill-down** - Analyse détaillée

#### 7. Audit et Compliance
- **Audit trail** - Traçabilité complète
- **Segregation of duties** - Séparation des tâches
- **Internal controls** - Contrôles internes
- **Compliance OHADA** - Conformité réglementaire
- **External audit** - Préparation audit externe

### 🔧 AMÉLIORATIONS NÉCESSAIRES

#### Haute Priorité
1. **Comptabilité OHADA** complète avec journalisation automatique
2. **Accounts receivable** avec aging et collection
3. **Accounts payable** avec approval workflow
4. **Budgeting et forecasting** complet
5. **Treasury management** intégré

#### Moyenne Priorité
1. **Reporting financier** avancé
2. **Audit et compliance** OHADA
3. **Multi-devises** complet
4. **KPIs financiers** automatiques

#### Basse Priorité
1. **AI-based forecasting** des revenus
2. **Blockchain** pour les transactions
3. **Real-time cash flow** avec prédictions

---

## 🏪 MODULE 6: MAGASIN (WMS)

### ✅ Fonctionnalités Actuelles
- Gestion des stocks
- Mouvements de stock
- Inventaires

### ❌ LACUNES CRITIQUES IDENTIFIÉES

#### 1. Advanced Inventory Management
- **ABC analysis** - Classification des articles
- **Economic Order Quantity (EOQ)** - Calcul des quantités optimales
- **Safety stock** - Calcul du stock de sécurité
- **Reorder point** - Point de réapprovisionnement
- **Demand forecasting** - Prévision de la demande

#### 2. Lot et Serial Tracking
- **Lot tracking** - Suivi par lot
- **Serial tracking** - Suivi par numéro de série
- **Expiration tracking** - Suivi des dates d'expiration
- **Quarantine** - Quarantaine des lots
- **Recall management** - Gestion des rappels

#### 3. Kitting and Assembly
- **Kitting** - Création de kits
- **Assembly** - Assemblage de produits
- **Disassembly** - Désassemblage
- **Bill of materials (BOM)** - Nomenclature
- **Work orders** - Ordres de travail

#### 4. Warehouse Management
- **Zone management** - Gestion des zones
- **Put-away rules** - Règles de mise en stock
- **Picking strategies** - Stratégies de prélèvement
- **Packing optimization** - Optimisation de l'emballage
- **Slotting optimization** - Optimisation des emplacements

#### 5. Integration with Transport
- **Delivery planning** - Planning des livraisons
- **Route optimization** - Optimisation des tournées
- **Proof of delivery** - Preuve de livraison
- **Returns management** - Gestion des retours
- **Reverse logistics** - Logistique inverse

#### 6. Quality Control
- **Quality checks** - Contrôles qualité
- **Inspection plans** - Plans d'inspection
- **Non-conformities** - Gestion des non-conformités
- **Quarantine** - Quarantaine des produits
- **Corrective actions** - Actions correctives

#### 7. Performance Monitoring
- **KPIs warehouse** - Indicateurs de performance
- **Productivity tracking** - Suivi de la productivité
- **Accuracy measurement** - Mesure de la précision
- **Throughput analysis** - Analyse du throughput
- **Benchmarking** - Comparaison avec les standards

### 🔧 AMÉLIORATIONS NÉCESSAIRES

#### Haute Priorité
1. **Lot et serial tracking** complet
2. **Expiration tracking** avec alertes
3. **Kitting et assembly** avec BOM
4. **Zone management** et put-away rules
5. **Quality control** avec inspection plans

#### Moyenne Priorité
1. **ABC analysis** et EOQ
2. **Picking strategies** avancées
3. **Integration transport** complète
4. **KPIs warehouse** automatiques

#### Basse Priorité
1. **AI-based forecasting** de la demande
2. **Robotics integration** pour picking
3. **Voice picking** système

---

*Suite de l'analyse à suivre pour les modules restants...*