// API Service for Reports Module

export interface ReportTemplate {
  id: string;
  module: string;
  title: string;
  description: string;
  lastRun: string;
  frequency: string;
  owner: string;
  fields: string[];
  filters: Record<string, any>;
}

export interface CustomReport {
  id: string;
  module: string;
  name: string;
  selectedFields: string[];
  filters: {
    startDate: string;
    endDate: string;
    searchColumns: string;
  };
  visualization: 'table' | 'chart' | 'pivot';
  exportFormat: 'excel' | 'pdf' | 'csv';
  scheduleReport: boolean;
}

export interface GeneratedReport {
  id: string;
  templateId: string;
  generatedAt: string;
  status: 'pending' | 'completed' | 'failed';
  fileUrl: string;
  fileSize: number;
}

