'use client';

import React, { useState, useRef, useEffect } from 'react';

export const GLOSSARY: Record<string, { title: string; definition: string; category: 'Douane' | 'Logistique' | 'Comptabilité' | 'Technique' | 'Sécurité'; fullForm?: string }> = {
  BAPLIE: {
    title: 'BAPLIE',
    fullForm: 'Bay Plan EDIFACT (ISO 9735)',
    definition: 'Fichier informatique standard international échangé entre le navire porte-conteneurs et l\'acconier décrivant l\'emplacement exact (baie, rangée, niveau) de chaque conteneur à bord.',
    category: 'Logistique',
  },
  STS: {
    title: 'Portique STS',
    fullForm: 'Ship-To-Shore Gantry Crane',
    definition: 'Grand portique de quai sur rails utilisé pour décharger et charger les conteneurs maritimes directement entre le navire et le quai.',
    category: 'Logistique',
  },
  TEU: {
    title: 'TEU / EVP',
    fullForm: 'Twenty-foot Equivalent Unit (Équivalent Vingt Pieds)',
    definition: 'Unité de mesure standard mondiale du volume de conteneurs. 1 conteneur 20 pieds = 1 EVP ; 1 conteneur 40 pieds = 2 EVP.',
    category: 'Logistique',
  },
  EVP: {
    title: 'EVP / TEU',
    fullForm: 'Équivalent Vingt Pieds',
    definition: 'Unité statistique désignant un conteneur standard de 20 pieds de long (environ 6 mètres).',
    category: 'Logistique',
  },
  DUM: {
    title: 'DUM',
    fullForm: 'Déclaration Unique de Marchandises',
    definition: 'Document officiel légal souscrit par le déclarant en douane sur la plateforme CAMCIS/Sydonia pour déclarer l\'espèce, la valeur CAF et l\'origine des marchandises.',
    category: 'Douane',
  },
  BAE: {
    title: 'BAE',
    fullForm: 'Bon à Enlever',
    definition: 'Autorisation administrative officielle délivrée par le service des douanes autorisant le propriétaire ou transitaire à retirer physiquement la marchandise de l\'enceinte portuaire.',
    category: 'Douane',
  },
  CAMCIS: {
    title: 'CAMCIS',
    fullForm: 'Cameroon Customs Information System',
    definition: 'Système d\'information douanier automatisé de la Direction Générale des Douanes du Cameroun assurant le dédouanement électronique.',
    category: 'Douane',
  },
  FEFO: {
    title: 'FEFO',
    fullForm: 'First Expired, First Out (Premier Périmé, Premier Sorti)',
    definition: 'Méthode de gestion logistique où les lots ayant la date limite de consommation (DLC) la plus proche sont prélevés et expédiés en priorité absolue.',
    category: 'Logistique',
  },
  FIFO: {
    title: 'FIFO',
    fullForm: 'First In, First Out (Premier Entré, Premier Sorti)',
    definition: 'Méthode de gestion d\'entrepôt où le premier article réceptionné en stock est le premier à être expédié.',
    category: 'Logistique',
  },
  ROP: {
    title: 'ROP (Point de Commande)',
    fullForm: 'Reorder Point (Formule de Wilson)',
    definition: 'Niveau de stock seuil déclenchant automatiquement une commande de réapprovisionnement pour éviter toute rupture pendant le délai de livraison.',
    category: 'Logistique',
  },
  TCO: {
    title: 'TCO',
    fullForm: 'Total Cost of Ownership (Coût Global de Possession)',
    definition: 'Calcul analytique complet du coût réel d\'un camion ou engin de levage : achat, carburant, pièces d\'usure, assurance et amortissement.',
    category: 'Technique',
  },
  IRPP: {
    title: 'IRPP',
    fullForm: 'Impôt sur le Revenu des Personnes Physiques',
    definition: 'Prélèvement fiscal légal à la source progressif (barème de 10% à 35%) retenu sur le salaire brut imposable selon le Code Général des Impôts.',
    category: 'Comptabilité',
  },
  DIPE: {
    title: 'DIPE Magnétique',
    fullForm: 'Document d\'Information sur le Personnel Employé',
    definition: 'Fichier déclaratif mensuel normé transmis obligatoirement à la Direction Générale des Impôts (DGI) et à la CNPS récapitulant les salaires et cotisations.',
    category: 'Comptabilité',
  },
  MAD: {
    title: 'MAD / Entrepôt Sous-Douane',
    fullForm: 'Magasin et Aire de Dédouanement',
    definition: 'Zone clôturée agréée par la douane où les marchandises importées peuvent séjourner en suspension temporaire des droits de douane et de la TVA.',
    category: 'Douane',
  },
  ePOD: {
    title: 'ePOD',
    fullForm: 'Electronic Proof of Delivery',
    definition: 'Preuve électronique de livraison comportant l\'horodatage certifié, les coordonnées GPS et la signature tactile du destinataire sur smartphone/tablette.',
    category: 'Logistique',
  },
  CMR: {
    title: 'CMR',
    fullForm: 'Convention relative au contrat de transport international de Marchandises par Route',
    definition: 'Lettre de voiture internationale normalisée faisant foi du contrat de transport entre l\'expéditeur, le transporteur routier et le destinataire final.',
    category: 'Logistique',
  },
  OT: {
    title: 'OT (GMAO)',
    fullForm: 'Ordre de Travail Atelier',
    definition: 'Document d\'instruction assigné à un mécanicien ou électromécanicien pour exécuter une maintenance préventive ou une réparation curative sur un véhicule.',
    category: 'Technique',
  },
  PDR: {
    title: 'PDR',
    fullForm: 'Pièce Détachée de Rechange',
    definition: 'Composant mécanique, électrique ou hydraulique (filtres, plaquettes, injecteurs) stocké en magasin pour la maintenance de la flotte.',
    category: 'Technique',
  },
  IMDG: {
    title: 'Code IMDG',
    fullForm: 'International Maritime Dangerous Goods Code',
    definition: 'Réglementation internationale de l\'OMI régissant l\'emballage, l\'étiquetage, l\'arrimage et la ségrégation des matières dangereuses transportées par mer.',
    category: 'Sécurité',
  },
  SYSCOHADA: {
    title: 'SYSCOHADA Révisé',
    fullForm: 'Système Comptable de l\'Organisation pour l\'Harmonisation en Afrique du Droit des Affaires',
    definition: 'Norme comptable légale obligatoire dans les 17 pays membres de l\'OHADA régissant le plan de comptes (classes 1 à 9) et les états financiers annuels.',
    category: 'Comptabilité',
  },
  CEMAC: {
    title: 'Zone CEMAC',
    fullForm: 'Communauté Économique et Monétaire de l\'Afrique Centrale',
    definition: 'Union douanière et monétaire regroupant le Cameroun, la Centrafrique, le Congo, le Gabon, la Guinée Équatoriale et le Tchad utilisant le Franc CFA (XAF).',
    category: 'Douane',
  },
};

