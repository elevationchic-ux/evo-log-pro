import { toast } from 'sonner';

export interface UndoToastOptions {
  message: string;
  description?: string;
  duration?: number;
  onUndo: () => void | Promise<void>;
  undoLabel?: string;
  icon?: string;
}

/**
 * Affiche une notification Sonner avec action "Annuler" réversible.
 * Évite les modales de confirmation bloquantes sur les actions réversibles courantes.
 */
export function showUndoToast({
  message,
  description,
  duration = 6000,
  onUndo,
  undoLabel = 'Annuler',
  icon = '↩️',
}: UndoToastOptions) {
  return toast(message, {
    description,
    duration,
    icon,
    action: {
      label: undoLabel,
      onClick: async () => {
        try {
          await onUndo();
          toast.success('Action annulée avec succès', {
            duration: 3000,
            icon: '✅',
          });
        } catch (error) {
          toast.error("Impossible d'annuler l'opération", {
            duration: 3000,
          });
        }
      },
    },
  });
}
