// API Service for Other Modules (Documents, Settings, Support)

export interface Document {
  id: string;
  type: string;
  reference: string;
  generatedAt: string;
  module: string;
  fileSize: number;
  fileUrl: string;
}

export interface DocumentCategory {
  id: string;
  name: string;
  icon: string;
  count: number;
  lastAdded: string;
}

export interface SystemSetting {
  id: string;
  key: string;
  value: string;
  category: string;
  description: string;
}

export interface SupportTicket {
  id: string;
  subject: string;
  description: string;
  priority: 'low' | 'medium' | 'high' | 'critical';
  status: 'open' | 'in_progress' | 'resolved' | 'closed';
  createdAt: string;
  userId: string;
}

