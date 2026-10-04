'use client';

import React, { useState, useEffect } from 'react';
import {
  BookOpen, Plus, Search, Filter, Download, CheckCircle2,
  AlertTriangle, RefreshCw, Layers, ArrowUpDown, FileText, Check,
  Printer, X, Tag, Loader2
} from 'lucide-react';
import { toast } from 'sonner';
import CompanyDocumentHeader, { CompanyDocumentFooter } from '@/components/documents/CompanyDocumentHeader';

export interface EntryLine {
  id: string;
  date: string;
  piece: string;
  journal: string;
  compte: string;
  compte_intitule: string;
  libelle: string;
  debit: number;
  credit: number;
  lettrage?: string;
  validated: boolean;
}

interface CompteAPI {
  id: number;
  numero_compte: string;
  intitule: string;
}

interface JournalAPI {
  id: number;
  code_journal: string;
  nom_journal: string;
  type_journal: string;
}

interface PieceLigneSaisie {
  compte_id: number | null;
  debit: number;
  credit: number;
}

const JOURNAL_TYPES = ['VENTES', 'ACHATS', 'BANQUE', 'CAISSE', 'SALAIRES', 'AMORTISSEMENTS', 'OD', 'TVA'] as const;

const ligneVide = (): PieceLigneSaisie => ({ compte_id: null, debit: 0, credit: 0 });

const detailErreur = async (res: Response): Promise<string> => {
  try {
    const body = await res.json();
    const d = body?.detail;
    if (typeof d === 'string') return d;
    if (Array.isArray(d)) {
      return d.map((e: Record<string, unknown>) => {
        const loc = Array.isArray(e?.loc) ? e.loc.join('.') : '';
        return `${loc ? `[${loc}] ` : ''}${String(e?.msg ?? '')}`;
      }).join('; ');
    }
    return JSON.stringify(d ?? body);
  } catch {
    return `HTTP ${res.status}`;
  }
};

