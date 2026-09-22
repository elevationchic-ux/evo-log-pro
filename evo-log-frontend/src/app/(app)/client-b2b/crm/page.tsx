'use client';

import React, { useState, useEffect } from 'react';
import { 
  Users, 
  Plus, 
  Search, 
  Filter, 
  Phone, 
  Mail, 
  MapPin, 
  Building2, 
  Star, 
  Clock, 
  Calendar,
  MessageSquare
} from 'lucide-react';
import { customerAPI } from '@/lib/api-client';
import { toast } from 'sonner';

interface B2BContact {
  id: string;
  nomEntreprise: string;
  contactNom: string;
  poste: string;
  telephone: string;
  email: string;
  ville: string;
  pays: string;
  noteSla: number;
  dernierEchange: string;
}

export default function ClientB2bCrmPage() {
  const [contacts, setContacts] = useState<B2BContact[]>([]);
  const [loading, setLoading] = useState(false);
  const [searchTerm, setSearchTerm] = useState('');
  const [showAddModal, setShowAddModal] = useState(false);

  const [form, setForm] = useState({
    nomEntreprise: '',
    contactNom: '',
    poste: 'Directeur Logistique / Supply Chain',
    telephone: '',
    email: '',
    ville: 'Douala',
    pays: 'Cameroun'
  });

  const loadContacts = async () => {
    setLoading(true);
    try {
      const res = await customerAPI.getCustomers({ limit: 50 });
      const raw = res.data?.items || res.data || [];
      if (Array.isArray(raw) && raw.length > 0) {
        setContacts(raw.map((c: any) => ({
          id: c.id?.toString() || Math.random().toString(),
          nomEntreprise: c.raison_sociale || c.nom || 'Client Partenaire',
          contactNom: c.contact_nom || 'Responsable Expéditions',
          poste: c.poste || 'Directeur des Opérations',
          telephone: c.telephone || '+237 233 00 00 00',
          email: c.email || 'contact@client.cm',
          ville: c.ville || 'Douala',
          pays: c.pays || 'Cameroun',
          noteSla: 5,
          dernierEchange: 'Récemment'
        })));
      } else {
        setContacts([]);
      }
    } catch (err) {
      console.warn('Contacts load handled:', err);
      setContacts([]);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadContacts();
  }, []);

  const handleCreateContact = (e: React.FormEvent) => {
    e.preventDefault();
    if (!form.nomEntreprise || !form.contactNom) {
      toast.error('Veuillez renseigner l\'entreprise et le nom du contact.');
      return;
    }

    const created: B2BContact = {
      id: Date.now().toString(),
      nomEntreprise: form.nomEntreprise,
      contactNom: form.contactNom,
      poste: form.poste,
      telephone: form.telephone,
      email: form.email,
      ville: form.ville,
      pays: form.pays,
      noteSla: 5,
      dernierEchange: 'Aujourd\'hui'
    };

    setContacts([created, ...contacts]);
    setShowAddModal(false);
    setForm({
      nomEntreprise: '',
      contactNom: '',
      poste: 'Directeur Logistique / Supply Chain',
      telephone: '',
      email: '',
      ville: 'Douala',
      pays: 'Cameroun'
    });
    toast.error("L'ajout de contacts CRM n'est pas encore raccordé à l'API.");
  };

  const filteredContacts = contacts.filter(c => 
    c.nomEntreprise.toLowerCase().includes(searchTerm.toLowerCase()) ||
    c.contactNom.toLowerCase().includes(searchTerm.toLowerCase())
  );

  return (
    <div className="p-4 sm:p-6 lg:p-8 max-w-7xl mx-auto space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-outline pb-5">
        <div className="flex items-center gap-3">
          <div className="p-2.5 bg-primary/10 rounded-xl text-primary">
            <Users className="w-6 h-6" />
          </div>
          <div>
            <h1 className="text-2xl font-bold text-on-surface">Annuaire CRM & Fiches Interlocuteurs B2B</h1>
            <p className="text-sm text-on-surface-variant">
              Coordonnées directes des décideurs supply chain, transitaires délégués et responsables comptables
            </p>
          </div>
        </div>

        <button
          onClick={() => setShowAddModal(true)}
          className="flex items-center gap-2 px-4 py-2 text-xs font-semibold rounded-xl bg-primary text-on-primary hover:opacity-95 transition-opacity"
        >
          <Plus className="w-4 h-4" />
          Nouveau Contact Décideur
        </button>
      </div>

      {/* Filter Bar */}
      <div className="bg-surface border border-outline rounded-2xl p-4 flex flex-wrap items-center justify-between gap-4">
        <div className="relative flex-1 min-w-[240px]">
          <Search className="w-4 h-4 absolute left-3 top-1/2 -translate-y-1/2 text-on-surface-variant" />
          <input
            type="text"
            placeholder="Rechercher par nom de contact ou entreprise..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="w-full pl-9 pr-4 py-2 bg-surface-container-low border border-outline text-xs rounded-xl text-on-surface focus:outline-none focus:border-primary"
          />
        </div>
      </div>

      {/* Contact Cards / Clean Slate State */}
      {filteredContacts.length === 0 ? (
        <div className="bg-surface border border-outline rounded-2xl p-12 text-center shadow-sm">
          <Users className="w-12 h-12 text-on-surface-variant/40 mx-auto mb-3" />
          <h3 className="font-semibold text-on-surface text-base">Aucun contact client répertorié</h3>
          <p className="text-xs text-on-surface-variant mt-1 max-w-md mx-auto mb-4">
            Alimentez votre carnet d'adresses B2B avec les coordonnées directes des directeurs supply chain et responsables achats de vos clients chargeurs.
          </p>
          <button
            onClick={() => setShowAddModal(true)}
            className="px-4 py-2 bg-primary text-on-primary rounded-xl font-bold text-xs hover:opacity-95"
          >
            + Enregistrer le Premier Interlocuteur
          </button>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {filteredContacts.map(c => (
            <div
              key={c.id}
              className="bg-surface border border-outline rounded-2xl p-5 hover:border-primary transition-all shadow-sm space-y-3"
            >
              <div className="flex justify-between items-start">
                <div>
                  <h3 className="font-bold text-base text-on-surface">{c.contactNom}</h3>
                  <span className="text-xs text-primary font-semibold block">{c.poste}</span>
                  <span className="text-xs text-on-surface-variant font-medium">{c.nomEntreprise}</span>
                </div>
                <div className="flex items-center gap-0.5 text-amber-500">
                  <Star className="w-3.5 h-3.5 fill-current" />
                  <span className="text-xs font-bold font-mono">{c.noteSla}.0</span>
                </div>
              </div>

              <div className="space-y-1.5 text-xs text-on-surface-variant pt-2 border-t border-outline/40">
                {c.telephone && (
                  <div className="flex items-center gap-2">
                    <Phone className="w-3.5 h-3.5 text-on-surface-variant" />
                    <span className="text-on-surface font-mono">{c.telephone}</span>
                  </div>
                )}
                {c.email && (
                  <div className="flex items-center gap-2">
                    <Mail className="w-3.5 h-3.5 text-on-surface-variant" />
                    <span className="text-on-surface">{c.email}</span>
                  </div>
                )}
                <div className="flex items-center gap-2">
                  <MapPin className="w-3.5 h-3.5 text-on-surface-variant" />
                  <span>{c.ville}, {c.pays}</span>
                </div>
              </div>

              <div className="pt-2 border-t border-outline/50 flex justify-between items-center text-[11px] text-on-surface-variant">
                <span>Dernier échange : <strong className="text-on-surface">{c.dernierEchange}</strong></span>
                <button
                  onClick={() => toast.error("L'ouverture du journal d'appel n'est pas encore raccordée à l'API.")}
                  className="text-primary hover:underline font-bold"
                >
                  Contacter
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
              <h3 className="font-bold text-on-surface text-base">Nouveau Contact Décideur B2B</h3>
              <button onClick={() => setShowAddModal(false)} className="text-on-surface-variant hover:text-on-surface">✕</button>
            </div>

            <form onSubmit={handleCreateContact} className="space-y-3 text-xs">
              <div>
                <label className="block text-on-surface-variant font-medium mb-1">Raison Sociale de l'Entreprise * :</label>
                <input
                  type="text"
                  placeholder="Ex: CIMENCAM / ALUCAM"
                  value={form.nomEntreprise}
                  onChange={(e) => setForm({ ...form, nomEntreprise: e.target.value })}
                  required
                  className="w-full p-2 bg-surface-container-low border border-outline rounded-xl text-on-surface font-semibold focus:outline-none focus:border-primary"
                />
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-on-surface-variant font-medium mb-1">Nom & Prénom * :</label>
                  <input
                    type="text"
                    placeholder="Ex: François Nguema"
                    value={form.contactNom}
                    onChange={(e) => setForm({ ...form, contactNom: e.target.value })}
                    required
                    className="w-full p-2 bg-surface-container-low border border-outline rounded-xl text-on-surface focus:outline-none focus:border-primary"
                  />
                </div>
                <div>
                  <label className="block text-on-surface-variant font-medium mb-1">Fonction / Poste :</label>
                  <input
                    type="text"
                    placeholder="Ex: Responsable Import-Export"
                    value={form.poste}
                    onChange={(e) => setForm({ ...form, poste: e.target.value })}
                    className="w-full p-2 bg-surface-container-low border border-outline rounded-xl text-on-surface focus:outline-none focus:border-primary"
                  />
                </div>
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-on-surface-variant font-medium mb-1">Téléphone Direct :</label>
                  <input
                    type="tel"
                    placeholder="+237 6..."
                    value={form.telephone}
                    onChange={(e) => setForm({ ...form, telephone: e.target.value })}
                    className="w-full p-2 bg-surface-container-low border border-outline rounded-xl text-on-surface focus:outline-none focus:border-primary"
                  />
                </div>
                <div>
                  <label className="block text-on-surface-variant font-medium mb-1">Email Pro :</label>
                  <input
                    type="email"
                    placeholder="nom@entreprise.cm"
                    value={form.email}
                    onChange={(e) => setForm({ ...form, email: e.target.value })}
                    className="w-full p-2 bg-surface-container-low border border-outline rounded-xl text-on-surface focus:outline-none focus:border-primary"
                  />
                </div>
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-on-surface-variant font-medium mb-1">Ville :</label>
                  <input
                    type="text"
                    value={form.ville}
                    onChange={(e) => setForm({ ...form, ville: e.target.value })}
                    className="w-full p-2 bg-surface-container-low border border-outline rounded-xl text-on-surface focus:outline-none focus:border-primary"
                  />
                </div>
                <div>
                  <label className="block text-on-surface-variant font-medium mb-1">Pays :</label>
                  <input
                    type="text"
                    value={form.pays}
                    onChange={(e) => setForm({ ...form, pays: e.target.value })}
                    className="w-full p-2 bg-surface-container-low border border-outline rounded-xl text-on-surface focus:outline-none focus:border-primary"
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
                  Enregistrer Contact
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
