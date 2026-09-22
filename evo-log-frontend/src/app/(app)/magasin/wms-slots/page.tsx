'use client'

import React from 'react'
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/Card'
import { Button } from '@/components/ui/button'
import { Plus, LayoutGrid, PackageSearch } from 'lucide-react'
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table'
import { Badge } from '@/components/ui/badge'

export default function WmsSlotsPage() {
  // Static data representing StorageSlots
  const slots = [
    { id: 1, code: 'A-01-01', aisle: 'A', rack: '01', level: '1', status: 'OCCUPIED', maxWeight: 1000, currentWeight: 800 },
    { id: 2, code: 'A-01-02', aisle: 'A', rack: '01', level: '2', status: 'AVAILABLE', maxWeight: 1000, currentWeight: 0 },
    { id: 3, code: 'A-01-03', aisle: 'A', rack: '01', level: '3', status: 'AVAILABLE', maxWeight: 800, currentWeight: 0 },
    { id: 4, code: 'B-01-01', aisle: 'B', rack: '01', level: '1', status: 'OCCUPIED', maxWeight: 1500, currentWeight: 1450 },
    { id: 5, code: 'B-01-02', aisle: 'B', rack: '01', level: '2', status: 'MAINTENANCE', maxWeight: 1500, currentWeight: 0 },
  ]

  return (
    <div className="p-6 space-y-6">
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h1 className="text-3xl font-bold tracking-tight text-gray-900">Magasin: Cartographie WMS</h1>
          <p className="text-muted-foreground mt-1">
            Gérez les emplacements physiques (Allées, Racks, Niveaux) et le "Directed Put-away".
          </p>
        </div>
        <div className="flex items-center gap-3">
          <Button variant="outline">
            <LayoutGrid className="w-4 h-4 mr-2" />
            Vue 3D
          </Button>
          <Button>
            <Plus className="w-4 h-4 mr-2" />
            Nouvel Emplacement
          </Button>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between pb-2 space-y-0">
            <CardTitle className="text-sm font-medium">Total Emplacements</CardTitle>
            <PackageSearch className="w-4 h-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">1,240</div>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="flex flex-row items-center justify-between pb-2 space-y-0">
            <CardTitle className="text-sm font-medium">Libres</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-green-600">450</div>
            <p className="text-xs text-muted-foreground mt-1">36% de la capacité</p>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="flex flex-row items-center justify-between pb-2 space-y-0">
            <CardTitle className="text-sm font-medium">Occupés</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-blue-600">785</div>
            <p className="text-xs text-muted-foreground mt-1">63% de la capacité</p>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="flex flex-row items-center justify-between pb-2 space-y-0">
            <CardTitle className="text-sm font-medium">Maintenance</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-red-600">5</div>
          </CardContent>
        </Card>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Liste des Emplacements</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="rounded-md border">
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Code Emplacement</TableHead>
                  <TableHead>Allée</TableHead>
                  <TableHead>Rack</TableHead>
                  <TableHead>Niveau</TableHead>
                  <TableHead>Poids Max (kg)</TableHead>
                  <TableHead>Statut</TableHead>
                  <TableHead className="text-right">Actions</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {slots.map((slot) => (
                  <TableRow key={slot.id}>
                    <TableCell className="font-mono font-medium">{slot.code}</TableCell>
                    <TableCell>{slot.aisle}</TableCell>
                    <TableCell>{slot.rack}</TableCell>
                    <TableCell>{slot.level}</TableCell>
                    <TableCell>
                      {slot.currentWeight} / {slot.maxWeight}
                      <div className="w-full bg-gray-200 rounded-full h-1.5 mt-1">
                        <div 
                          className={`h-1.5 rounded-full ${slot.currentWeight / slot.maxWeight > 0.9 ? 'bg-red-500' : 'bg-blue-500'}`} 
                          style={{ width: `${(slot.currentWeight / slot.maxWeight) * 100}%` }}
                        ></div>
                      </div>
                    </TableCell>
                    <TableCell>
                      <Badge variant={
                        slot.status === 'AVAILABLE' ? 'default' : 
                        slot.status === 'OCCUPIED' ? 'secondary' : 'destructive'
                      }>
                        {slot.status === 'AVAILABLE' ? 'Libre' : slot.status === 'OCCUPIED' ? 'Occupé' : 'Maintenance'}
                      </Badge>
                    </TableCell>
                    <TableCell className="text-right">
                      <Button variant="ghost" size="sm">Détails</Button>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
