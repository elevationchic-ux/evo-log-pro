'use client'

import { useState } from 'react'
import { QrCode, CheckCircle, AlertTriangle, Info, Printer, Save, Camera } from 'lucide-react'
import { toast } from 'sonner'

interface InventoryItem {
  status: 'match' | 'shortage' | 'overage' | 'pending'
  location: string
  code: string
  description: string
  uom: string
  systemQty: number
  realQty: number | string
  variance: number | string
}

export default function SaisieInventairePhysiquePage() {
  const [selectedWarehouse, setSelectedWarehouse] = useState('WH-A (Terminal 1)')
  const [selectedZone, setSelectedZone] = useState('Zone A-12')
  const [inventoryDate, setInventoryDate] = useState('2026-08-15')
  const [showScanner, setShowScanner] = useState(false)
  const [scannedCode, setScannedCode] = useState('')

  const [inventoryItems, setInventoryItems] = useState<InventoryItem[]>([
    {
      status: 'match',
      location: 'A-12-01',
      code: 'ART-4492-X',
      description: 'Filtre à huile lourd MAN',
      uom: 'PCS',
      systemQty: 45.00,
      realQty: 45,
      variance: 0.00
    },
    {
      status: 'shortage',
      location: 'A-12-02',
      code: 'ART-1102-Y',
      description: 'Plaquettes de frein remorque',
      uom: 'SET',
      systemQty: 12.00,
      realQty: 10,
      variance: -2.00
    },
    {
      status: 'overage',
      location: 'A-12-03',
      code: 'ART-8831-Z',
      description: 'Lubrifiant synthétique 5L',
      uom: 'BID',
      systemQty: 100.00,
      realQty: 105,
      variance: 5.00
    },
    {
      status: 'pending',
      location: 'A-12-04',
      code: 'ART-5510-A',
      description: 'Courroie de distribution renforcée',
      uom: 'PCS',
      systemQty: 8.00,
      realQty: '',
      variance: '--'
    },
    {
      status: 'pending',
      location: 'A-12-05',
      code: 'ART-9921-B',
      description: 'Joint torique industriel (Lot 100)',
      uom: 'LOT',
      systemQty: 22.00,
      realQty: '',
      variance: '--'
    }
  ])

  const handleRealQtyChange = (index: number, value: string) => {
    const newItems = [...inventoryItems]
    const realQty = value === '' ? '' : parseFloat(value)
    newItems[index].realQty = realQty
    
    if (realQty !== '' && typeof realQty === 'number') {
      const variance = realQty - newItems[index].systemQty
      newItems[index].variance = variance
      
      if (variance === 0) {
        newItems[index].status = 'match'
      } else if (variance < 0) {
        newItems[index].status = 'shortage'
      } else {
        newItems[index].status = 'overage'
      }
    } else {
      newItems[index].status = 'pending'
      newItems[index].variance = '--'
    }
    
    setInventoryItems(newItems)
  }

  const handleSimulateScan = (codeToScan: string) => {
    const idx = inventoryItems.findIndex(i => i.code.toLowerCase() === codeToScan.toLowerCase())
    if (idx !== -1) {
      const item = inventoryItems[idx]
      const currentQty = typeof item.realQty === 'number' ? item.realQty : 0
      handleRealQtyChange(idx, (currentQty + 1).toString())
      toast.success(`Code-barres scanné : ${item.code} (+1 sur qté réelle)`)
    } else {
      toast.error(`Article ${codeToScan} non trouvé dans cet inventaire`)
    }
    setScannedCode('')
    setShowScanner(false)
  }

  const handleValidateInventory = () => {
    const shortages = inventoryItems.filter(i => i.status === 'shortage').length
    const overages = inventoryItems.filter(i => i.status === 'overage').length
    toast.success(`Inventaire WMS validé ! Écritures de régularisation générées : ${shortages} pertes, ${overages} surplus.`)
  }

  return (
    <div className="min-h-screen p-6 max-w-7xl mx-auto space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2 text-xs text-muted-foreground mb-1">
            <span>K-Magasin WMS</span> • <span className="text-amber-400 font-semibold">Inventaire Physique</span>
          </div>
          <h1 className="text-2xl font-bold text-foreground flex items-center gap-2">
            Saisie Inventaire Physique WMS
            <span className="bg-amber-500/10 text-amber-400 border border-amber-500/30 text-xs px-2.5 py-0.5 rounded-full font-mono">T-CODE: KM01</span>
          </h1>
        </div>
        <div className="flex gap-2">
          <button
            onClick={() => setShowScanner(!showScanner)}
            className="px-4 py-2 bg-amber-500/10 border border-amber-500/30 text-amber-400 rounded-xl flex items-center gap-2 hover:bg-amber-500/20 text-sm font-medium transition-colors"
          >
            <QrCode size={16} /> Scanner Douchette / QR
          </button>
          <button
            onClick={handleValidateInventory}
            className="px-4 py-2 bg-amber-600 hover:bg-amber-700 text-white rounded-xl flex items-center gap-2 text-sm font-bold shadow-lg shadow-amber-600/20 transition-all"
          >
            <Save size={16} /> Valider Écarts WMS
          </button>
        </div>
      </div>

      {/* Zone Scanner Douchette */}
      {showScanner && (
        <div className="p-4 rounded-2xl border border-amber-500/40 bg-amber-500/5 space-y-3 animate-in fade-in duration-300">
          <div className="flex items-center justify-between">
            <span className="text-xs font-bold text-amber-400 uppercase tracking-wide flex items-center gap-2">
              <Camera size={14} /> Mode Scan Douchette / Caméra Mobile
            </span>
            <button onClick={() => setShowScanner(false)} className="text-xs text-muted-foreground hover:text-foreground">Fermer ✕</button>
          </div>
          <div className="flex gap-2">
            <input
              type="text"
              placeholder="Scanner ou saisir un code article (ex: ART-4492-X)..."
              value={scannedCode}
              onChange={(e) => setScannedCode(e.target.value)}
              onKeyDown={(e) => e.key === 'Enter' && handleSimulateScan(scannedCode)}
              className="flex-1 bg-background border border-border rounded-xl px-4 py-2 text-sm font-mono focus:ring-2 focus:ring-amber-500"
              autoFocus
            />
            <button
              onClick={() => handleSimulateScan(scannedCode)}
              className="px-4 py-2 bg-amber-500 text-black font-bold text-sm rounded-xl hover:bg-amber-400 transition-colors"
            >
              Simuler Scan
            </button>
          </div>
          <div className="flex gap-2 text-xs text-muted-foreground">
            <span>Raccourcis rapides test :</span>
            {inventoryItems.map(i => (
              <button key={i.code} onClick={() => handleSimulateScan(i.code)} className="font-mono text-amber-400 underline hover:text-amber-300">
                {i.code}
              </button>
            ))}
          </div>
        </div>
      )}

      {/* Meta Form */}
      <div className="bg-card border border-border rounded-2xl p-4 flex gap-6 items-center flex-wrap">
        <div className="flex flex-col gap-1 w-48">
          <label className="text-xs font-bold text-muted-foreground uppercase">Magasin</label>
          <select 
            className="bg-background border border-border rounded-xl p-2 text-sm"
            value={selectedWarehouse}
            onChange={(e) => setSelectedWarehouse(e.target.value)}
          >
            <option>WH-A (Terminal 1)</option>
            <option>WH-B (Terminal 2)</option>
            <option>Zone Quarantaine</option>
          </select>
        </div>
        <div className="flex flex-col gap-1 w-36">
          <label className="text-xs font-bold text-muted-foreground uppercase">Allée/Zone</label>
          <select 
            className="bg-background border border-border rounded-xl p-2 text-sm"
            value={selectedZone}
            onChange={(e) => setSelectedZone(e.target.value)}
          >
            <option>Zone A-12</option>
            <option>Zone B-04</option>
            <option>Toutes</option>
          </select>
        </div>
        <div className="flex flex-col gap-1 w-40">
          <label className="text-xs font-bold text-muted-foreground uppercase">Date Inventaire</label>
          <input 
            className="bg-background border border-border rounded-xl p-2 text-sm text-foreground" 
            type="date" 
            value={inventoryDate}
            onChange={(e) => setInventoryDate(e.target.value)}
          />
        </div>
        <div className="ml-auto flex items-center gap-2">
          <span className="w-3 h-3 rounded-full bg-emerald-500 animate-pulse"></span>
          <span className="text-sm font-medium text-emerald-400">Saisie active (142 articles)</span>
        </div>
      </div>

      {/* Data Table */}
      <div className="bg-card border border-border rounded-2xl overflow-hidden shadow-sm">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-sm">
            <thead className="bg-muted/40 border-b border-border">
              <tr>
                <th className="py-3 px-4 font-semibold text-muted-foreground text-xs uppercase w-12">Statut</th>
                <th className="py-3 px-4 font-semibold text-muted-foreground text-xs uppercase w-24">Empl.</th>
                <th className="py-3 px-4 font-semibold text-muted-foreground text-xs uppercase w-32">Code Article</th>
                <th className="py-3 px-4 font-semibold text-muted-foreground text-xs uppercase">Description</th>
                <th className="py-3 px-4 font-semibold text-muted-foreground text-xs uppercase text-center w-20">UoM</th>
                <th className="py-3 px-4 font-semibold text-muted-foreground text-xs uppercase text-right w-28">Qté Sys.</th>
                <th className="py-3 px-4 font-semibold text-amber-400 text-xs uppercase text-center w-36 bg-amber-500/5">Qté Réelle</th>
                <th className="py-3 px-4 font-semibold text-muted-foreground text-xs uppercase text-right w-28">Écart</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-border">
              {inventoryItems.map((item, index) => (
                <tr key={index} className="hover:bg-muted/20 transition-colors">
                  <td className="py-3 px-4 text-center">
                    {item.status === 'match' && <CheckCircle size={16} className="text-emerald-400 mx-auto" />}
                    {item.status === 'shortage' && <AlertTriangle size={16} className="text-red-400 mx-auto" />}
                    {item.status === 'overage' && <Info size={16} className="text-blue-400 mx-auto" />}
                    {item.status === 'pending' && <span className="w-3 h-3 rounded-full border border-muted-foreground inline-block"></span>}
                  </td>
                  <td className="py-3 px-4 font-mono text-xs text-muted-foreground">{item.location}</td>
                  <td className="py-3 px-4 font-mono text-xs font-bold text-amber-400">{item.code}</td>
                  <td className="py-3 px-4 text-foreground font-medium">{item.description}</td>
                  <td className="py-3 px-4 text-center text-xs text-muted-foreground">{item.uom}</td>
                  <td className="py-3 px-4 text-right font-bold text-foreground">{item.systemQty.toFixed(2)}</td>
                  <td className="py-2 px-4 text-center bg-amber-500/5">
                    <input 
                      type="number" 
                      className={`w-full text-center border rounded-xl py-1.5 px-2 text-sm font-mono font-bold focus:ring-2 focus:ring-amber-500 bg-background ${
                        item.status === 'shortage' ? 'border-red-500/50 text-red-400' :
                        item.status === 'overage' ? 'border-blue-500/50 text-blue-400' :
                        'border-border text-foreground'
                      }`}
                      value={item.realQty}
                      onChange={(e) => handleRealQtyChange(index, e.target.value)}
                      placeholder="..."
                    />
                  </td>
                  <td className={`py-3 px-4 text-right font-mono font-bold ${
                    item.status === 'shortage' ? 'text-red-400' :
                    item.status === 'overage' ? 'text-blue-400' :
                    'text-muted-foreground'
                  }`}>
                    {typeof item.variance === 'number' ? (item.variance > 0 ? '+' : '') + item.variance.toFixed(2) : item.variance}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  )
}