interface TermDefinitionProps {
  term: string;
  children?: React.ReactNode;
  showIcon?: boolean;
}

export function TermDefinition({ term, children, showIcon = true }: TermDefinitionProps) {
  const [isOpen, setIsOpen] = useState(false);
  const info = GLOSSARY[term.toUpperCase()] || {
    title: term,
    definition: 'Terme spécialisé utilisé dans les opérations logistiques, portuaires ou comptables d\'EVO-LOG.',
    category: 'Technique',
  };

  const popoverRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const handleOutsideClick = (e: MouseEvent) => {
      if (popoverRef.current && !popoverRef.current.contains(e.target as Node)) {
        setIsOpen(false);
      }
    };
    if (isOpen) {
      document.addEventListener('mousedown', handleOutsideClick);
    }
    return () => document.removeEventListener('mousedown', handleOutsideClick);
  }, [isOpen]);

  const categoryColors: Record<string, string> = {
    Douane: 'bg-amber-500/10 text-amber-500 border-amber-500/20',
    Logistique: 'bg-blue-500/10 text-blue-500 border-blue-500/20',
    Comptabilité: 'bg-emerald-500/10 text-emerald-500 border-emerald-500/20',
    Technique: 'bg-purple-500/10 text-purple-500 border-purple-500/20',
    Sécurité: 'bg-rose-500/10 text-rose-500 border-rose-500/20',
  };

  return (
    <span className="relative inline-flex items-center group cursor-help" ref={popoverRef}>
      <span
        onClick={(e) => {
          e.stopPropagation();
          setIsOpen(!isOpen);
        }}
        className="underline decoration-dotted decoration-primary/60 underline-offset-4 hover:text-primary transition-colors inline-flex items-center gap-0.5"
      >
        {children || term}
        {showIcon && (
          <span className="material-symbols-outlined text-[14px] text-on-surface-variant/70 group-hover:text-primary">
            help_outline
          </span>
        )}
      </span>

      {isOpen && (
        <div
          className="absolute bottom-full left-1/2 -translate-x-1/2 mb-2 w-72 p-3 bg-surface border border-outline rounded-xl shadow-2xl z-50 animate-in fade-in zoom-in-95 duration-150 text-left"
          onClick={(e) => e.stopPropagation()}
        >
          <div className="flex items-center justify-between gap-2 mb-1.5">
            <span className="font-bold text-sm text-on-surface">{info.title}</span>
            <span className={`text-[10px] font-bold px-1.5 py-0.5 rounded border uppercase ${categoryColors[info.category]}`}>
              {info.category}
            </span>
          </div>

          {info.fullForm && (
            <p className="text-[11px] font-medium text-primary mb-1.5 leading-snug">
              {info.fullForm}
            </p>
          )}

          <p className="text-xs text-on-surface-variant leading-relaxed">
            {info.definition}
          </p>

          <div className="mt-2.5 pt-2 border-t border-outline/50 flex items-center justify-between text-[10px] text-on-surface-variant/80">
            <span>Guide d'aide EVO-LOG</span>
            <button
              onClick={() => setIsOpen(false)}
              className="font-bold text-primary hover:underline"
            >
              Fermer
            </button>
          </div>
        </div>
      )}
    </span>
  );
}
