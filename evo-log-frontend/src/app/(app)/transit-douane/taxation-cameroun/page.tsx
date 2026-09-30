'use client';

import React, { useEffect, useState } from 'react';
import {
  Calculator, Search, AlertTriangle, DollarSign, Info, Loader2, CheckCircle2,
} from 'lucide-react';
import { toast } from 'sonner';
import { apiClient } from '@/lib/api-client';
import { exportToCSV } from '@/lib/export';

// Position tarifaire renvoyee par /transit-avance/nomenclature-cemac (table reelle).
type NomenclaturePosition = {
  code_hs: string;
  description: string;
  taux_dd: number;   // fraction (0.20) ou pourcentage (20.0) selon l'import
  taux_tva: number;
  statut?: string;
  source_reference?: string | null;
};

// Resultat de la liquidation calculee par le moteur UNIQUE backend.
type TaxationResult = {
  valeur_cif_xaf: number;
  taux_dd: number;
  taux_tva: number;
  droit_douane_dd: number;
  redevance_informatique: number;
  cci_cemac: number;
  prelevement_ohada: number;
  base_tva: number;
  tva_1925: number;
  precompte_is: number;
  total_a_liquider_xaf: number;
  devise: string;
  regime: string;
  origine: string;
  source_taux: string;
  simulation: boolean;
  note: string;
};

// Libelle honnete de la provenance du taux, affiche dans le bandeau de resultat.
const SOURCE_LABELS: Record<string, { texte: string; cls: string }> = {
  nomenclature_cemac: { texte: 'Taux issu de la nomenclature CEMAC enregistrée en base', cls: 'text-emerald-400' },
  manuel: { texte: 'Taux saisi manuellement (aucune position SH trouvée en base)', cls: 'text-blue-400' },
  categorie_tec: { texte: 'Simulation basée sur la catégorie TEC sélectionnée', cls: 'text-amber-400' },
  defaut_simulation: { texte: 'Simulation — position SH absente de la nomenclature, taux par défaut (produit fini 20%) appliqué', cls: 'text-amber-400' },
  exoneration_origine: { texte: 'Droit de douane exonéré au titre de l’origine (CEMAC / ZLECAF)', cls: 'text-emerald-400' },
};

const xaf = (n: number) => `${Math.round(n).toLocaleString()} XAF`;
const pct = (taux: number) => `${(taux > 1 ? taux : taux * 100).toFixed(2).replace(/\.?0+$/, '')} %`;

