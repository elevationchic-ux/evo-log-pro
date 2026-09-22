'use client';

import React, { useEffect, useState } from 'react';
import {
  TrendingUp,
  PieChart,
  BarChart3,
  Calendar,
  CheckCircle2,
  AlertTriangle,
  RefreshCw,
  Search,
  FileText,
  ShoppingCart,
  Truck,
  Users
} from 'lucide-react';
import { financeAPI, transportAPI, magasinAPI, analyticsAPI } from '@/lib/api-client';

export default function ClientReportsPage() {
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [dateRange, setDateRange] = useState({
    startDate: new Date(new Date().setMonth(new Date().getMonth() - 1)).toISOString().split('T')[0],
    endDate: new Date().toISOString().split('T')[0]
  });
  const [reportType, setReportType] = useState('financial');
  const [financialData, setFinancialData] = useState(null);
  const [transportData, setTransportData] = useState(null);
  const [inventoryData, setInventoryData] = useState(null);
  const [chartData, setChartData] = useState({});

  useEffect(() => {
    loadReports();
  }, [dateRange, reportType]);

  const loadReports = async () => {
    setLoading(true);
    setError(null);
    try {
      // Load data based on report type
      switch (reportType) {
        case 'financial':
          const financialRes = await financeAPI.getAnalyticsChartData();
          setFinancialData(financialRes.data || financialRes);
          break;
        case 'transport':
          const transportRes = await transportAPI.getVehiclesHistory({
            dateDebut: dateRange.startDate,
            dateFin: dateRange.endDate
          });
          setTransportData(transportRes.data || transportRes);
          break;
        case 'inventory':
          // For simplicity, we'll get general magasin stats
          const magasinRes = await magasinAPI.getKpis();
          setInventoryData(magasinRes.data || magasinRes);
          break;
        default:
          setFinancialData(null);
          setTransportData(null);
          setInventoryData(null);
      }

      // Load chart data for the selected report type
      if (reportType === 'financial') {
        const chartRes = await financeAPI.getAnalyticsChartData();
        setChartData(chartRes.data || chartRes);
      } else if (reportType === 'transport') {
        const chartRes = await transportAPI.getKPIs();
        setChartData(chartRes.data || chartRes);
      }
    } catch (err) {
      console.error('Failed to load reports:', err);
      setError('Impossible de charger les rapports. Veuillez réessayer.');
    } finally {
      setLoading(false);
    }
  };
  return <div><h1>Reports</h1></div>;
}