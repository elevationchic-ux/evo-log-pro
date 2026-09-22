'use client';

import React, { useState, useEffect } from 'react';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/Card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import { financeAPI, masterDataAPI } from '@/lib/api-client';
import { Plus, CheckCircle, Search, CreditCard, RefreshCw } from 'lucide-react';
import { toast } from 'sonner';
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogFooter,
} from "@/components/ui/dialog";

export default function EncaissementsPage() {
  const [encaissements, setEncaissements] = useState<any[]>([]);
  const [factures, setFactures] = useState<any[]>([]);
  const [clients, setClients] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [isLettrageModalOpen, setIsLettrageModalOpen] = useState(false);
  const [selectedEncaissement, setSelectedEncaissement] = useState<any>(null);

  // Formulaire d'encaissement
  const [formData, setFormData] = useState({
    facture_id: '',
    tiers_id: '',
    mode_paiement: 'VIREMENT',
    reference_paiement: '',
    montant_encaisse: '',
    date_paiement: new Date().toISOString().split('T')[0],
    notes: ''
  });

  const [lettrageData, setLettrageData] = useState({
    facture_id: ''
  });

  const fetchData = async () => {
    setLoading(true);
    try {
      const [resEncaissements, resFactures, resClients] = await Promise.all([
        financeAPI.getEncaissements(),
        financeAPI.getFactures(),
        masterDataAPI.getTiers({ type_tiers: 'CLIENT' })
      ]);
      setEncaissements(resEncaissements.data);
      setFactures(resFactures.data);
      setClients(resClients.data);
    } catch (error) {
      toast.error('Erreur lors du chargement des données');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, []);

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const handleCreateEncaissement = async () => {
    try {
      const payload = {
        ...formData,
        facture_id: parseInt(formData.facture_id),
        tiers_id: formData.tiers_id ? parseInt(formData.tiers_id) : undefined,
        montant_encaisse: parseFloat(formData.montant_encaisse)
      };
      await financeAPI.enregistrerEncaissement(payload);
      toast.success('Paiement enregistré avec succès');
      setIsModalOpen(false);
      fetchData();
    } catch (error) {
      toast.error('Erreur lors de l\'enregistrement');
    }
  };

  const handleLettrer = async () => {
    if (!selectedEncaissement || !lettrageData.facture_id) return;
    try {
      await financeAPI.lettrerEncaissement(selectedEncaissement.id, parseInt(lettrageData.facture_id));
      toast.success('Paiement lettré avec succès');
      setIsLettrageModalOpen(false);
      fetchData();
    } catch (error) {
      toast.error('Erreur lors du lettrage');
    }
  };

  return (
    <div className="p-6 space-y-6 max-w-7xl mx-auto">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold tracking-tight text-gray-900">Encaissements & Règlements</h1>
          <p className="text-muted-foreground mt-1">Gérez les paiements clients et le lettrage comptable.</p>
        </div>
        <Button onClick={() => setIsModalOpen(true)}>
          <Plus className="w-4 h-4 mr-2" />
          Enregistrer un Paiement
        </Button>
      </div>

      {loading ? (
        <div className="flex justify-center h-32 items-center">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary"></div>
        </div>
      ) : (
        <Card className="border-t-4 border-t-primary">
          <CardContent className="p-0">
            <div className="overflow-x-auto">
              <table className="w-full text-sm text-left">
                <thead className="bg-slate-50 border-b text-gray-600">
                  <tr>
                    <th className="px-6 py-4 font-semibold">Référence / Mode</th>
                    <th className="px-6 py-4 font-semibold">Date</th>
                    <th className="px-6 py-4 font-semibold">Client</th>
                    <th className="px-6 py-4 font-semibold">Montant (XAF)</th>
                    <th className="px-6 py-4 font-semibold">Statut Lettrage</th>
                    <th className="px-6 py-4 font-semibold text-right">Actions</th>
                  </tr>
                </thead>
                <tbody className="divide-y">
                  {encaissements.map((enc) => (
                    <tr key={enc.id} className="hover:bg-slate-50 transition-colors">
                      <td className="px-6 py-4">
                        <div className="font-bold text-gray-900">{enc.reference || 'AUTO'}</div>
                        <div className="text-xs text-gray-500 mt-1 flex items-center">
                          <CreditCard className="w-3 h-3 mr-1" /> {enc.mode_paiement}
                        </div>
                        {enc.reference_paiement && (
                          <div className="text-xs text-gray-400">Réf: {enc.reference_paiement}</div>
                        )}
                      </td>
                      <td className="px-6 py-4 text-gray-600">
                        {new Date(enc.date_paiement || enc.created_at).toLocaleDateString()}
                      </td>
                      <td className="px-6 py-4">
                        <span className="font-medium">{enc.tiers?.raison_sociale || 'N/A'}</span>
                      </td>
                      <td className="px-6 py-4">
                        <span className="font-bold text-green-700 text-base">
                          {Number(enc.montant_encaisse).toLocaleString()}
                        </span>
                      </td>
                      <td className="px-6 py-4">
                        {enc.lettree ? (
                          <Badge className="bg-green-100 text-green-800 hover:bg-green-100 flex items-center w-fit">
                            <CheckCircle className="w-3 h-3 mr-1" /> Lettré
                          </Badge>
                        ) : (
                          <Badge variant="outline" className="text-amber-600 border-amber-300 bg-amber-50">
                            Non lettré
                          </Badge>
                        )}
                        {enc.lettree && enc.facture_id && (
                          <div className="text-xs text-gray-500 mt-1">Facture #{enc.facture_id}</div>
                        )}
                      </td>
                      <td className="px-6 py-4 text-right">
                        {!enc.lettree && (
                          <Button 
                            variant="outline" 
                            size="sm"
                            className="text-primary border-primary hover:bg-primary/10"
                            onClick={() => {
                              setSelectedEncaissement(enc);
                              setIsLettrageModalOpen(true);
                            }}
                          >
                            <RefreshCw className="w-3 h-3 mr-1" /> Lettrer
                          </Button>
                        )}
                      </td>
                    </tr>
                  ))}
                  {encaissements.length === 0 && (
                    <tr>
                      <td colSpan={6} className="px-6 py-12 text-center text-gray-500">
                        Aucun encaissement trouvé.
                      </td>
                    </tr>
                  )}
                </tbody>
              </table>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Modal d'enregistrement */}
      <Dialog open={isModalOpen} onOpenChange={setIsModalOpen}>
        <DialogContent className="max-w-md">
          <DialogHeader>
            <DialogTitle>Enregistrer un Paiement</DialogTitle>
          </DialogHeader>
          <div className="space-y-4 pt-4">
            <div>
              <label className="text-sm font-medium mb-1 block">Facture Associée (ID) *</label>
              <select 
                className="w-full flex h-10 rounded-md border border-input bg-background px-3 py-2 text-sm"
                name="facture_id" 
                value={formData.facture_id} 
                onChange={handleInputChange}
              >
                <option value="">Sélectionner une facture</option>
                {factures.map(f => (
                  <option key={f.id} value={f.id}>{f.numero_facture} - {f.montant_ttc_xaf?.toLocaleString()} XAF</option>
                ))}
              </select>
            </div>
            
            <div>
              <label className="text-sm font-medium mb-1 block">Client (Optionnel)</label>
              <select 
                className="w-full flex h-10 rounded-md border border-input bg-background px-3 py-2 text-sm"
                name="tiers_id" 
                value={formData.tiers_id} 
                onChange={handleInputChange}
              >
                <option value="">Sélectionner un client</option>
                {clients.map(c => (
                  <option key={c.id} value={c.id}>{c.raison_sociale}</option>
                ))}
              </select>
            </div>

            <div>
              <label className="text-sm font-medium mb-1 block">Mode de Paiement</label>
              <select 
                className="w-full flex h-10 rounded-md border border-input bg-background px-3 py-2 text-sm"
                name="mode_paiement" 
                value={formData.mode_paiement} 
                onChange={handleInputChange}
              >
                <option value="VIREMENT">Virement Bancaire</option>
                <option value="ESPECES">Espèces</option>
                <option value="MOBILE_MONEY">Mobile Money</option>
                <option value="CHEQUE">Chèque</option>
              </select>
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="text-sm font-medium mb-1 block">Montant Encaissé (XAF) *</label>
                <Input 
                  type="number" 
                  name="montant_encaisse" 
                  value={formData.montant_encaisse} 
                  onChange={handleInputChange} 
                  required
                />
              </div>
              <div>
                <label className="text-sm font-medium mb-1 block">Date</label>
                <Input 
                  type="date" 
                  name="date_paiement" 
                  value={formData.date_paiement} 
                  onChange={handleInputChange} 
                />
              </div>
            </div>

            <div>
              <label className="text-sm font-medium mb-1 block">Référence (Trx ID, N° Chèque)</label>
              <Input 
                name="reference_paiement" 
                value={formData.reference_paiement} 
                onChange={handleInputChange} 
                placeholder="Ex: TR123456789"
              />
            </div>
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={() => setIsModalOpen(false)}>Annuler</Button>
            <Button onClick={handleCreateEncaissement} disabled={!formData.facture_id || !formData.montant_encaisse}>
              Enregistrer
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* Modal de lettrage */}
      <Dialog open={isLettrageModalOpen} onOpenChange={setIsLettrageModalOpen}>
        <DialogContent className="max-w-sm">
          <DialogHeader>
            <DialogTitle>Lettrer un paiement</DialogTitle>
          </DialogHeader>
          <div className="py-4 space-y-4">
            <p className="text-sm text-gray-500">
              Associez ce paiement de <strong>{selectedEncaissement?.montant_encaisse?.toLocaleString()} XAF</strong> à une facture existante.
            </p>
            <div>
              <label className="text-sm font-medium mb-1 block">Sélectionner la facture</label>
              <select 
                className="w-full flex h-10 rounded-md border border-input bg-background px-3 py-2 text-sm"
                value={lettrageData.facture_id} 
                onChange={(e) => setLettrageData({ facture_id: e.target.value })}
              >
                <option value="">-- Choisir --</option>
                {factures.filter(f => f.statut !== 'PAYEE').map(f => (
                  <option key={f.id} value={f.id}>{f.numero_facture} ({f.montant_ttc_xaf?.toLocaleString()} XAF)</option>
                ))}
              </select>
            </div>
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={() => setIsLettrageModalOpen(false)}>Annuler</Button>
            <Button onClick={handleLettrer} disabled={!lettrageData.facture_id}>Confirmer le lettrage</Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
}
