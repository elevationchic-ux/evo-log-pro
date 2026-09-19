'use client';

import React, { useState, useEffect, useMemo } from 'react';
import { GLOSSARY } from './TermDefinition';

interface HelpAndShortcutsModalProps {
  isOpen: boolean;
  onClose: () => void;
  defaultTab?: 'shortcuts' | 'glossary' | 'guide';
}

export function HelpAndShortcutsModal({
  isOpen,
  onClose,
  defaultTab = 'shortcuts',
}: HelpAndShortcutsModalProps) {
  const [activeTab, setActiveTab] = useState<'shortcuts' | 'glossary' | 'guide'>(defaultTab);
  const [glossarySearch, setGlossarySearch] = useState('');

  useEffect(() => {
    setActiveTab(defaultTab);
  }, [defaultTab]);

  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === 'Escape') {
        onClose();
      }
    };
    if (isOpen) {
      document.addEventListener('keydown', handleKeyDown);
    }
    return () => document.removeEventListener('keydown', handleKeyDown);
  }, [isOpen, onClose]);

  const filteredGlossary = useMemo(() => {
    const query = glossarySearch.toLowerCase().trim();
    if (!query) return Object.entries(GLOSSARY);
    return Object.entries(GLOSSARY).filter(([key, val]) => {
      return (
        key.toLowerCase().includes(query) ||
        val.title.toLowerCase().includes(query) ||
        (val.fullForm && val.fullForm.toLowerCase().includes(query)) ||
        val.definition.toLowerCase().includes(query) ||
        val.category.toLowerCase().includes(query)
      );
    });
  }, [glossarySearch]);

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-[100] flex items-center justify-center bg-black/50 backdrop-blur-sm p-4 animate-in fade-in duration-200">
      <div
        className="relative w-full max-w-3xl rounded-2xl bg-surface border border-outline shadow-2xl overflow-hidden flex flex-col max-h-[85vh] text-on-surface"
        onClick={(e) => e.stopPropagation()}
      >
        {/* Header */}
        <div className="flex items-center justify-between px-6 py-4 border-b border-outline bg-surface-container-low shrink-0">
          <div className="flex items-center gap-3">
            <div className="h-10 w-10 rounded-xl bg-primary/10 border border-primary/20 flex items-center justify-center text-primary">
              <span className="material-symbols-outlined text-[24px]">help_center</span>
            </div>
            <div>
              <h2 className="text-lg font-bold">Centre d'Aide & Productivité EVO-LOG</h2>
              <p className="text-xs text-on-surface-variant">Raccourcis clavier pro, glossaire des sigles et guide de navigation</p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="h-8 w-8 rounded-lg hover:bg-surface-container flex items-center justify-center text-on-surface-variant hover:text-on-surface transition-colors"
          >
            <span className="material-symbols-outlined text-[20px]">close</span>
          </button>
        </div>

        {/* Tabs */}
        <div className="flex items-center gap-2 px-6 pt-3 border-b border-outline bg-surface shrink-0">
          <button
            onClick={() => setActiveTab('shortcuts')}
            className={`flex items-center gap-2 px-4 py-2.5 text-xs font-bold border-b-2 transition-colors ${
              activeTab === 'shortcuts'
                ? 'border-primary text-primary'
                : 'border-transparent text-on-surface-variant hover:text-on-surface'
            }`}
          >
            <span className="material-symbols-outlined text-[18px]">keyboard</span>
            Raccourcis Clavier Pro
          </button>
          <button
            onClick={() => setActiveTab('glossary')}
            className={`flex items-center gap-2 px-4 py-2.5 text-xs font-bold border-b-2 transition-colors ${
              activeTab === 'glossary'
                ? 'border-primary text-primary'
                : 'border-transparent text-on-surface-variant hover:text-on-surface'
            }`}
          >
            <span className="material-symbols-outlined text-[18px]">menu_book</span>
            Glossaire des Sigles ({Object.keys(GLOSSARY).length})
          </button>
          <button
            onClick={() => setActiveTab('guide')}
            className={`flex items-center gap-2 px-4 py-2.5 text-xs font-bold border-b-2 transition-colors ${
              activeTab === 'guide'
                ? 'border-primary text-primary'
                : 'border-transparent text-on-surface-variant hover:text-on-surface'
            }`}
          >
            <span className="material-symbols-outlined text-[18px]">explore</span>
            Guide Débutant (3 Échelons)
          </button>
        </div>

        {/* Content Body */}
        <div className="p-6 overflow-y-auto flex-1">
          {/* TAB 1: SHORTCUTS */}
          {activeTab === 'shortcuts' && (
            <div className="space-y-6">
              <div>
                <h3 className="text-xs font-black uppercase tracking-wider text-primary mb-3">Navigation & T-Codes SAP-Like</h3>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-2.5">
                  <div className="flex items-center justify-between p-3 rounded-xl bg-surface-container-low border border-outline">
                    <span className="text-xs font-medium">Recherche Universelle & T-Codes</span>
                    <kbd className="px-2 py-1 rounded bg-surface-container border border-outline text-[11px] font-mono font-bold text-primary shadow-sm">
                      Ctrl + K
                    </kbd>
                  </div>
                  <div className="flex items-center justify-between p-3 rounded-xl bg-surface-container-low border border-outline">
                    <span className="text-xs font-medium">Ouvrir ce Centre d'Aide</span>
                    <kbd className="px-2 py-1 rounded bg-surface-container border border-outline text-[11px] font-mono font-bold text-primary shadow-sm">
                      ? ou F1
                    </kbd>
                  </div>
                  <div className="flex items-center justify-between p-3 rounded-xl bg-surface-container-low border border-outline">
                    <span className="text-xs font-medium">Fermer Tiroir / Modale Active</span>
                    <kbd className="px-2 py-1 rounded bg-surface-container border border-outline text-[11px] font-mono font-bold text-primary shadow-sm">
                      Échap (Esc)
                    </kbd>
                  </div>
                  <div className="flex items-center justify-between p-3 rounded-xl bg-surface-container-low border border-outline">
                    <span className="text-xs font-medium">Focus Recherche dans le Tableau</span>
                    <kbd className="px-2 py-1 rounded bg-surface-container border border-outline text-[11px] font-mono font-bold text-primary shadow-sm">
                      /
                    </kbd>
                  </div>
                </div>
              </div>

              <div>
                <h3 className="text-xs font-black uppercase tracking-wider text-primary mb-3">Accès Directs Portails Collaborateurs</h3>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-2.5">
                  <div className="flex items-center justify-between p-3 rounded-xl bg-surface-container-low border border-outline">
                    <span className="text-xs font-medium">Portail Chauffeur & Tournées</span>
                    <span className="text-[11px] font-mono font-bold px-2 py-1 bg-surface-container border border-outline rounded text-primary">T-Code: KDRV_TRN</span>
                  </div>
                  <div className="flex items-center justify-between p-3 rounded-xl bg-surface-container-low border border-outline">
                    <span className="text-xs font-medium">Portail Magasinier Picking WMS</span>
                    <span className="text-[11px] font-mono font-bold px-2 py-1 bg-surface-container border border-outline rounded text-primary">T-Code: KWMS_OP</span>
                  </div>
                  <div className="flex items-center justify-between p-3 rounded-xl bg-surface-container-low border border-outline">
                    <span className="text-xs font-medium">Portail Notes de Frais & Avances</span>
                    <span className="text-[11px] font-mono font-bold px-2 py-1 bg-surface-container border border-outline rounded text-primary">T-Code: KEXP_FEE</span>
                  </div>
                  <div className="flex items-center justify-between p-3 rounded-xl bg-surface-container-low border border-outline">
                    <span className="text-xs font-medium">Grand Livre Comptable OHADA</span>
                    <span className="text-[11px] font-mono font-bold px-2 py-1 bg-surface-container border border-outline rounded text-primary">T-Code: KOHA_GL</span>
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* TAB 2: GLOSSARY */}
          {activeTab === 'glossary' && (
            <div className="space-y-4">
              <div className="relative">
                <span className="material-symbols-outlined absolute left-3 top-1/2 -translate-y-1/2 text-on-surface-variant text-[20px]">
                  search
                </span>
                <input
                  type="text"
                  placeholder="Rechercher un sigle (ex: DUM, BAE, FEFO, OHADA, BAPLIE)..."
                  value={glossarySearch}
                  onChange={(e) => setGlossarySearch(e.target.value)}
                  className="w-full pl-10 pr-4 py-2 text-xs rounded-xl bg-surface-container-low border border-outline focus:outline-none focus:ring-2 focus:ring-primary text-on-surface"
                />
              </div>

              <div className="space-y-3">
                {filteredGlossary.map(([key, item]) => (
                  <div key={key} className="p-3.5 rounded-xl bg-surface-container-low border border-outline hover:border-primary/40 transition-colors">
                    <div className="flex items-center justify-between gap-2 mb-1">
                      <div className="flex items-center gap-2">
                        <span className="font-black text-sm text-primary">{item.title}</span>
                        {item.fullForm && (
                          <span className="text-xs font-medium text-on-surface-variant">({item.fullForm})</span>
                        )}
                      </div>
                      <span className="text-[10px] font-bold px-2 py-0.5 rounded border border-outline bg-surface text-on-surface-variant uppercase">
                        {item.category}
                      </span>
                    </div>
                    <p className="text-xs text-on-surface-variant leading-relaxed">
                      {item.definition}
                    </p>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* TAB 3: NOVICE GUIDE */}
          {activeTab === 'guide' && (
            <div className="space-y-4">
              <div className="p-4 rounded-xl bg-primary/5 border border-primary/20">
                <h4 className="font-bold text-sm text-primary mb-1">Règle d'or N°1 : Vous êtes sur un écran d'exploitation</h4>
                <p className="text-xs text-on-surface-variant leading-relaxed">
                  Tous les chiffres que vous voyez sont des données réelles de la base de données. Il n'y a aucun chiffre factice. Vos créations sont immédiatement enregistrées.
                </p>
              </div>

              <div className="p-4 rounded-xl bg-blue-500/5 border border-blue-500/20">
                <h4 className="font-bold text-sm text-blue-500 mb-1">Règle d'or N°2 : Ne cherchez plus dans 50 menus</h4>
                <p className="text-xs text-on-surface-variant leading-relaxed">
                  Si vous êtes conducteur, magasinier ou technicien, allez directement sur le <strong>Hub Collaborateur</strong> (<code className="text-primary font-bold">/portail-collaborateur</code>). C'est votre écran d'accueil avec vos boutons prioritaires.
                </p>
              </div>

              <div className="p-4 rounded-xl bg-emerald-500/5 border border-emerald-500/20">
                <h4 className="font-bold text-sm text-emerald-500 mb-1">Règle d'or N°3 : Retrouvez n'importe quelle page en 1 seconde</h4>
                <p className="text-xs text-on-surface-variant leading-relaxed">
                  Appuyez sur <kbd className="px-1.5 py-0.5 rounded bg-surface border border-outline text-primary font-mono font-bold">Ctrl + K</kbd>, tapez les premières lettres de ce que vous cherchez (ex: <em>carburant</em>, <em>bulletin</em>, <em>stock</em>) et appuyez sur Entrée.
                </p>
              </div>
            </div>
          )}
        </div>

        {/* Footer */}
        <div className="px-6 py-3 border-t border-outline bg-surface-container-low flex items-center justify-between shrink-0 text-xs text-on-surface-variant">
          <span>Conseil : Pressez <kbd className="px-1 py-0.5 rounded bg-surface border border-outline font-mono">?</kbd> à tout moment pour rouvrir cette fenêtre.</span>
          <button
            onClick={onClose}
            className="px-4 py-1.5 rounded-lg bg-primary text-on-primary font-bold hover:bg-primary/90 transition-colors"
          >
            J'ai Compris
          </button>
        </div>
      </div>
    </div>
  );
}
