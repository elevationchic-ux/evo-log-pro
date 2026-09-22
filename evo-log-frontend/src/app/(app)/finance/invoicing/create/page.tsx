'use client';

import React, { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import {
  FileText,
  ArrowLeft,
  Save,
  Plus,
  Trash2,
  Building,
  Calendar,
  DollarSign,
  AlertCircle
} from 'lucide-react';
import { financeAPI, tiersAPI } from '@/lib/api-client';
import { toast } from 'sonner';

interface InvoiceLine {
  id: string;
  designation: string;
  quantite: number;
  prix_unitaire_ht: number;
  taux_tva: number; // e.g. 19.25
}

export default function CreateInvoicePage() {
  const router = useRouter();
  const [clients, setClients] = useState<any[]>([]);
  const [loadingClients, setLoadingClients] = useState(true);
  const [submitting, setSubmitting] = useState(false);

  // Form State
  const [clientId, setClientId] = useState('');
  const [numeroFacture, setNumeroFacture] = useState('');
  const [dateEmission, setDateEmission] = useState(new Date().toISOString().slice(0, 10));
  const [dateEcheance, setDateEcheance] = useState(new Date(Date.now() + 30 * 86400000).toISOString().slice(0, 10));
  const [modeReglement, setModeReglement] = useState('VIREMENT');
  const [referenceDossier, setReferenceDossier] = useState('');
  const [conditionsPaiement, setConditionsPaiement] = useState('Paiement à 30 jours fin de mois');

  const [lines, setLines] = useState<InvoiceLine[]>([]);

  useEffect(() => {
    tiersAPI.getTiers()
      .then(res => {
        const raw = res.data?.items || res.data || [];
        setClients(Array.isArray(raw) ? raw : []);
        if (raw.length > 0) setClientId(String(raw[0].id));
      })
      .catch(() => setClients([]))
      .finally(() => setLoadingClients(false));
  }, []);

  const addLine = () => {
    setLines([
      ...lines,
      {
        id: `line-${lines.length + 1}`,
        designation: '',
        quantite: 1,
        prix_unitaire_ht: 0,
        taux_tva: 19.25
      }
    ]);
  };

  const removeLine = (id: string) => {
    if (lines.length > 1) {
      setLines(lines.filter(l => l.id !== id));
    }
  };

  const updateLine = (id: string, field: keyof InvoiceLine, value: any) => {
    setLines(lines.map(l => l.id === id ? { ...l, [field]: value } : l));
  };

  const totalHT = lines.reduce((sum, l) => sum + (Number(l.quantite) * Number(l.prix_unitaire_ht)), 0);
  const totalTVA = lines.reduce((sum, l) => sum + (Number(l.quantite) * Number(l.prix_unitaire_ht) * (Number(l.taux_tva) / 100)), 0);
  const totalTTC = totalHT + totalTVA;

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!clientId && clients.length > 0) {
      toast.error('Veuillez sélectionner un client.');
      return;
    }
    if (!numeroFacture || lines.length === 0 || lines.some(line => !line.designation || line.quantite <= 0)) {
      toast.error('Veuillez renseigner la référence, au moins une ligne valide et les quantités de la facture.');
      return;
    }

    setSubmitting(true);
    try {
      const selectedClient = clients.find(c => String(c.id) === clientId);
      const payload = {
        numero_facture: numeroFacture,
        tiers_id: clientId ? Number(clientId) : undefined,
        client_nom: selectedClient ? selectedClient.nom || selectedClient.raison_sociale : 'Client Comptant',
        date_emission: dateEmission,
        date_echeance: dateEcheance,
        mode_reglement: modeReglement,
        reference_dossier: referenceDossier,
        montant_ht: totalHT,
        montant_tva: totalTVA,
        montant_ttc: totalTTC,
        lignes: lines,
        conditions: conditionsPaiement,
        statut: 'VALIDEE'
      };

      await financeAPI.createFacture(payload);
      toast.success('Facture émise et comptabilisée avec succès !');
      router.push('/finance/invoicing');
    } catch (err: any) {
      toast.error(err?.response?.data?.detail || "Erreur lors de l'émission de la facture.");
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="p-4 sm:p-6 lg:p-8 max-w-5xl mx-auto space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between border-b border-outline pb-5">
        <div className="flex items-center gap-3">
          <button
            onClick={() => router.back()}
            className="p-2 border border-outline rounded-xl text-on-surface-variant hover:bg-surface-container transition-colors"
          >
            <ArrowLeft className="w-4 h-4" />
          </button>
          <div>
            <h1 className="text-2xl font-bold text-on-surface flex items-center gap-2">
              <FileText className="w-6 h-6 text-primary" />
              Émission d'une Nouvelle Facture Client (OHADA)
            </h1>
            <p className="text-sm text-on-surface-variant">
              Génération de décompte conforme au système comptable OHADA révisé (SYSCOHADA)
            </p>
          </div>
        </div>
      </div>

      <form onSubmit={handleSubmit} className="space-y-6">
        {/* En-tête Facture */}
        <div className="bg-surface border border-outline rounded-2xl p-6 space-y-4 shadow-sm">
          <h2 className="font-bold text-sm text-on-surface border-b border-outline pb-2 flex items-center gap-2">
            <Building className="w-4 h-4 text-primary" /> Destinataire & Références
          </h2>

          <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
            <div>
              <label className="block text-xs font-semibold text-on-surface-variant mb-1">Client Débiteur *</label>
              <select
                value={clientId}
                onChange={(e) => setClientId(e.target.value)}
                className="w-full px-3 py-2 text-sm rounded-xl border border-outline bg-surface-container-low text-on-surface focus:outline-none focus:border-primary"
              >
                {clients.length === 0 ? (
                  <option value="">Aucun tiers enregistré (Client Comptant)</option>
                ) : (
                  clients.map(c => (
                    <option key={c.id} value={String(c.id)}>
                      {c.nom || c.raison_sociale} {c.nif ? `(${c.nif})` : ''}
                    </option>
                  ))
                )}
              </select>
            </div>

            <div>
              <label className="block text-xs font-semibold text-on-surface-variant mb-1">Numéro Facture *</label>
              <input
                type="text"
                required
                value={numeroFacture}
                onChange={(e) => setNumeroFacture(e.target.value)}
                className="w-full px-3 py-2 text-sm rounded-xl border border-outline bg-surface-container-low text-on-surface focus:outline-none focus:border-primary font-mono"
              />
            </div>

            <div>
              <label className="block text-xs font-semibold text-on-surface-variant mb-1">Réf. Dossier Opérationnel</label>
              <input
                type="text"
                value={referenceDossier}
                onChange={(e) => setReferenceDossier(e.target.value)}
                placeholder="Ex: TR-2026-0042 / BL-8890"
                className="w-full px-3 py-2 text-sm rounded-xl border border-outline bg-surface-container-low text-on-surface focus:outline-none focus:border-primary"
              />
            </div>

            <div>
              <label className="block text-xs font-semibold text-on-surface-variant mb-1">Date d'Émission</label>
              <input
                type="date"
                required
                value={dateEmission}
                onChange={(e) => setDateEmission(e.target.value)}
                className="w-full px-3 py-2 text-sm rounded-xl border border-outline bg-surface-container-low text-on-surface focus:outline-none focus:border-primary"
              />
            </div>

            <div>
              <label className="block text-xs font-semibold text-on-surface-variant mb-1">Date d'Échéance</label>
              <input
                type="date"
                required
                value={dateEcheance}
                onChange={(e) => setDateEcheance(e.target.value)}
                className="w-full px-3 py-2 text-sm rounded-xl border border-outline bg-surface-container-low text-on-surface focus:outline-none focus:border-primary"
              />
            </div>

            <div>
              <label className="block text-xs font-semibold text-on-surface-variant mb-1">Mode de Règlement Prévu</label>
              <select
                value={modeReglement}
                onChange={(e) => setModeReglement(e.target.value)}
                className="w-full px-3 py-2 text-sm rounded-xl border border-outline bg-surface-container-low text-on-surface focus:outline-none focus:border-primary"
              >
                <option value="VIREMENT">Virement Bancaire</option>
                <option value="CHEQUE">Chèque de Banque</option>
                <option value="TRAITE">Traite / Effet de Commerce</option>
                <option value="ESPECES">Caisse Centrale Espèces</option>
              </select>
            </div>
          </div>
        </div>

        {/* Lignes de Facture */}
        <div className="bg-surface border border-outline rounded-2xl p-6 space-y-4 shadow-sm">
          <div className="flex items-center justify-between border-b border-outline pb-2">
            <h2 className="font-bold text-sm text-on-surface flex items-center gap-2">
              <DollarSign className="w-4 h-4 text-primary" /> Prestations et Lignes de Facturation
            </h2>
            <button
              type="button"
              onClick={addLine}
              className="flex items-center gap-1 px-3 py-1.5 text-xs font-semibold rounded-xl bg-surface-container hover:bg-surface-container-high text-on-surface"
            >
              <Plus className="w-3.5 h-3.5" /> Ajouter une Ligne
            </button>
          </div>

          <div className="space-y-3">
            {lines.map((line, idx) => (
              <div key={line.id} className="grid grid-cols-12 gap-2 items-center bg-surface-container-low p-3 rounded-xl border border-outline/40">
                <div className="col-span-12 sm:col-span-5">
                  <label className="block text-[11px] font-semibold text-on-surface-variant mb-0.5">Désignation Prestation</label>
                  <input
                    type="text"
                    required
                    value={line.designation}
                    onChange={(e) => updateLine(line.id, 'designation', e.target.value)}
                    placeholder="Description de la prestation..."
                    className="w-full px-2.5 py-1.5 text-xs rounded-lg border border-outline bg-surface text-on-surface focus:outline-none focus:border-primary"
                  />
                </div>
                <div className="col-span-4 sm:col-span-2">
                  <label className="block text-[11px] font-semibold text-on-surface-variant mb-0.5">Quantité</label>
                  <input
                    type="number"
                    min="1"
                    required
                    value={line.quantite}
                    onChange={(e) => updateLine(line.id, 'quantite', Number(e.target.value))}
                    className="w-full px-2.5 py-1.5 text-xs rounded-lg border border-outline bg-surface text-on-surface focus:outline-none focus:border-primary text-right"
                  />
                </div>
                <div className="col-span-4 sm:col-span-3">
                  <label className="block text-[11px] font-semibold text-on-surface-variant mb-0.5">P.U. HT (FCFA)</label>
                  <input
                    type="number"
                    min="0"
                    required
                    value={line.prix_unitaire_ht}
                    onChange={(e) => updateLine(line.id, 'prix_unitaire_ht', Number(e.target.value))}
                    className="w-full px-2.5 py-1.5 text-xs rounded-lg border border-outline bg-surface text-on-surface focus:outline-none focus:border-primary text-right font-mono"
                  />
                </div>
                <div className="col-span-3 sm:col-span-1">
                  <label className="block text-[11px] font-semibold text-on-surface-variant mb-0.5">TVA</label>
                  <select
                    value={line.taux_tva}
                    onChange={(e) => updateLine(line.id, 'taux_tva', Number(e.target.value))}
                    className="w-full px-1 py-1.5 text-xs rounded-lg border border-outline bg-surface text-on-surface focus:outline-none focus:border-primary"
                  >
                    <option value={19.25}>19.25%</option>
                    <option value={0}>0% (Exonéré)</option>
                  </select>
                </div>
                <div className="col-span-1 sm:col-span-1 flex justify-center pt-4 sm:pt-4">
                  <button
                    type="button"
                    onClick={() => removeLine(line.id)}
                    className="p-1.5 text-rose-500 hover:bg-rose-500/10 rounded-lg transition-colors"
                  >
                    <Trash2 className="w-4 h-4" />
                  </button>
                </div>
              </div>
            ))}
          </div>

          {/* Totaux */}
          <div className="flex justify-end pt-4">
            <div className="w-full sm:w-72 bg-surface-container-low p-4 rounded-xl space-y-2 border border-outline/50 font-mono text-xs">
              <div className="flex justify-between text-on-surface-variant">
                <span>Total HT :</span>
                <span className="font-semibold text-on-surface">{totalHT.toLocaleString('fr-FR')} FCFA</span>
              </div>
              <div className="flex justify-between text-on-surface-variant">
                <span>TVA (19.25%) :</span>
                <span className="font-semibold text-on-surface">{Math.round(totalTVA).toLocaleString('fr-FR')} FCFA</span>
              </div>
              <div className="border-t border-outline/40 pt-2 flex justify-between text-sm font-bold text-primary font-sans">
                <span>Total Net à Payer (TTC) :</span>
                <span className="font-mono">{Math.round(totalTTC).toLocaleString('fr-FR')} FCFA</span>
              </div>
            </div>
          </div>
        </div>

        <div className="flex justify-end gap-3 pt-2">
          <button
            type="button"
            onClick={() => router.back()}
            className="px-5 py-2.5 border border-outline rounded-xl text-sm font-semibold text-on-surface hover:bg-surface-container transition-colors"
          >
            Annuler
          </button>
          <button
            type="submit"
            disabled={submitting}
            className="flex items-center gap-2 px-6 py-2.5 rounded-xl text-sm font-semibold bg-primary text-on-primary hover:opacity-90 transition-opacity disabled:opacity-50"
          >
            <Save className="w-4 h-4" />
            {submitting ? 'Validation...' : 'Valider & Émettre la Facture'}
          </button>
        </div>
      </form>
    </div>
  );
}
