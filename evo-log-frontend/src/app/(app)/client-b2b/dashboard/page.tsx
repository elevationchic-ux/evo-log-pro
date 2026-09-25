'use client';

import React, { useState, useEffect } from 'react';
import {
  Users,
  Plus,
  Search,
  Filter,
  TrendingUp,
  DollarSign,
  CheckCircle2,
  Clock,
  FileText,
  ChevronRight,
  Briefcase,
  Layers,
  Phone,
  Mail,
  Building2,
  RefreshCw
} from 'lucide-react';
import { customerAPI } from '@/lib/api-client';
import { useRouter } from 'next/navigation';
import { toast } from 'sonner';

interface B2BOpportunity {
  id: string;
  nomEntreprise: string;
  contactNom: string;
  telephone: string;
  email: string;
  typeService: 'TRANSIT_DOUANE' | 'ACCONAGE_MANUTENTION' | 'TRANSPORT_CORRIDOR' | 'STOCKAGE_MAD';
  montantEstime: number;
  etape: 'PROSPECTION' | 'DEVIS_ENVOYE' | 'NEGOCIATION' | 'GAGNE' | 'PERDU';
  dateCreation: string;
  responsableCommercial: string;
}

export default function ClientB2bDashboardPage() {
  const router = useRouter();
  const [opportunities, setOpportunities] = useState<B2BOpportunity[]>([]);
  const [loading, setLoading] = useState(false);
  const [searchTerm, setSearchTerm] = useState('');
  const [stageFilter, setStageFilter] = useState('ALL');
  const [showAddModal, setShowAddModal] = useState(false);

  const [form, setForm] = useState({
    nomEntreprise: '',
    contactNom: '',
    telephone: '',
    email: '',
    typeService: 'TRANSIT_DOUANE',
    montantEstime: '',
    responsableCommercial: 'Équipe Commerciale CADC'
  });

  const loadData = async () => {
    setLoading(true);
    try {
      const res = await customerAPI.getCustomers({ limit: 50 });
      const raw = res.data?.items || res.data || [];
      if (Array.isArray(raw) && raw.length > 0) {
        setOpportunities(raw.filter((c: any) => c.id != null).map((c: any) => ({
          id: c.id.toString(),
          nomEntreprise: c.raison_sociale || c.nom || 'Importateur CEMAC',
          contactNom: c.contact_nom || 'Responsable Supply Chain',
          telephone: c.telephone || '+237 600 00 00 00',
          email: c.email || 'client@domain.cm',
          typeService: 'TRANSIT_DOUANE',
          montantEstime: Number(c.chiffre_affaires) || 15000000,
          etape: 'GAGNE',
          dateCreation: c.created_at || '2025-01-15',
          responsableCommercial: 'Direction Commerciale'
        })));
      } else {
        setOpportunities([]);
      }
    } catch (err) {
      console.warn('Customer API handled:', err);
      setOpportunities([]);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, []);

  const handleCreateOpportunity = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!form.nomEntreprise || !form.contactNom) {
      toast.error('Veuillez renseigner le nom de l\'entreprise et du contact.');
      return;
    }

    try {
      await customerAPI.createCustomer({
        raison_sociale: form.nomEntreprise,
        contact_nom: form.contactNom,
        telephone: form.telephone || undefined,
        email: form.email || undefined,
        type_service: form.typeService,
        budget_estime: form.montantEstime ? Number(form.montantEstime) : undefined,
      });
      toast.success(`Prospect « ${form.nomEntreprise} » ajouté au pipeline.`);
      setShowAddModal(false);
      setForm({ nomEntreprise: '', contactNom: '', telephone: '', email: '', typeService: 'TRANSIT_DOUANE', montantEstime: '', responsableCommercial: 'Équipe Commerciale CADC' });
      loadData();
    } catch (err: any) {
      toast.error(err?.response?.data?.detail || 'Erreur  prospect non enregistré.');
    }
  };

  const filteredOpps = opportunities.filter(o => {
    const matchesSearch =
      o.nomEntreprise.toLowerCase().includes(searchTerm.toLowerCase()) ||
      o.contactNom.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesStage = stageFilter === 'ALL' || o.etape === stageFilter;
    return matchesSearch && matchesStage;
  });

  const totalPipeline = opportunities.reduce((sum, o) => sum + o.montantEstime, 0);

  return (
    <div className="p-4 sm:p-6 lg:p-8 max-w-7xl mx-auto space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-outline pb-5">
        <div className="flex items-center gap-3">
          <div className="p-2.5 bg-primary/10 rounded-xl text-primary">
            <Briefcase className="w-6 h-6" />
          </div>
          <div>
            <h1 className="text-2xl font-bold text-on-surface">CRM B2B & Pipeline Commercial</h1>
            <p className="text-sm text-on-surface-variant">
              Prospection, cotations tarifaires et suivi des comptes chargeurs & importateurs CEMAC
            </p>
          </div>
        </div>

        <button
          onClick={() => setShowAddModal(true)}
          className="flex items-center gap-2 px-4 py-2 text-xs font-semibold rounded-xl bg-primary text-on-primary hover:opacity-95 transition-opacity"
        >
          <Plus className="w-4 h-4" />
          Nouveau Prospect Commercial
        </button>
      </div>

      {/* KPI Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <div className="bg-surface border border-outline rounded-2xl p-4 flex items-center justify-between">
          <div>
            <p className="text-xs text-on-surface-variant font-medium">Valeur Pipeline B2B</p>
            <p className="text-xl font-bold font-mono text-on-surface mt-1">{totalPipeline.toLocaleString('fr-FR')} FCFA</p>
            <span className="text-[10px] text-on-surface-variant">Opportunités actives</span>
          </div>
          <div className="p-3 bg-primary/10 rounded-xl text-primary">
            <DollarSign className="w-5 h-5" />
          </div>
        </div>

        <div className="bg-surface border border-outline rounded-2xl p-4 flex items-center justify-between">
          <div>
            <p className="text-xs text-on-surface-variant font-medium">Prospects en Cours</p>
            <p className="text-xl font-bold font-mono text-on-surface mt-1">{opportunities.length}</p>
            <span className="text-[10px] text-on-surface-variant">Importateurs / Chargeurs</span>
          </div>
          <div className="p-3 bg-blue-500/10 rounded-xl text-blue-500">
            <Users className="w-5 h-5" />
          </div>
        </div>

        <div className="bg-surface border border-outline rounded-2xl p-4 flex items-center justify-between">
          <div>
            <p className="text-xs text-on-surface-variant font-medium">Contrats Signés</p>
            <p className="text-xl font-bold font-mono text-emerald-600 mt-1">
              {opportunities.filter(o => o.etape === 'GAGNE').length}
            </p>
            <span className="text-[10px] text-on-surface-variant">Accords cadres logistiques</span>
          </div>
          <div className="p-3 bg-emerald-500/10 rounded-xl text-emerald-500">
            <CheckCircle2 className="w-5 h-5" />
          </div>
        </div>

        <div className="bg-surface border border-outline rounded-2xl p-4 flex items-center justify-between">
          <div>
            <p className="text-xs text-on-surface-variant font-medium">Taux de Conversion</p>
            <p className="text-xl font-bold font-mono text-emerald-600 mt-1">
              {opportunities.length > 0 ? Math.round((opportunities.filter(o => o.etape === 'GAGNE').length / opportunities.length) * 100) : 0}%
            </p>
            <span className="text-[10px] text-on-surface-variant">Devis convertis en missions</span>
          </div>
          <div className="p-3 bg-emerald-500/10 rounded-xl text-emerald-500">
            <TrendingUp className="w-5 h-5" />
          </div>
        </div>
      </div>

      {/* Filter Bar */}
      <div className="bg-surface border border-outline rounded-2xl p-4 flex flex-wrap items-center justify-between gap-4">
        <div className="relative flex-1 min-w-[240px]">
          <Search className="w-4 h-4 absolute left-3 top-1/2 -translate-y-1/2 text-on-surface-variant" />
          <input
            type="text"
            placeholder="Rechercher par raison sociale, contact..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="w-full pl-9 pr-4 py-2 bg-surface-container-low border border-outline text-xs rounded-xl text-on-surface focus:outline-none focus:border-primary"
          />
        </div>

        <div className="flex items-center gap-3">
          <select
            value={stageFilter}
            onChange={(e) => setStageFilter(e.target.value)}
            className="bg-surface-container-low border border-outline text-xs rounded-xl px-3 py-2 text-on-surface focus:outline-none focus:border-primary"
          >
            <option value="ALL">Toutes les étapes du cycle de vente</option>
            <option value="PROSPECTION">Prospection Initiale</option>
            <option value="DEVIS_ENVOYE">Cotation / Devis Transmis</option>
            <option value="NEGOCIATION">Négociation Tarifaire</option>
            <option value="GAGNE">Gagné / Contrat Actif</option>
            <option value="PERDU">Perdu / Sans Suite</option>
          </select>

          <button
            onClick={loadData}
            className="p-2 border border-outline rounded-xl hover:bg-surface-container text-on-surface-variant hover:text-on-surface"
            title="Actualiser"
          >
            <RefreshCw className={`w-3.5 h-3.5 ${loading ? 'animate-spin' : ''}`} />
          </button>
        </div>
      </div>

      {/* Grid or Clean Slate State */}
      {filteredOpps.length === 0 ? (
        <div className="bg-surface border border-outline rounded-2xl p-12 text-center shadow-sm">
          <Briefcase className="w-12 h-12 text-on-surface-variant/40 mx-auto mb-3" />
          <h3 className="font-semibold text-on-surface text-base">Aucun prospect ou compte B2B dans le pipeline</h3>
          <p className="text-xs text-on-surface-variant mt-1 max-w-md mx-auto mb-4">
            Enregistrez les importateurs, exportateurs et industriels de la sous-région pour gérer vos cotations, contrats de transit et conventions tarifaires.
          </p>
          <button
            onClick={() => setShowAddModal(true)}
            className="px-4 py-2 bg-primary text-on-primary rounded-xl font-bold text-xs hover:opacity-95"
          >
            + Enregistrer le Premier Prospect
          </button>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {filteredOpps.map(opp => (
            <div
              key={opp.id}
              className="bg-surface border border-outline rounded-2xl p-5 hover:border-primary transition-all shadow-sm space-y-3"
            >
              <div className="flex justify-between items-start">
                <div>
                  <span className="text-[10px] font-bold text-primary uppercase">{opp.typeService.replace(/_/g, ' ')}</span>
                  <h3 className="font-bold text-base text-on-surface">{opp.nomEntreprise}</h3>
                </div>
                <span className={`px-2.5 py-0.5 rounded-full text-[10px] font-bold ${opp.etape === 'GAGNE' ? 'bg-emerald-500/10 text-emerald-600' :
                    opp.etape === 'NEGOCIATION' ? 'bg-blue-500/10 text-blue-600' :
                      opp.etape === 'DEVIS_ENVOYE' ? 'bg-amber-500/10 text-amber-600' :
                        'bg-surface-container text-on-surface-variant'
                  }`}>
                  {opp.etape}
                </span>
              </div>

              <div className="space-y-1 text-xs text-on-surface-variant">
                <div className="flex items-center gap-1.5">
                  <Users className="w-3.5 h-3.5" />
                  <span className="text-on-surface font-medium">{opp.contactNom}</span>
                </div>
                {opp.telephone && (
                  <div className="flex items-center gap-1.5">
                    <Phone className="w-3.5 h-3.5" />
                    <span>{opp.telephone}</span>
                  </div>
                )}
                {opp.email && (
                  <div className="flex items-center gap-1.5">
                    <Mail className="w-3.5 h-3.5" />
                    <span>{opp.email}</span>
                  </div>
                )}
              </div>

              <div className="pt-2 border-t border-outline/50 flex justify-between items-center">
                <div>
                  <span className="text-[10px] text-on-surface-variant block">Volume Estimé :</span>
                  <span className="font-mono font-bold text-sm text-primary">
                    {opp.montantEstime.toLocaleString('fr-FR')} FCFA
                  </span>
                </div>
                <button
                  onClick={() => router.push(`/client-b2b/crm?client=${opp.id}`)}
                  className="p-2 hover:bg-surface-container rounded-lg text-primary"
                >
                  <ChevronRight className="w-4 h-4" />
                </button>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Add Modal */}
      {showAddModal && (
        <div className="fixed inset-0 z-50 bg-black/50 backdrop-blur-sm flex items-center justify-center p-4">
          <div className="bg-surface border border-outline rounded-2xl w-full max-w-md p-6 space-y-4 shadow-xl">
            <div className="flex justify-between items-center border-b border-outline pb-3">
              <h3 className="font-bold text-on-surface text-base">Nouveau Prospect / Compte B2B</h3>
              <button onClick={() => setShowAddModal(false)} className="text-on-surface-variant hover:text-on-surface">✕</button>
            </div>

            <form onSubmit={handleCreateOpportunity} className="space-y-3 text-xs">
              <div>
                <label className="block text-on-surface-variant font-medium mb-1">Raison Sociale de l'Entreprise * :</label>
                <input
                  type="text"
                  placeholder="Ex: SOCAVER SA / CICAM"
                  value={form.nomEntreprise}
                  onChange={(e) => setForm({ ...form, nomEntreprise: e.target.value })}
                  required
                  className="w-full p-2 bg-surface-container-low border border-outline rounded-xl text-on-surface font-semibold focus:outline-none focus:border-primary"
                />
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-on-surface-variant font-medium mb-1">Nom du Contact * :</label>
                  <input
                    type="text"
                    placeholder="Ex: Paul Mbarga"
                    value={form.contactNom}
                    onChange={(e) => setForm({ ...form, contactNom: e.target.value })}
                    required
                    className="w-full p-2 bg-surface-container-low border border-outline rounded-xl text-on-surface focus:outline-none focus:border-primary"
                  />
                </div>
                <div>
                  <label className="block text-on-surface-variant font-medium mb-1">Téléphone :</label>
                  <input
                    type="tel"
                    placeholder="+237 6..."
                    value={form.telephone}
                    onChange={(e) => setForm({ ...form, telephone: e.target.value })}
                    className="w-full p-2 bg-surface-container-low border border-outline rounded-xl text-on-surface focus:outline-none focus:border-primary"
                  />
                </div>
              </div>

              <div>
                <label className="block text-on-surface-variant font-medium mb-1">Email Professionnel :</label>
                <input
                  type="email"
                  placeholder="contact@entreprise.cm"
                  value={form.email}
                  onChange={(e) => setForm({ ...form, email: e.target.value })}
                  className="w-full p-2 bg-surface-container-low border border-outline rounded-xl text-on-surface focus:outline-none focus:border-primary"
                />
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-on-surface-variant font-medium mb-1">Service Principal Demandé :</label>
                  <select
                    value={form.typeService}
                    onChange={(e) => setForm({ ...form, typeService: e.target.value })}
                    className="w-full p-2 bg-surface-container-low border border-outline rounded-xl text-on-surface focus:outline-none focus:border-primary"
                  >
                    <option value="TRANSIT_DOUANE">Transit & Dédouanement</option>
                    <option value="ACCONAGE_MANUTENTION">Acconage Portuaire</option>
                    <option value="TRANSPORT_CORRIDOR">Transport Corridor CEMAC</option>
                    <option value="STOCKAGE_MAD">Entrepôt Logistique MAD</option>
                  </select>
                </div>
                <div>
                  <label className="block text-on-surface-variant font-medium mb-1">Budget Estimé (FCFA) :</label>
                  <input
                    type="number"
                    placeholder="Ex: 25000000"
                    value={form.montantEstime}
                    onChange={(e) => setForm({ ...form, montantEstime: e.target.value })}
                    className="w-full p-2 bg-surface-container-low border border-outline rounded-xl text-on-surface font-mono focus:outline-none focus:border-primary"
                  />
                </div>
              </div>

              <div className="pt-3 flex justify-end gap-2">
                <button
                  type="button"
                  onClick={() => setShowAddModal(false)}
                  className="px-4 py-2 border border-outline rounded-xl text-on-surface hover:bg-surface-container font-semibold"
                >
                  Annuler
                </button>
                <button
                  type="submit"
                  className="px-4 py-2 bg-primary text-on-primary rounded-xl font-bold hover:opacity-90"
                >
                  Ajouter au CRM
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}