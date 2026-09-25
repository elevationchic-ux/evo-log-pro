'use client';

import React, { useState, useEffect } from 'react';
import { Building2, ShieldCheck, Phone, Mail, MapPin, Globe } from 'lucide-react';
import { apiClient } from '@/lib/api-client';

export interface CompanyInfo {
  raison_sociale: string;
  sigle?: string;
  forme_juridique?: string;
  capital_social?: string;
  nif?: string;
  rccm?: string;
  agrement_douane?: string;
  agrement_pad?: string;
  agrement_pak?: string;
  adresse?: string;
  ville?: string;
  pays?: string;
  telephone?: string;
  email?: string;
  site_web?: string;
  logo_url?: string;
  rib?: string;
}

interface CompanyDocumentHeaderProps {
  documentTitle: string;
  documentNumber: string;
  documentDate?: string;
  documentReference?: string;
  companyOverride?: Partial<CompanyInfo>;
}

export function CompanyDocumentHeader({
  documentTitle,
  documentNumber,
  documentDate,
  documentReference,
  companyOverride
}: CompanyDocumentHeaderProps) {
  const [company, setCompany] = useState<CompanyInfo>({
    raison_sociale: 'EVO-LOGISTICS & TRANSIT CEMAC SA',
    sigle: 'EVO-LOG',
    forme_juridique: 'Société Anonyme',
    capital_social: '100 000 000 FCFA',
    nif: 'M010200034567P',
    rccm: 'RC/DLA/2019/B/890',
    agrement_douane: 'DEC-DGD-2021/045',
    agrement_pad: 'PAD-ACC-2022/88',
    agrement_pak: 'PAK-TRANSIT-2023/12',
    adresse: 'Zone Portuaire, Boulevard Leclerc',
    ville: 'Douala',
    pays: 'Cameroun',
    telephone: '+237 233 42 00 00',
    email: 'direction@evo-logistics.cm',
    site_web: 'https://evo-logistics.cm',
    rib: '10019 02345 01234567890 45'
  });

  useEffect(() => {
    apiClient.get('/api/v1/tenant/company-profile')
      .then(res => {
        if (res.data) {
          setCompany(prev => ({ ...prev, ...res.data }));
        }
      })
      .catch(() => {
        // Keeps default corporate setup if remote is quiet
      });
  }, []);

  const active = { ...company, ...companyOverride };

  return (
    <div className="w-full border-b-2 border-slate-900 pb-4 mb-6 text-slate-200 font-sans print:border-black">
      {/* Top Header Row */}
      <div className="flex flex-col sm:flex-row justify-between items-start gap-4">
        {/* Left: Logo & Corporate Identity */}
        <div className="flex items-start gap-4 max-w-lg">
          {active.logo_url ? (
            <img
              src={active.logo_url}
              alt={active.raison_sociale}
              className="w-20 h-20 object-contain rounded-xl border border-slate-700 bg-slate-900 p-1 shrink-0"
            />
          ) : (
            <div className="w-20 h-20 rounded-xl bg-slate-900 text-white flex flex-col items-center justify-center font-black text-xl shrink-0 shadow-sm print:border print:border-black print:text-black print:bg-transparent">
              <span>{active.sigle || 'EVO'}</span>
              <span className="text-[9px] tracking-widest font-normal text-cyan-300 print:text-black">LOG</span>
            </div>
          )}

          <div className="space-y-0.5">
            <h1 className="text-base font-black uppercase tracking-tight text-slate-950 leading-tight">
              {active.raison_sociale}
            </h1>
            <p className="text-[11px] text-slate-400 font-medium">
              {active.forme_juridique} {active.capital_social ? `au capital de ${active.capital_social}` : ''}
            </p>
            <div className="text-[10px] text-slate-400 space-y-0.5 pt-0.5">
              <p>
                <span className="font-semibold text-slate-200">NIF :</span> {active.nif} •{' '}
                <span className="font-semibold text-slate-200">RCCM :</span> {active.rccm}
              </p>
              {active.agrement_douane && (
                <p>
                  <span className="font-semibold text-slate-200">Agrément Douane :</span> {active.agrement_douane}
                  {active.agrement_pad && ` • PAD : ${active.agrement_pad}`}
                </p>
              )}
              <p className="flex items-center gap-2 pt-0.5">
                <span>{active.adresse}, {active.ville} - {active.pays}</span>
                <span>• Tél : {active.telephone}</span>
              </p>
            </div>
          </div>
        </div>

        {/* Right: Document Formal Identity Box */}
        <div className="text-right sm:self-stretch flex flex-col justify-between border-l-2 border-slate-900 pl-4 print:border-black min-w-[200px]">
          <div>
            <span className="inline-block px-2 py-0.5 text-[10px] font-black uppercase tracking-wider bg-slate-900 text-white rounded print:bg-transparent print:text-black print:border print:border-black">
              DOCUMENT OFFICIEL
            </span>
            <h2 className="text-lg font-black text-slate-950 uppercase mt-1">
              {documentTitle}
            </h2>
            <p className="font-mono text-sm font-bold text-cyan-300 print:text-black">
              N° {documentNumber}
            </p>
          </div>

          <div className="text-[10px] text-slate-400 mt-2 font-mono">
            {documentDate && <p>Émis le : <span className="font-bold text-slate-200">{documentDate}</span></p>}
            {documentReference && <p>Réf. Interne : <span className="font-semibold">{documentReference}</span></p>}
          </div>
        </div>
      </div>
    </div>
  );
}

export function CompanyDocumentFooter({ companyOverride }: { companyOverride?: Partial<CompanyInfo> }) {
  return (
    <div className="w-full border-t border-slate-600 pt-3 mt-8 text-center text-[9px] text-slate-500 font-sans print:text-[8px] print:border-black">
      <p className="font-semibold text-slate-300">
        Document d'exploitation émis par le progiciel certifié EVO-LOG • Conforme réglementation CEMAC / OHADA
      </p>
      <p className="mt-0.5">
        Toute altération, surcharge ou falsification du présent titre engage la responsabilité pénale de son auteur.
      </p>
    </div>
  );
}

export default CompanyDocumentHeader;