export default function ComptabiliteOhadaJournal() {
  const [entries, setEntries] = useState<EntryLine[]>([]);
  const [loading, setLoading] = useState(true);
  const [listeErreur, setListeErreur] = useState<string | null>(null);
  const [selectedJournal, setSelectedJournal] = useState<string>('ALL');
  const [searchQuery, setSearchQuery] = useState('');
  const [showNewModal, setShowNewModal] = useState(false);
  const [selectedIds, setSelectedIds] = useState<string[]>([]);
  const [isLettrageModalOpen, setIsLettrageModalOpen] = useState(false);
  const [lettrageCode, setLettrageCode] = useState('LA01');

  // Referels reels lus depuis l'API (aucun compte codé en dur).
  const [comptes, setComptes] = useState<CompteAPI[]>([]);
  const [journaux, setJournaux] = useState<JournalAPI[]>([]);

  // Saisie de piece en partie double : en-tete + lignes.
  const [newDate, setNewDate] = useState(new Date().toISOString().split('T')[0]);
  const [newJournal, setNewJournal] = useState<string>('VENTES');
  const [newPiece, setNewPiece] = useState('');
  const [newLibelle, setNewLibelle] = useState('');
  const [lignes, setLignes] = useState<PieceLigneSaisie[]>([ligneVide(), ligneVide()]);
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    const chargerReferentiels = async () => {
      const headers = { 'Authorization': `Bearer ${localStorage.getItem('access_token') || ''}` };
      try {
        const res = await fetch('/api/v1/finance/plan-comptable?actif=true&limit=500', { headers });
        if (res.ok) {
          const data = await res.json();
          setComptes(Array.isArray(data) ? data.map((c: CompteAPI) => ({
            id: c.id, numero_compte: c.numero_compte, intitule: c.intitule,
          })) : []);
        } else {
          setListeErreur(`Plan comptable inaccessible (${await detailErreur(res)})`);
        }
      } catch {
        setListeErreur('Plan comptable inaccessible : API injoignable.');
      }
      try {
        const res = await fetch('/api/v1/comptabilite-avance/journaux', { headers });
        if (res.ok) {
          const data = await res.json();
          const brut = Array.isArray(data) ? data : (data?.journaux ?? data?.items ?? data?.data ?? []);
          setJournaux(Array.isArray(brut) ? brut : []);
        }
      } catch {
        /* le select fallback sur les types de journaux standards */
      }
    };
    chargerReferentiels();
  }, []);

  const majLigne = (index: number, champ: 'compte_id' | 'debit' | 'credit', valeur: number | null) => {
    setLignes(prev => prev.map((l, i) => {
      if (i !== index) return l;
      if (champ === 'debit' && (valeur ?? 0) > 0) return { ...l, debit: valeur ?? 0, credit: 0 };
      if (champ === 'credit' && (valeur ?? 0) > 0) return { ...l, debit: 0, credit: valeur ?? 0 };
      return { ...l, [champ]: valeur };
    }));
  };

  const ajouterLigne = () => setLignes(prev => [...prev, ligneVide()]);

  const retirerLigne = (index: number) =>
    setLignes(prev => (prev.length > 2 ? prev.filter((_, i) => i !== index) : prev));

  const totalDebitSaisie = lignes.reduce((a, l) => a + (Number(l.debit) || 0), 0);
  const totalCreditSaisie = lignes.reduce((a, l) => a + (Number(l.credit) || 0), 0);
  const ecartSaisie = Math.round((totalDebitSaisie - totalCreditSaisie) * 100) / 100;
  const pieceEquilibree = Math.abs(ecartSaisie) < 0.01 && totalDebitSaisie > 0;
  const blocageSaisie = (() => {
    if (lignes.length < 2) return 'Une piece en partie double exige au moins 2 lignes.';
    if (lignes.some(l => !l.compte_id)) return 'Chaque ligne doit porter un compte du plan comptable.';
    if (lignes.some(l => (l.debit > 0 && l.credit > 0) || (l.debit <= 0 && l.credit <= 0))) {
      return 'Chaque ligne doit porter exactement un cote : debit OU credit, non nul.';
    }
    if (!pieceEquilibree) return `Piece desequilibree : ecart debit - credit = ${ecartSaisie.toLocaleString()} XAF.`;
    return null;
  })();

  const fetchEntries = async () => {
    setLoading(true);
    try {
      const res = await fetch(`/api/v1/comptabilite-avance/ecritures?journal=${selectedJournal}`, {
        headers: { 'Authorization': `Bearer ${localStorage.getItem('access_token') || ''}` }
      });
      if (res.ok) {
        const data = await res.json();
        if (Array.isArray(data)) {
          // Une piece = un en-tete + ses lignes ; le livre-journal s'affiche
          // ligne par ligne, avec les comptes reels de la piece.
          const plats: EntryLine[] = [];
          for (const item of data) {
            const lines = Array.isArray(item.lignes) ? item.lignes : [];
            const base = {
              date: item.date_ecriture || new Date().toISOString().split('T')[0],
              piece: item.numero_piece || item.numero_ecriture || 'PIECE',
              journal: item.journal || 'OD',
              lettrage: item.lettrage || undefined,
              validated: Boolean(item.valider),
            };
            if (lines.length > 0) {
              for (const l of lines) {
                plats.push({
                  ...base,
                  id: `${item.id}-${l.id}`,
                  compte: l.compte_numero || '',
                  compte_intitule: l.compte_intitule || '',
                  libelle: l.libelle_detail || item.libelle || '',
                  debit: parseFloat(String(l.debit ?? 0)),
                  credit: parseFloat(String(l.credit ?? 0)),
                });
              }
            } else {
              plats.push({
                ...base,
                id: String(item.id ?? item.numero_ecriture),
                compte: item.compte_numero || String(item.compte_id ?? ''),
                compte_intitule: '',
                libelle: item.libelle || '',
                debit: parseFloat(String(item.debit ?? 0)),
                credit: parseFloat(String(item.credit ?? 0)),
              });
            }
          }
          setEntries(plats);
          setListeErreur(null);
        } else {
          setEntries([]);
        }
      } else {
        setEntries([]);
        setListeErreur(`Lecture du journal impossible (${await detailErreur(res)}).`);
      }
    } catch {
      setEntries([]);
      setListeErreur('Lecture du journal impossible : API injoignable.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchEntries();
  }, [selectedJournal]);

  const filteredEntries = entries.filter(e => {
    const matchJournal = selectedJournal === 'ALL'
      || e.journal === selectedJournal
      || journaux.some(j => j.code_journal === e.journal && j.type_journal === selectedJournal);
    const matchSearch = e.piece.toLowerCase().includes(searchQuery.toLowerCase()) ||
      e.compte.toLowerCase().includes(searchQuery.toLowerCase()) ||
      e.libelle.toLowerCase().includes(searchQuery.toLowerCase());
    return matchJournal && matchSearch;
  });

  const totalDebit = filteredEntries.reduce((acc, curr) => acc + curr.debit, 0);
  const totalCredit = filteredEntries.reduce((acc, curr) => acc + curr.credit, 0);
  const isBalanced = Math.abs(totalDebit - totalCredit) < 0.01;

  const handleAddPiece = async (e: React.FormEvent) => {
    e.preventDefault();
    if (blocageSaisie) {
      toast.error(blocageSaisie);
      return;
    }
    setSaving(true);
    try {
      const res = await fetch('/api/v1/finance/pieces', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('access_token') || ''}`
        },
        body: JSON.stringify({
          date_ecriture: newDate,
          libelle: newLibelle,
          numero_piece: newPiece || null,
          type_journal: newJournal,
          lignes: lignes.map(l => ({
            compte_id: l.compte_id,
            debit: Number(l.debit) || 0,
            credit: Number(l.credit) || 0,
          })),
        })
      });
      if (res.ok) {
        const piece = await res.json();
        toast.success(`Piece ${piece.numero_ecriture} enregistree (${lignes.length} lignes, equilibree)`);
        fetchEntries();
        setShowNewModal(false);
        setNewPiece('');
        setNewLibelle('');
        setLignes([ligneVide(), ligneVide()]);
      } else {
        toast.error(`Piece rejetee par le serveur : ${await detailErreur(res)}`);
      }
    } catch {
      toast.error('Erreur reseau piece non enregistree.');
    } finally {
      setSaving(false);
    }
  };

  const handleApplyLettrage = () => {
    if (selectedIds.length === 0) {
      toast.error('Veuillez sélectionner au moins 2 lignes à lettrer');
      return;
    }

    const selectedLines = entries.filter(e => selectedIds.includes(e.id));
    const selDebit = selectedLines.reduce((acc, c) => acc + c.debit, 0);
    const selCredit = selectedLines.reduce((acc, c) => acc + c.credit, 0);

    if (Math.abs(selDebit - selCredit) > 0.01) {
      toast.error(`Déséquilibre de lettrage : Débit (${selDebit.toLocaleString()} XAF) ≠ Crédit (${selCredit.toLocaleString()} XAF)`);
      return;
    }

    toast.error('Le lettrage doit être exécuté par un endpoint comptable persistant.');
  };

  const handleRemoveLettrage = () => {
    if (selectedIds.length === 0) return;
    toast.error('La suppression du lettrage doit être exécutée par un endpoint comptable persistant.');
  };

  const toggleSelect = (id: string) => {
    setSelectedIds(prev => prev.includes(id) ? prev.filter(i => i !== id) : [...prev, id]);
  };

  const handlePrint = () => {
    toast.success('Génération de l\'état certifié du Journal OHADA...');
    window.print();
  };

  return (
    <div className="space-y-6 animate-in fade-in duration-300 font-sans">
      {/* Official Corporate Header for Print */}
      <div className="hidden print:block">
        <CompanyDocumentHeader
          documentTitle="LIVRE-JOURNAL DES ÉCRITURES SYSCOHADA"
          documentNumber={`JRN-${selectedJournal}-${new Date().getFullYear()}`}
          documentDate={new Date().toLocaleDateString('fr-FR')}
          documentReference={`JOURNAL-${selectedJournal}`}
        />
      </div>

      {/* Screen Header Controls */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 bg-slate-900/90 border border-violet-500/30 p-6 rounded-3xl shadow-xl backdrop-blur-xl print:hidden">
        <div>
          <div className="flex items-center gap-2 mb-2">
            <span className="px-2.5 py-0.5 rounded-full text-[11px] font-black tracking-wider uppercase bg-violet-500/20 text-violet-300 border border-violet-500/30">
              Livre-Journal Général & Auxiliaires
            </span>
            <span className="font-mono text-xs text-amber-400 font-bold bg-slate-950 px-2 py-0.5 rounded border border-slate-800">
              T-Code : KOHA_JRN
            </span>
          </div>
          <h1 className="text-2xl sm:text-3xl font-black text-slate-100 flex items-center gap-3">
            <BookOpen className="w-8 h-8 text-violet-400" />
            Journaux Auxiliaires OHADA
          </h1>
          <p className="text-xs sm:text-sm text-slate-400 mt-1">
            Ventilation comptable des 7 journaux standards SYSCOHADA avec lettrage automatique et contrôle d&apos;équilibre.
          </p>
        </div>

        <div className="flex items-center gap-3">
          <button
            onClick={() => setIsLettrageModalOpen(true)}
            disabled={selectedIds.length < 2}
            className="px-4 py-2.5 bg-slate-800 hover:bg-slate-700 disabled:opacity-40 text-amber-300 border border-amber-500/30 font-bold text-xs rounded-xl flex items-center gap-2 transition-all"
          >
            <Layers className="w-4 h-4 text-amber-400" /> Lettrer la Sélection ({selectedIds.length})
          </button>
          <button
            onClick={handlePrint}
            className="px-4 py-2.5 bg-slate-800 hover:bg-slate-700 text-slate-200 border border-slate-700 font-bold text-xs rounded-xl flex items-center gap-2 transition-all"
          >
            <Printer className="w-4 h-4 text-slate-400" /> Imprimer Journal
          </button>
          <button
            onClick={() => setShowNewModal(true)}
            className="px-4 py-2.5 bg-gradient-to-r from-violet-600 to-indigo-600 hover:from-violet-500 hover:to-indigo-500 text-white font-bold text-xs rounded-xl flex items-center gap-2 shadow-lg shadow-violet-500/25 transition-all"
          >
            <Plus className="w-4 h-4" /> Saisir Écriture
          </button>
        </div>
      </div>

      {/* Onglets des 7 Journaux Auxiliaires */}
      <div className="flex items-center gap-2 overflow-x-auto pb-2 scrollbar-none print:hidden">
        {[
          { key: 'ALL', label: 'Tous les Journaux' },
          { key: 'VENTES', label: 'Journal des Ventes (VE)' },
          { key: 'ACHATS', label: 'Journal des Achats (AC)' },
          { key: 'BANQUE', label: 'Journal de Banque (BQ)' },
          { key: 'CAISSE', label: 'Journal de Caisse (CA)' },
          { key: 'SALAIRES', label: 'Journal des Salaires (OD-PAY)' },
          { key: 'AMORTISSEMENTS', label: 'Dotations Amortissements (OD-DOT)' },
          { key: 'OD', label: 'Opérations Diverses (OD)' }
        ].map(tab => (
          <button
            key={tab.key}
            onClick={() => setSelectedJournal(tab.key)}
            className={`px-4 py-2 rounded-xl text-xs font-bold whitespace-nowrap transition-all border ${selectedJournal === tab.key
                ? 'bg-violet-600 text-white border-violet-500 shadow-md shadow-violet-600/30'
                : 'bg-slate-900/80 text-slate-400 border-slate-800 hover:bg-slate-800 hover:text-slate-200'
              }`}
          >
            {tab.label}
          </button>
        ))}
      </div>

      {/* Barre de Recherche & Contrôles */}
      <div className="bg-slate-900/90 border border-slate-800 p-4 rounded-2xl flex flex-col sm:flex-row items-center justify-between gap-4 print:hidden">
        <div className="relative w-full sm:w-96">
          <Search className="w-4 h-4 absolute left-3.5 top-1/2 -translate-y-1/2 text-slate-500" />
          <input
            type="text"
            placeholder="Rechercher par N° pièce, compte ou libellé..."
            value={searchQuery}
            onChange={e => setSearchQuery(e.target.value)}
            className="w-full pl-10 pr-4 py-2 bg-slate-950 border border-slate-800 rounded-xl text-xs text-slate-200 placeholder-slate-500 focus:outline-none focus:border-violet-500 font-mono"
          />
        </div>

        <div className="flex items-center gap-4 text-xs font-mono">
          <span className="text-slate-400">Total Débit : <b className="text-emerald-400">{totalDebit.toLocaleString()} XAF</b></span>
          <span className="text-slate-400">Total Crédit : <b className="text-blue-400">{totalCredit.toLocaleString()} XAF</b></span>
          <span className={`px-2.5 py-1 rounded-full font-bold flex items-center gap-1 ${isBalanced ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20' : 'bg-red-500/10 text-red-400 border border-red-500/20'
            }`}>
            {isBalanced ? <CheckCircle2 className="w-3.5 h-3.5" /> : <AlertTriangle className="w-3.5 h-3.5" />}
            {isBalanced ? 'Équilibré (D=C)' : 'Déséquilibre Détecté'}
          </span>
        </div>
      </div>

      {/* Tableau des Écritures */}
      <div className="bg-slate-900/90 border border-slate-800 rounded-3xl overflow-hidden shadow-xl">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead className="bg-slate-950/80 border-b border-slate-800 text-[11px] uppercase tracking-wider font-mono text-slate-400">
              <tr>
                <th className="py-3 px-4 w-10 print:hidden">
                  <input
                    type="checkbox"
                    checked={selectedIds.length > 0 && selectedIds.length === filteredEntries.length}
                    onChange={() => {
                      if (selectedIds.length === filteredEntries.length) setSelectedIds([]);
                      else setSelectedIds(filteredEntries.map(e => e.id));
                    }}
                    className="rounded border-slate-700 bg-slate-900"
                  />
                </th>
                <th className="py-3 px-4">Date</th>
                <th className="py-3 px-4">N° Pièce</th>
                <th className="py-3 px-4">Journal</th>
                <th className="py-3 px-4">Compte OHADA</th>
                <th className="py-3 px-4">Libellé de l&apos;Écriture</th>
                <th className="py-3 px-4 text-right">Débit (XAF)</th>
                <th className="py-3 px-4 text-right">Crédit (XAF)</th>
                <th className="py-3 px-4 text-center">Lettrage</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60 font-mono">
              {filteredEntries.length === 0 ? (
                <tr>
                  <td colSpan={9} className="py-12 text-center text-slate-500">
                    <BookOpen className="w-10 h-10 mx-auto mb-2 text-slate-400" />
                    Aucune écriture enregistrée pour ce journal. Cliquez sur &quot;Saisir Écriture&quot; pour débuter.
                  </td>
                </tr>
              ) : (
                filteredEntries.map(entry => {
                  const isSelected = selectedIds.includes(entry.id);
                  return (
                    <tr
                      key={entry.id}
                      className={`hover:bg-slate-800/40 transition-colors ${isSelected ? 'bg-violet-950/20' : ''
                        }`}
                    >
                      <td className="py-3 px-4 print:hidden">
                        <input
                          type="checkbox"
                          checked={isSelected}
                          onChange={() => toggleSelect(entry.id)}
                          className="rounded border-slate-700 bg-slate-900 text-violet-600 focus:ring-violet-500"
                        />
                      </td>
                      <td className="py-3 px-4 text-slate-300 whitespace-nowrap">{entry.date}</td>
                      <td className="py-3 px-4 font-bold text-violet-400">{entry.piece}</td>
                      <td className="py-3 px-4">
                        <span className="px-2 py-0.5 rounded-full text-[11px] font-bold bg-slate-950 border border-slate-800 text-slate-300">
                          {entry.journal}
                        </span>
                      </td>
                      <td className="py-3 px-4 font-bold text-amber-300">
                        {entry.compte}
                        {entry.compte_intitule && (
                          <span className="block text-[10px] text-slate-500 font-sans font-normal truncate max-w-[180px]">{entry.compte_intitule}</span>
                        )}
                      </td>
                      <td className="py-3 px-4 text-slate-200 font-sans max-w-xs truncate">{entry.libelle}</td>
                      <td className="py-3 px-4 text-right font-bold text-emerald-400">
                        {entry.debit > 0 ? entry.debit.toLocaleString() : '-'}
                      </td>
                      <td className="py-3 px-4 text-right font-bold text-blue-400">
                        {entry.credit > 0 ? entry.credit.toLocaleString() : '-'}
                      </td>
                      <td className="py-3 px-4 text-center">
                        {entry.lettrage ? (
                          <span className="px-2 py-0.5 rounded bg-amber-500/15 border border-amber-500/30 text-amber-300 text-[11px] font-bold font-mono">
                            {entry.lettrage}
                          </span>
                        ) : (
                          <span className="text-slate-400 text-[11px]">-</span>
                        )}
                      </td>
                    </tr>
                  );
                })
              )}
            </tbody>
          </table>
        </div>
      </div>

      {/* Official Footer for Print */}
      <div className="hidden print:block">
        <CompanyDocumentFooter />
      </div>

      {/* MODAL SAISIE DE PIECE (PARTIE DOUBLE) */}
      {showNewModal && (
        <div className="fixed inset-0 z-[100] bg-black/80 backdrop-blur-sm flex items-center justify-center p-4">
          <div className="bg-slate-900 border border-violet-500/40 rounded-3xl p-6 max-w-3xl w-full shadow-2xl space-y-4 animate-in zoom-in-95 duration-200 max-h-[92vh] overflow-y-auto">
            <div className="flex items-center justify-between pb-3 border-b border-slate-800">
              <h3 className="text-base font-bold text-white flex items-center gap-2">
                <BookOpen className="w-5 h-5 text-violet-400" />
                Saisir une Piece en Partie Double
              </h3>
              <button onClick={() => setShowNewModal(false)} className="text-slate-400 hover:text-white p-1">
                <X className="w-5 h-5" />
              </button>
            </div>

            <form onSubmit={handleAddPiece} className="space-y-3">
              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-[11px] font-bold text-slate-300 uppercase mb-1">Date</label>
                  <input
                    type="date"
                    value={newDate}
                    onChange={e => setNewDate(e.target.value)}
                    className="w-full h-10 px-3 bg-slate-950 border border-slate-800 rounded-xl text-xs text-white"
                    required
                  />
                </div>
                <div>
                  <label className="block text-[11px] font-bold text-slate-300 uppercase mb-1">Journal</label>
                  <select
                    value={newJournal}
                    onChange={e => setNewJournal(e.target.value)}
                    className="w-full h-10 px-3 bg-slate-950 border border-slate-800 rounded-xl text-xs text-white"
                  >
                    {JOURNAL_TYPES.map(t => {
                      const j = journaux.find(x => String(x.type_journal || '').toUpperCase() === t);
                      return <option key={t} value={t}>{j ? j.nom_journal : `Journal ${t} (${t})`}</option>;
                    })}
                  </select>
                </div>
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-[11px] font-bold text-slate-300 uppercase mb-1">N° de Piece (facultatif)</label>
                  <input
                    type="text"
                    placeholder="FAC-2026-..."
                    value={newPiece}
                    onChange={e => setNewPiece(e.target.value)}
                    className="w-full h-10 px-3 bg-slate-950 border border-slate-800 rounded-xl text-xs text-white font-mono"
                  />
                </div>
                <div>
                  <label className="block text-[11px] font-bold text-slate-300 uppercase mb-1">Libellé de la piece</label>
                  <input
                    type="text"
                    placeholder="Désignation de la transaction..."
                    value={newLibelle}
                    onChange={e => setNewLibelle(e.target.value)}
                    className="w-full h-10 px-3 bg-slate-950 border border-slate-800 rounded-xl text-xs text-white"
                    required
                  />
                </div>
              </div>

              {/* Lignes de la piece : un compte + debit OU credit par ligne */}
              <div className="border border-slate-800 rounded-2xl overflow-hidden">
                <div className="grid grid-cols-[1fr_120px_120px_32px] gap-2 bg-slate-950 px-3 py-2 text-[10px] font-bold uppercase tracking-wider text-slate-400 border-b border-slate-800">
                  <span>Compte SYSCOHADA (plan réel)</span>
                  <span className="text-right">Débit (XAF)</span>
                  <span className="text-right">Crédit (XAF)</span>
                  <span />
                </div>
                {lignes.map((ligne, index) => (
                  <div key={index} className="grid grid-cols-[1fr_120px_120px_32px] gap-2 items-center px-3 py-2 border-b border-slate-800/60 last:border-b-0">
                    <select
                      value={ligne.compte_id ?? ''}
                      onChange={e => majLigne(index, 'compte_id', e.target.value ? Number(e.target.value) : null)}
                      className="h-9 px-2 bg-slate-950 border border-slate-800 rounded-xl text-xs text-white font-mono"
                      required
                    >
                      <option value="">— choisir un compte —</option>
                      {comptes.map(c => (
                        <option key={c.id} value={c.id}>{c.numero_compte} · {c.intitule}</option>
                      ))}
                    </select>
                    <input
                      type="number" min="0" step="0.01"
                      value={ligne.debit || ''}
                      onChange={e => majLigne(index, 'debit', parseFloat(e.target.value) || 0)}
                      placeholder="0"
                      className="h-9 px-2 bg-slate-950 border border-slate-800 rounded-xl text-xs text-white font-mono text-right"
                    />
                    <input
                      type="number" min="0" step="0.01"
                      value={ligne.credit || ''}
                      onChange={e => majLigne(index, 'credit', parseFloat(e.target.value) || 0)}
                      placeholder="0"
                      className="h-9 px-2 bg-slate-950 border border-slate-800 rounded-xl text-xs text-white font-mono text-right"
                    />
                    <button
                      type="button"
                      onClick={() => retirerLigne(index)}
                      disabled={lignes.length <= 2}
                      title={lignes.length <= 2 ? 'Une piece en partie double exige au moins 2 lignes' : 'Retirer cette ligne'}
                      className="h-9 w-8 flex items-center justify-center bg-slate-800 hover:bg-red-500/20 disabled:opacity-30 disabled:hover:bg-slate-800 text-slate-400 rounded-xl"
                    >
                      <X className="w-3.5 h-3.5" />
                    </button>
                  </div>
                ))}
                <div className="px-3 py-2 bg-slate-950/60">
                  <button
                    type="button"
                    onClick={ajouterLigne}
                    className="px-3 py-1.5 bg-slate-800 hover:bg-slate-700 text-slate-300 border border-slate-700 rounded-lg text-[11px] font-bold flex items-center gap-1.5"
                  >
                    <Plus className="w-3.5 h-3.5" /> Ajouter une ligne
                  </button>
                </div>
              </div>

              {/* Totaux en direct + blocage si desequilibre */}
              <div className="flex items-center justify-between text-xs font-mono bg-slate-950 border border-slate-800 rounded-xl px-4 py-3">
                <span className="text-slate-400">Total Débit : <b className="text-emerald-400">{totalDebitSaisie.toLocaleString()}</b></span>
                <span className="text-slate-400">Total Crédit : <b className="text-blue-400">{totalCreditSaisie.toLocaleString()}</b></span>
                <span className={`px-2.5 py-1 rounded-full font-bold flex items-center gap-1 ${pieceEquilibree ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20' : 'bg-red-500/10 text-red-400 border border-red-500/20'}`}>
                  {pieceEquilibree ? <CheckCircle2 className="w-3.5 h-3.5" /> : <AlertTriangle className="w-3.5 h-3.5" />}
                  {pieceEquilibree ? 'Équilibrée (D=C)' : `Écart : ${ecartSaisie.toLocaleString()} XAF`}
                </span>
              </div>
              {blocageSaisie && (
                <p className="text-[11px] text-amber-400 font-semibold flex items-center gap-1.5">
                  <AlertTriangle className="w-3.5 h-3.5" /> {blocageSaisie}
                </p>
              )}
              {comptes.length === 0 && (
                <p className="text-[11px] text-red-400 font-semibold">
                  Aucun compte chargé depuis /finance/plan-comptable — appliquez la migration de seed du plan SYSCOHADA côté backend.
                </p>
              )}

              <div className="pt-3 flex justify-end gap-2">
                <button
                  type="button"
                  onClick={() => setShowNewModal(false)}
                  className="px-4 py-2 bg-slate-800 text-slate-300 rounded-xl text-xs font-bold"
                >
                  Annuler
                </button>
                <button
                  type="submit"
                  disabled={Boolean(blocageSaisie) || saving || comptes.length === 0}
                  className="px-5 py-2 bg-violet-600 hover:bg-violet-500 disabled:opacity-40 disabled:cursor-not-allowed text-white rounded-xl text-xs font-bold shadow-lg flex items-center gap-2"
                >
                  {saving ? <Loader2 className="w-4 h-4 animate-spin" /> : <Check className="w-4 h-4" />}
                  Enregistrer la Piece
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* MODAL LETTRAGE */}
      {isLettrageModalOpen && (
        <div className="fixed inset-0 z-[100] bg-black/80 backdrop-blur-sm flex items-center justify-center p-4">
          <div className="bg-slate-900 border border-amber-500/40 rounded-3xl p-6 max-w-md w-full shadow-2xl space-y-4">
            <div className="flex items-center justify-between pb-3 border-b border-slate-800">
              <h3 className="text-base font-bold text-white flex items-center gap-2">
                <Layers className="w-5 h-5 text-amber-400" />
                Lettrage des Écritures Sélectionnées
              </h3>
              <button onClick={() => setIsLettrageModalOpen(false)} className="text-slate-400 hover:text-white p-1">
                <X className="w-5 h-5" />
              </button>
            </div>

            <p className="text-xs text-slate-300 leading-relaxed">
              Vous avez sélectionné <b>{selectedIds.length} écritures</b>. Veuillez confirmer le code de lettrage d&apos;apurement :
            </p>

            <div>
              <label className="block text-[11px] font-bold text-slate-300 uppercase mb-1">Code de Lettrage</label>
              <input
                type="text"
                value={lettrageCode}
                onChange={e => setLettrageCode(e.target.value.toUpperCase())}
                className="w-full h-10 px-3 bg-slate-950 border border-slate-800 rounded-xl text-xs text-amber-300 font-mono font-bold"
                required
              />
            </div>

            <div className="pt-2 flex items-center justify-between gap-2">
              <button
                type="button"
                onClick={handleRemoveLettrage}
                className="px-3 py-2 bg-red-500/20 text-red-400 border border-red-500/30 rounded-xl text-xs font-bold"
              >
                Délettrer
              </button>
              <div className="flex gap-2">
                <button
                  type="button"
                  onClick={() => setIsLettrageModalOpen(false)}
                  className="px-4 py-2 bg-slate-800 text-slate-300 rounded-xl text-xs font-bold"
                >
                  Annuler
                </button>
                <button
                  type="button"
                  onClick={handleApplyLettrage}
                  className="px-4 py-2 bg-amber-500 hover:bg-amber-400 text-slate-950 rounded-xl text-xs font-black shadow-lg"
                >
                  Valider le Lettrage
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
