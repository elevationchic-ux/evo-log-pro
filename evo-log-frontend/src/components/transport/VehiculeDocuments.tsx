'use client';

import React from 'react';
import { FileText, Download, Eye } from 'lucide-react';

interface Document {
  id: string;
  name: string;
  type: string;
  date: string;
  status: 'valide' | 'expire' | 'bientot_expire';
}

interface VehiculeDocumentsProps {
  vehiculeId: string;
  documents?: Document[];
}

export default function VehiculeDocuments({ documents = [] }: VehiculeDocumentsProps) {
  const statusColors = {
    valide: 'bg-green-500/15 text-green-300',
    expire: 'bg-red-500/15 text-red-300',
    bientot_expire: 'bg-yellow-500/15 text-yellow-300',
  };

  return (
    <div className="bg-slate-900 rounded-xl border border-slate-700 p-6">
      <h3 className="text-lg font-semibold text-slate-100 mb-4 flex items-center gap-2">
        <FileText className="w-5 h-5 text-blue-600" />
        Documents du vehicule
      </h3>
      {documents.length === 0 ? (
        <p className="text-sm text-slate-400 text-center py-8">Aucun document disponible</p>
      ) : (
        <div className="space-y-3">
          {documents.map(doc => (
            <div key={doc.id} className="flex items-center justify-between p-3 bg-slate-800 rounded-lg">
              <div className="flex items-center gap-3">
                <FileText className="w-5 h-5 text-gray-400" />
                <div>
                  <p className="text-sm font-medium text-slate-100">{doc.name}</p>
                  <p className="text-xs text-slate-400">{doc.date}</p>
                </div>
              </div>
              <div className="flex items-center gap-2">
                <span className={`px-2 py-0.5 rounded-full text-xs font-medium ${statusColors[doc.status]}`}>{doc.status}</span>
                <button className="p-1 hover:bg-slate-700 rounded"><Eye className="w-4 h-4 text-slate-400" /></button>
                <button className="p-1 hover:bg-slate-700 rounded"><Download className="w-4 h-4 text-slate-400" /></button>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}