export default function TransitDouaneTaxationPage() {
  const [hsQuery, setHsQuery] = useState('');
  const [positions, setPositions] = useState<NomenclaturePosition[]>([]);
  const [searching, setSearching] = useState(false);
  const [dropdownOpen, setDropdownOpen] = useState(false);
  const [selected, setSelected] = useState<NomenclaturePosition | null>(null);

  const [valeurFOB, setValeurFOB] = useState(0);
  const [fretsAssurances, setFretsAssurances] = useState(0);
  const [regime, setRegime] = useState('IM4');
  const [origine, setOrigine] = useState('HORS_ZONE');
  const [categorieTec, setCategorieTec] = useState('');
  const [tauxDDManuel, setTauxDDManuel] = useState('');

  const [result, setResult] = useState<TaxationResult | null>(null);
  const [computing, setComputing] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const valeurCIF = valeurFOB + fretsAssurances;

  // Recherche des positions tarifaires REELLES (aucun tarif code en dur ici).
  useEffect(() => {
    const term = hsQuery.trim();
    if (!term) { setPositions([]); return; }
    let cancelled = false;
    setSearching(true);
    const timer = setTimeout(async () => {
      try {
        const res = await apiClient.get('/api/v1/transit-avance/nomenclature-cemac', {
          params: { search: term, limite: 8 },
        });
        if (!cancelled) setPositions(Array.isArray(res.data) ? res.data : []);
      } catch {
        if (!cancelled) setPositions([]);
      } finally {
        if (!cancelled) setSearching(false);
      }
    }, 300);
    return () => { cancelled = true; clearTimeout(timer); };
  }, [hsQuery]);

  const choisirPosition = (p: NomenclaturePosition) => {
    setSelected(p);
    setHsQuery(p.code_hs);
    setDropdownOpen(false);
    setResult(null);
  };

  const calculer = async () => {
    const code = (selected?.code_hs || hsQuery).trim();
    if (!code) {
      setError('Renseignez au moins le code SH (position tarifaire) à simuler.');
      return;
    }
    if (valeurCIF <= 0) {
      setError('La valeur en douane (FOB + fret/assurance) doit être positive.');
      return;
    }
    setError(null);
    setComputing(true);
    try {
      const payload: Record<string, unknown> = {
        valeur_cif_xaf: valeurCIF,
        code_sh: code,
        regime,
        origine,
      };
      if (categorieTec !== '') payload.categorie_tec = parseInt(categorieTec, 10);
      if (tauxDDManuel) payload.taux_dd_explicite = parseFloat(tauxDDManuel);
      const res = await apiClient.post('/api/v1/transit-douane-avance/taxation/simuler', payload);
      setResult(res.data);
    } catch (e: any) {
      setResult(null);
      setError(e?.response?.data?.detail || 'Le calcul a échoué. Vérifiez les valeurs saisies.');
    } finally {
      setComputing(false);
    }
  };

  const exporter = () => {
    if (!result) return;
    exportToCSV([
      { poste: `Droit de Douane (${pct(result.taux_dd)})`, montant: Math.round(result.droit_douane_dd) },
      { poste: 'Redevance informatique (RID)', montant: Math.round(result.redevance_informatique) },
      { poste: 'Contribution Communautaire d’Intégration (CCI)', montant: Math.round(result.cci_cemac) },
      { poste: 'Prélèvement communautaire OHADA', montant: Math.round(result.prelevement_ohada) },
      { poste: `TVA (${pct(result.taux_tva)})`, montant: Math.round(result.tva_1925) },
      { poste: 'Précompte IS', montant: Math.round(result.precompte_is) },
      { poste: 'TOTAL À LIQUIDER', montant: Math.round(result.total_a_liquider_xaf) },
    ], `simulation-droits-${(selected?.code_hs || hsQuery).replace(/\./g, '-') || 'sh'}`);
    toast.success('Simulation exportée en CSV.');
  };

  const source = result ? SOURCE_LABELS[result.source_taux] : null;

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-black text-white">Calculateur Taxation Douanière CEMAC</h1>
        <p className="text-xs text-slate-400 mt-0.5">
          Simulation déléguée au moteur central des droits &amp; taxes (DD, RID, CCI, OHADA, TVA, précompte IS).
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Saisie */}
        <div className="bg-slate-900/80 border border-slate-800 rounded-2xl p-5 shadow-xl space-y-5">
          <h2 className="text-sm font-bold text-slate-200 flex items-center gap-2">
            <Calculator className="w-4 h-4 text-amber-400" /> Paramètres de la Déclaration
          </h2>

          {/* Recherche position SH (table reelle) */}
          <div className="relative">
            <label className="block text-xs font-bold text-slate-300 uppercase mb-1.5">Code SH / Position tarifaire CEMAC</label>
            <div className="relative">
              <Search className="w-4 h-4 absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" />
              <input
                type="text"
                value={hsQuery}
                onChange={e => { setHsQuery(e.target.value); setSelected(null); setDropdownOpen(true); }}
                onFocus={() => setDropdownOpen(true)}
                placeholder="Tapez un code SH (ex: 2710, 8471)…"
                className="w-full h-11 pl-9 pr-4 bg-slate-950 border border-slate-800 rounded-xl text-sm text-slate-100 placeholder-slate-500 focus:outline-none focus:border-amber-500 font-mono"
              />
            </div>
            {dropdownOpen && hsQuery.trim() && (
              <div className="absolute z-20 top-full left-0 right-0 mt-1 bg-slate-950 border border-slate-800 rounded-xl shadow-2xl overflow-hidden">
                {searching ? (
                  <div className="px-4 py-3 text-xs text-slate-500 flex items-center gap-2">
                    <Loader2 className="w-3.5 h-3.5 animate-spin" /> Recherche dans la nomenclature…
                  </div>
                ) : positions.length > 0 ? (
                  positions.map(p => (
                    <button
                      key={p.code_hs}
                      onClick={() => choisirPosition(p)}
                      className="w-full text-left px-4 py-3 hover:bg-slate-800 border-b border-slate-800/60 last:border-0 transition-colors"
                    >
                      <div className="text-xs font-mono font-bold text-amber-300">{p.code_hs}</div>
                      <div className="text-[11px] text-slate-400">{p.description}</div>
                      <div className="text-[11px] text-slate-500 mt-0.5">DD: {pct(p.taux_dd)} • TVA: {pct(p.taux_tva)}</div>
                    </button>
                  ))
                ) : (
                  <div className="px-4 py-3 text-[11px] text-slate-500">
                    Aucune position « {hsQuery.trim()} » dans la nomenclature CEMAC chargée en base.
                    Le calcul utilisera une hypothèse de simulation (catégorie TEC ou taux manuel ci-dessous).
                  </div>
                )}
              </div>
            )}
          </div>

          {selected && (
            <div className="bg-emerald-500/5 border border-emerald-500/20 rounded-xl p-3">
              <div className="text-[11px] text-emerald-400 font-mono">{selected.code_hs}</div>
              <div className="text-xs text-slate-300 font-medium">{selected.description}</div>
              {selected.source_reference && (
                <div className="text-[10px] text-slate-500 mt-0.5">Réf. : {selected.source_reference}</div>
              )}
            </div>
          )}

          {/* Valeurs */}
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-xs font-bold text-slate-300 uppercase mb-1.5">Valeur FOB (XAF)</label>
              <input
                type="number" min={0}
                value={valeurFOB || ''}
                onChange={e => setValeurFOB(parseFloat(e.target.value) || 0)}
                placeholder="Ex: 45 000 000"
                className="w-full h-11 px-4 bg-slate-950 border border-slate-800 rounded-xl text-sm text-slate-100 placeholder-slate-500 focus:outline-none focus:border-amber-500 font-mono"
              />
            </div>
            <div>
              <label className="block text-xs font-bold text-slate-300 uppercase mb-1.5">Fret + Assurance (XAF)</label>
              <input
                type="number" min={0}
                value={fretsAssurances || ''}
                onChange={e => setFretsAssurances(parseFloat(e.target.value) || 0)}
                placeholder="Ex: 3 500 000"
                className="w-full h-11 px-4 bg-slate-950 border border-slate-800 rounded-xl text-sm text-slate-100 placeholder-slate-500 focus:outline-none focus:border-amber-500 font-mono"
              />
            </div>
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-xs font-bold text-slate-300 uppercase mb-1.5">Régime douanier</label>
              <select
                value={regime}
                onChange={e => setRegime(e.target.value)}
                className="w-full h-11 px-4 bg-slate-950 border border-slate-800 rounded-xl text-sm text-slate-100 focus:outline-none focus:border-amber-500"
              >
                <option value="IM4">IM4 — Mise à la consommation</option>
                <option value="IM7">IM7 — Entrepôt (DD/TVA non liquidés)</option>
                <option value="T1">T1 — Transit (DD/TVA non liquidés)</option>
              </select>
            </div>
            <div>
              <label className="block text-xs font-bold text-slate-300 uppercase mb-1.5">Origine</label>
              <select
                value={origine}
                onChange={e => setOrigine(e.target.value)}
                className="w-full h-11 px-4 bg-slate-950 border border-slate-800 rounded-xl text-sm text-slate-100 focus:outline-none focus:border-amber-500"
              >
                <option value="HORS_ZONE">Hors zone (taxable)</option>
                <option value="CEMAC">CEMAC (DD exonéré)</option>
                <option value="ZLECAF">ZLECAF (DD exonéré)</option>
                <option value="UEAC">UEAC (DD exonéré)</option>
              </select>
            </div>
          </div>

          {/* Secours honnetes quand la position est absente de la nomenclature */}
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-xs font-bold text-slate-300 uppercase mb-1.5">Catégorie TEC (si SH absent)</label>
              <select
                value={categorieTec}
                onChange={e => setCategorieTec(e.target.value)}
                className="w-full h-11 px-4 bg-slate-950 border border-slate-800 rounded-xl text-sm text-slate-100 focus:outline-none focus:border-amber-500"
              >
                <option value="">Auto (défaut simulation)</option>
                <option value="0">Cat. 0 — 0 %</option>
                <option value="1">Cat. 1 — 5 %</option>
                <option value="2">Cat. 2 — 10 %</option>
                <option value="3">Cat. 3 — 20 %</option>
              </select>
            </div>
            <div>
              <label className="block text-xs font-bold text-slate-300 uppercase mb-1.5">Taux DD manuel (%)</label>
              <input
                type="number" min={0} max={100} step="0.01"
                value={tauxDDManuel}
                onChange={e => setTauxDDManuel(e.target.value)}
                placeholder="Prioritaire sur la catégorie"
                className="w-full h-11 px-4 bg-slate-950 border border-slate-800 rounded-xl text-sm text-slate-100 placeholder-slate-500 focus:outline-none focus:border-amber-500 font-mono"
              />
            </div>
          </div>

          <div className="p-3 bg-slate-950 border border-slate-800 rounded-xl">
            <div className="flex justify-between text-xs">
              <span className="text-slate-400">Valeur en douane (assiette CAF/CIF) =</span>
              <span className="font-mono font-black text-amber-300">{valeurCIF.toLocaleString()} XAF</span>
            </div>
          </div>

          {error && (
            <div className="flex items-start gap-2 text-xs text-red-400 bg-red-500/10 border border-red-500/20 rounded-xl p-3">
              <AlertTriangle className="w-4 h-4 shrink-0 mt-0.5" /> {error}
            </div>
          )}

          <button
            onClick={calculer}
            disabled={computing}
            className="w-full h-11 bg-amber-500 hover:bg-amber-400 disabled:opacity-60 text-slate-950 font-black text-sm rounded-xl transition-colors flex items-center justify-center gap-2"
          >
            {computing ? <><Loader2 className="w-4 h-4 animate-spin" /> Calcul…</> : 'Simuler la liquidation'}
          </button>
        </div>

        {/* Resultat */}
        <div className="bg-slate-900/80 border border-slate-800 rounded-2xl p-5 shadow-xl space-y-4">
          <h2 className="text-sm font-bold text-slate-200 flex items-center gap-2">
            <DollarSign className="w-4 h-4 text-emerald-400" /> Droits &amp; Taxes Calculés
          </h2>

          {result ? (
            <>
              <div className={`rounded-xl p-3 mb-1 border ${result.simulation ? 'bg-amber-500/5 border-amber-500/20' : 'bg-emerald-500/5 border-emerald-500/20'}`}>
                <div className="flex items-center gap-2">
                  {result.simulation
                    ? <AlertTriangle className="w-4 h-4 text-amber-400 shrink-0" />
                    : <CheckCircle2 className="w-4 h-4 text-emerald-400 shrink-0" />}
                  <span className={`text-[11px] font-bold ${source?.cls || 'text-slate-300'}`}>
                    {source?.texte || result.source_taux}
                  </span>
                </div>
                <p className="text-[10px] text-slate-500 mt-1">{result.note}</p>
              </div>

              <div className="space-y-2">
                {[
                  { label: `Droit de Douane (DD)  ${pct(result.taux_dd)}`, amount: result.droit_douane_dd, color: 'text-blue-400' },
                  { label: 'Redevance informatique (RID)', amount: result.redevance_informatique, color: 'text-sky-400' },
                  { label: 'Contribution Communautaire d’Intégration (CCI)', amount: result.cci_cemac, color: 'text-cyan-400' },
                  { label: 'Prélèvement communautaire OHADA', amount: result.prelevement_ohada, color: 'text-indigo-400' },
                  { label: `TVA (base ${xaf(result.base_tva)})  ${pct(result.taux_tva)}`, amount: result.tva_1925, color: 'text-amber-400' },
                  { label: 'Précompte IS', amount: result.precompte_is, color: 'text-purple-400' },
                ].map((t, i) => (
                  <div key={i} className="flex justify-between text-xs py-1.5 border-b border-slate-800/60">
                    <span className="text-slate-400">{t.label}</span>
                    <span className={`font-mono font-bold ${t.color}`}>{xaf(t.amount)}</span>
                  </div>
                ))}
              </div>

              <div className="bg-amber-500/10 border border-amber-500/30 rounded-2xl p-4 flex items-center justify-between mt-4">
                <div>
                  <div className="text-xs font-bold text-slate-300 uppercase">Total à liquider</div>
                  <div className="text-2xl font-black text-amber-300 font-mono mt-0.5">{xaf(result.total_a_liquider_xaf)}</div>
                  <div className="text-[11px] text-slate-400 mt-0.5">
                    Taux effectif global : {result.valeur_cif_xaf > 0 ? ((result.total_a_liquider_xaf / result.valeur_cif_xaf) * 100).toFixed(1) : '0'} % de la valeur en douane
                  </div>
                </div>
                <button
                  onClick={exporter}
                  className="px-4 py-2 bg-amber-500/20 hover:bg-amber-500/30 text-amber-300 font-bold text-xs rounded-xl border border-amber-500/30 transition-colors"
                >
                  Exporter CSV
                </button>
              </div>
            </>
          ) : (
            <div className="flex-1 flex flex-col items-center justify-center py-16 text-slate-500">
              <Calculator className="w-10 h-10 mb-3 opacity-30" />
              <p className="text-sm text-center max-w-xs">
                Renseignez le code SH et la valeur en douane, puis lancez la simulation pour obtenir les droits et taxes.
              </p>
            </div>
          )}
        </div>
      </div>

      {/* Notes legales */}
      <div className="p-4 bg-slate-900/60 border border-slate-800 rounded-xl">
        <p className="text-[11px] text-slate-500 flex items-start gap-2">
          <Info className="w-3.5 h-3.5 shrink-0 mt-0.5" />
          Simulation indicative produite par le moteur central de liquidation (formule CEMAC mutualisée). Les taux
          dépendent du tarif officiel en vigueur et de la nomenclature importée en base ; les droits définitifs sont
          liquidés par l’inspecteur des douanes via le visuel DGI/SYDONIA. EVO-LOG décline toute responsabilité en cas
          d’écart entre la simulation et la liquidation officielle.
        </p>
      </div>
    </div>
  );
}
