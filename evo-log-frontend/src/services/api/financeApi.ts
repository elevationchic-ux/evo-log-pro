import { apiClient } from './client';

export interface Invoice {
  id: string;
  number: string;
  clientId: string;
  type: 'INVOICE' | 'CREDIT_NOTE' | 'PROFORMA';
  status: 'DRAFT' | 'VALIDATED' | 'SENT' | 'PAID' | 'OVERDUE' | 'CANCELLED';
  issueDate: string;
  dueDate: string;
  items: InvoiceItem[];
  subtotal: number;
  taxAmount: number;
  total: number;
  paidAmount: number;
  currency: string;
}

export interface InvoiceItem {
  articleId?: string;
  description: string;
  quantity: number;
  unitPrice: number;
  taxRate: number;
  total: number;
}

export interface Payment {
  id: string;
  invoiceId: string;
  amount: number;
  method: 'CASH' | 'BANK_TRANSFER' | 'MOBILE_MONEY' | 'CHECK';
  reference?: string;
  date: string;
  recordedBy?: string;
}

export interface SupplierInvoice {
  id: string;
  number: string;
  supplierId: string;
  status: 'PENDING' | 'PAID' | 'CANCELLED';
  amount: number;
  dueDate: string;
}

export const financeApi = {
  // Invoices
  getInvoices: (params?: { status?: string; clientId?: string; dateFrom?: string; dateTo?: string }) =>
    apiClient.get<{ data: Invoice[]; total: number }>('/finance/invoices', { params }),
  
  getInvoice: (id: string) => apiClient.get<Invoice>(`/finance/invoices/${id}`),
  
  createInvoice: (data: Partial<Invoice>) => apiClient.post<Invoice>('/finance/invoices', data),
  
  validateInvoice: (id: string) => apiClient.post<Invoice>(`/finance/invoices/${id}/validate`),
  
  sendInvoice: (id: string) => apiClient.post<Invoice>(`/finance/invoices/${id}/send`),

  // Payments
  getPayments: (params?: { invoiceId?: string; dateFrom?: string }) =>
    apiClient.get<{ data: Payment[] }>('/finance/payments', { params }),
  
  recordPayment: (data: Partial<Payment>) => apiClient.post<Payment>('/finance/payments', data),

  // Supplier Invoices
  getSupplierInvoices: (params?: { status?: string }) =>
    apiClient.get<{ data: SupplierInvoice[] }>('/finance/supplier-invoices', { params }),

  // Statistics
  getStats: () => apiClient.get<{
    totalReceivable: number;
    totalPayable: number;
    cashFlow: number;
    invoicesThisMonth: number;
    paidThisMonth: number;
    overdueAmount: number;
  }>('/finance/stats'),

  // OHADA Accounting
  getJournalEntries: (params?: { dateFrom?: string; dateTo?: string; accountId?: string }) =>
    apiClient.get<{ data: any[] }>('/finance/accounting/journal', { params }),
  
  createJournalEntry: (data: { debit: any; credit: any; description: string; date: string }) =>
    apiClient.post('/finance/accounting/journal', data),

  getBalance: () => apiClient.get<{
    assets: number;
    liabilities: number;
    equity: number;
    result: number;
  }>('/finance/accounting/balance'),
};

export default financeApi;