'use client';

import { useEffect, useState } from 'react';
import { CalendarDays, RefreshCw, Users } from 'lucide-react';
import { rhAPI } from '@/lib/api-client';

type Employee = {
  id: number;
  matricule?: string | null;
  full_name: string;
  email: string;
  poste?: string | null;
  departement?: string | null;
  statut: string;
};

type Leave = {
  id: number;
  employe_id: number;
  type_conge: string;
  date_debut: string;
  date_fin: string;
  statut: string;
};

export default function RHDashboardPage() {
  const [employees, setEmployees] = useState<Employee[]>([]);
  const [leaves, setLeaves] = useState<Leave[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const load = async () => {
    setLoading(true);
    setError(null);
    try {
      const [employeesResponse, leavesResponse] = await Promise.all([
        rhAPI.getEmployes(),
        rhAPI.getConges(),
      ]);
      const employeeData = employeesResponse.data;
      const leaveData = leavesResponse.data;
      setEmployees(Array.isArray(employeeData) ? employeeData : employeeData?.items || []);
      setLeaves(Array.isArray(leaveData) ? leaveData : leaveData?.items || []);
    } catch (requestError: any) {
      setEmployees([]);
      setLeaves([]);
      setError(requestError?.response?.data?.detail || 'Impossible de charger les données RH.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    load();
  }, []);

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-black text-white flex items-center gap-2">
            <Users className="w-6 h-6 text-amber-400" /> Ressources humaines
          </h1>
          <p className="text-xs text-slate-400">Données de l’entreprise courante uniquement</p>
        </div>
        <button onClick={load} disabled={loading} className="px-3 py-2 rounded-lg border border-slate-700 text-slate-300 text-xs">
          <RefreshCw className={`w-4 h-4 inline mr-2 ${loading ? 'animate-spin' : ''}`} /> Actualiser
        </button>
      </div>
      {error && <div className="p-4 rounded-xl border border-red-500/30 bg-red-500/10 text-red-300 text-sm">{error}</div>}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div className="rounded-2xl border border-slate-800 bg-slate-900/80 p-5">
          <div className="text-xs text-slate-400">Employés actifs</div>
          <div className="text-3xl font-black text-white mt-2">{employees.length}</div>
        </div>
        <div className="rounded-2xl border border-slate-800 bg-slate-900/80 p-5">
          <div className="text-xs text-slate-400">Congés enregistrés</div>
          <div className="text-3xl font-black text-white mt-2">{leaves.length}</div>
        </div>
      </div>
      <div className="rounded-2xl border border-slate-800 bg-slate-900/80 overflow-hidden">
        <div className="p-4 border-b border-slate-800 flex items-center gap-2 text-slate-200 font-bold">
          <Users className="w-4 h-4 text-blue-400" /> Annuaire
        </div>
        {loading ? <div className="p-6 text-slate-400">Chargement...</div> : employees.length === 0 ? (
          <div className="p-6 text-slate-400">Aucun employé enregistré.</div>
        ) : (
          <div className="divide-y divide-slate-800">
            {employees.map(employee => (
              <div key={employee.id} className="p-4 grid grid-cols-1 md:grid-cols-5 gap-2 text-sm">
                <span className="text-white font-semibold">{employee.full_name}</span>
                <span className="text-slate-400">{employee.matricule || 'Matricule indisponible'}</span>
                <span className="text-slate-400">{employee.poste || 'Poste indisponible'}</span>
                <span className="text-slate-400">{employee.departement || 'Département indisponible'}</span>
                <span className="text-slate-300">{employee.statut}</span>
              </div>
            ))}
          </div>
        )}
      </div>
      <div className="rounded-2xl border border-slate-800 bg-slate-900/80 overflow-hidden">
        <div className="p-4 border-b border-slate-800 flex items-center gap-2 text-slate-200 font-bold">
          <CalendarDays className="w-4 h-4 text-emerald-400" /> Congés
        </div>
        {leaves.length === 0 ? <div className="p-6 text-slate-400">Aucune demande de congé enregistrée.</div> : (
          <div className="divide-y divide-slate-800">
            {leaves.map(leave => (
              <div key={leave.id} className="p-4 flex flex-wrap gap-3 text-sm text-slate-300">
                <span>Employé #{leave.employe_id}</span>
                <span>{leave.type_conge}</span>
                <span>{leave.date_debut} → {leave.date_fin}</span>
                <span>{leave.statut}</span>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
