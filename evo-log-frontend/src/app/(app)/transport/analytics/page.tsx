'use client';

import React, { useState, useEffect } from 'react';
import ModuleLayout from '@/components/layout/ModuleLayout';
import { AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, BarChart, Bar, Legend } from 'recharts';
import { financeAPI } from '@/lib/api-client';
import { PieChart, Activity, TrendingUp, DollarSign } from 'lucide-react';

export default function AnalyticsPage() {
  const [data, setData] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const loadData = async () => {
      try {
        const res = await financeAPI.getAnalyticsChartData();
        setData(res.data || res);
      } catch (e) {
        console.log("Erreur lors du chargement des analytiques");
      } finally {
        setLoading(false);
      }
    };
    loadData();
  }, []);

  return (
    <ModuleLayout module="transport">
      <div className="max-w-7xl mx-auto py-8 px-4 animate-in fade-in duration-500">
        
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-black text-slate-900 flex items-center gap-3">
            <PieChart className="w-8 h-8 text-blue-600" />
            EVO-Analytics (Business Intelligence)
          </h1>
          <p className="text-sm text-slate-500 mt-2">Vue consolidÃ©e des performances financiÃ¨res et opÃ©rationnelles.</p>
        </div>

        {/* KPIs */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
          <div className="bg-white p-6 rounded-2xl shadow-sm border border-slate-200">
            <div className="flex justify-between items-start">
              <h3 className="text-sm font-bold text-slate-500 uppercase">Chiffre d'Affaires</h3>
              <div className="p-2 bg-blue-50 text-blue-600 rounded-lg"><DollarSign className="w-5 h-5"/></div>
            </div>
            <p className="text-3xl font-black text-slate-800 mt-4 font-mono">19.5M</p>
            <p className="text-sm text-emerald-600 font-bold mt-2 flex items-center gap-1"><TrendingUp className="w-4 h-4"/> +14.5%</p>
          </div>
          <div className="bg-white p-6 rounded-2xl shadow-sm border border-slate-200">
            <div className="flex justify-between items-start">
              <h3 className="text-sm font-bold text-slate-500 uppercase">DÃ©penses OpÃ©rationnelles</h3>
              <div className="p-2 bg-rose-50 text-rose-600 rounded-lg"><Activity className="w-5 h-5"/></div>
            </div>
            <p className="text-3xl font-black text-slate-800 mt-4 font-mono">12.3M</p>
            <p className="text-sm text-rose-600 font-bold mt-2 flex items-center gap-1"><TrendingUp className="w-4 h-4"/> +5.2%</p>
          </div>
        </div>

        {/* Charts */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          
          {/* Evolution CA vs Depenses */}
          <div className="bg-white p-6 rounded-3xl shadow-sm border border-slate-200">
            <h3 className="text-lg font-bold text-slate-800 mb-6">Ã‰volution CA vs DÃ©penses</h3>
            <div className="h-80 w-full">
              {loading ? (
                <div className="h-full w-full bg-slate-50 rounded-xl animate-pulse"></div>
              ) : (
                <ResponsiveContainer width="100%" height="100%">
                  <AreaChart data={data} margin={{ top: 10, right: 30, left: 0, bottom: 0 }}>
                    <defs>
                      <linearGradient id="colorCA" x1="0" y1="0" x2="0" y2="1">
                        <stop offset="5%" stopColor="#2563eb" stopOpacity={0.3}/>
                        <stop offset="95%" stopColor="#2563eb" stopOpacity={0}/>
                      </linearGradient>
                      <linearGradient id="colorDepenses" x1="0" y1="0" x2="0" y2="1">
                        <stop offset="5%" stopColor="#ef4444" stopOpacity={0.3}/>
                        <stop offset="95%" stopColor="#ef4444" stopOpacity={0}/>
                      </linearGradient>
                    </defs>
                    <XAxis dataKey="name" axisLine={false} tickLine={false} tick={{fill: '#64748b', fontSize: 12}} dy={10} />
                    <YAxis axisLine={false} tickLine={false} tick={{fill: '#64748b', fontSize: 12}} />
                    <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#e2e8f0" />
                    <Tooltip contentStyle={{borderRadius: '12px', border: 'none', boxShadow: '0 10px 25px -5px rgba(0, 0, 0, 0.1)'}} />
                    <Legend />
                    <Area type="monotone" dataKey="CA" stroke="#2563eb" strokeWidth={3} fillOpacity={1} fill="url(#colorCA)" />
                    <Area type="monotone" dataKey="Depenses" stroke="#ef4444" strokeWidth={3} fillOpacity={1} fill="url(#colorDepenses)" />
                  </AreaChart>
                </ResponsiveContainer>
              )}
            </div>
          </div>

          {/* Marges par mois */}
          <div className="bg-white p-6 rounded-3xl shadow-sm border border-slate-200">
            <h3 className="text-lg font-bold text-slate-800 mb-6">Marge Nette (BÃ©nÃ©fice)</h3>
            <div className="h-80 w-full">
              {loading ? (
                <div className="h-full w-full bg-slate-50 rounded-xl animate-pulse"></div>
              ) : (
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart data={data} margin={{ top: 10, right: 30, left: 0, bottom: 0 }}>
                    <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#e2e8f0" />
                    <XAxis dataKey="name" axisLine={false} tickLine={false} tick={{fill: '#64748b', fontSize: 12}} dy={10} />
                    <YAxis axisLine={false} tickLine={false} tick={{fill: '#64748b', fontSize: 12}} />
                    <Tooltip cursor={{fill: '#f8fafc'}} contentStyle={{borderRadius: '12px', border: 'none', boxShadow: '0 10px 25px -5px rgba(0, 0, 0, 0.1)'}} />
                    <Legend />
                    <Bar dataKey="Marge" fill="#10b981" radius={[4, 4, 4, 4]} />
                  </BarChart>
                </ResponsiveContainer>
              )}
            </div>
          </div>

        </div>
      </div>
    </ModuleLayout>
  );
}
