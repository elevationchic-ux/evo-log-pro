// API Service for Finance Module

export interface Transaction {
  id: string;
  type: 'credit' | 'debit';
  amount: number;
  currency: string;
  date: string;
  description: string;
  status: 'pending' | 'completed' | 'failed';
}

export interface Invoice {
  id: string;
  client: string;
  amount: number;
  dueDate: string;
  status: 'draft' | 'sent' | 'paid' | 'overdue';
  items: Array<{ description: string; quantity: number; unitPrice: number }>;
}

export interface BankReconciliation {
  id: string;
  bankAccount: string;
  statementDate: string;
  openingBalance: number;
  closingBalance: number;
  transactions: Transaction[];
}

