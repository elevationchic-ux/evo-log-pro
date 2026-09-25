// src/lib/utils.ts  Utilitaires Frontend EVO-LOG
import { type ClassValue, clsx } from 'clsx';
import { twMerge } from 'tailwind-merge';

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

export function formatCurrency(amount: number, currency: string = 'XAF'): string {
  // 'FCFA' n'est pas un code ISO valide (4 lettres) : Intl.NumberFormat levait
  // un RangeError sur chaque appel par défaut. On le normalise en 'XAF', que
  // fr-FR rend déjà « FCFA » à l'affichage.
  const code = currency.toUpperCase() === 'FCFA' ? 'XAF' : currency;
  return new Intl.NumberFormat('fr-FR', {
    style: 'currency',
    currency: code,
    maximumFractionDigits: code === 'XAF' ? 0 : 2,
  }).format(amount);
}

export function formatDate(date: string | Date): string {
  return new Intl.DateTimeFormat('fr-FR', {
    year: 'numeric',
    month: 'long',
    day: 'numeric',
  }).format(new Date(date));
}

export function formatDateTime(date: string | Date): string {
  return new Intl.DateTimeFormat('fr-FR', {
    year: 'numeric',
    month: 'long',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  }).format(new Date(date));
}
