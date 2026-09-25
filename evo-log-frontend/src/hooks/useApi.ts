'use client';

/**
 * Hook de chargement de données standard du projet EVO-LOG.
 *
 * Garde-fous communs à toutes les pages :
 *  - jamais d'écran blanc : tout échec produit un état classifié et actionnable ;
 *  - distinction explicite des cas : 404 (ressource inexistante), 401/403 (accès),
 *    5xx (panne backend), réseau (backend injoignable), succès vide (0 enregistrement) ;
 *  - refetch manuel, annulation des courses, et messages en français simple.
 */
import { useCallback, useEffect, useRef, useState } from 'react';
import { AxiosError } from 'axios';

export type ApiErrorKind =
  | 'none'
  | 'empty'          // réponse OK mais 0 enregistrement
  | 'not_found'      // 404 : endpoint ou ressource absente
  | 'unauthorized'   // 401/403 : session ou permission
  | 'server'         // 5xx : panne du service backend
  | 'network'        // backend injoignable / timeout
  | 'unknown';

export interface ApiErrorInfo {
  kind: ApiErrorKind;
  /** Message court, en français, compréhensible par un non-expert. */
  message: string;
  /** Détail technique (statut, endpoint) affiché en petit pour le support. */
  detail?: string;
  status?: number;
}

export function classifyApiError(err: unknown): ApiErrorInfo {
  const ax = err as AxiosError;
  const status = ax?.response?.status;
  const url = ax?.config?.url;
  const tech = status ? `HTTP ${status}${url ? `  ${url}` : ''}` : url ? String(url) : undefined;

  if (status === 404) {
    return { kind: 'not_found', message: 'Cette fonction n\u2019est pas encore disponible : le serveur ne connaît pas cette adresse.', detail: tech, status };
  }
  if (status === 401 || status === 403) {
    return { kind: 'unauthorized', message: 'Accès refusé. Votre session a peut-être expiré ou votre rôle ne permet pas de voir ces données.', detail: tech, status };
  }
  if (status && status >= 500) {
    return { kind: 'server', message: 'Le serveur rencontre un problème technique. Réessayez dans quelques instants.', detail: tech, status };
  }
  if (!ax?.response && (ax?.code === 'ERR_NETWORK' || ax?.message?.includes('Network') || ax?.message?.includes('timeout'))) {
    return { kind: 'network', message: 'Le serveur EVO-LOG est injoignable (réseau ou maintenance). Vérifiez votre connexion puis réessayez.', detail: tech };
  }
  return { kind: 'unknown', message: 'Une erreur est survenue pendant le chargement des données.', detail: tech, status };
}

export interface UseApiOptions<T> {
  /** Transforme la réponse brute en donnée exploitable (par ex. extraire .data.items). */
  select?: (payload: unknown) => T;
  /** Valeur considérée comme « vide » (par défaut : tableau vide ou null). */
  isEmpty?: (data: T) => boolean;
  /** Recharge automatiquement toutes les N ms (optionnel). */
  refreshInterval?: number;
}

export interface UseApiResult<T> {
  data: T | null;
  loading: boolean;
  error: ApiErrorInfo | null;
  /** true si la réponse est un succès sans enregistrement (état vide légitime). */
  isEmpty: boolean;
  refetch: () => Promise<void>;
}

function defaultIsEmpty(data: unknown): boolean {
  if (data == null) return true;
  if (Array.isArray(data)) return data.length === 0;
  if (typeof data === 'object') {
    const items = (data as Record<string, unknown>).items;
    if (Array.isArray(items)) return items.length === 0;
    const results = (data as Record<string, unknown>).results;
    if (Array.isArray(results)) return results.length === 0;
    return Object.keys(data as object).length === 0;
  }
  return false;
}

/**
 * useApi(async () => (await magasinAPI.getAll()).data.items)
 */
export function useApi<T>(
  fetcher: () => Promise<T>,
  options: UseApiOptions<T> = {}
): UseApiResult<T> {
  const { isEmpty = defaultIsEmpty as (d: T) => boolean } = options;
  const [data, setData] = useState<T | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<ApiErrorInfo | null>(null);
  const [tick, setTick] = useState(0);
  const reqId = useRef(0);
  const fetcherRef = useRef(fetcher);
  fetcherRef.current = fetcher;

  useEffect(() => {
    let cancelled = false;
    const id = ++reqId.current;
    setLoading(true);
    setError(null);
    (async () => {
      try {
        const result = await fetcherRef.current();
        if (cancelled || id !== reqId.current) return;
        setData(result);
        setError(null);
      } catch (err) {
        if (cancelled || id !== reqId.current) return;
        setError(classifyApiError(err));
        setData(null);
      } finally {
        if (!cancelled && id === reqId.current) setLoading(false);
      }
    })();
    return () => { cancelled = true; };
  }, [tick]);

  useEffect(() => {
    if (!options.refreshInterval) return;
    const t = setInterval(() => setTick((x) => x + 1), options.refreshInterval);
    return () => clearInterval(t);
  }, [options.refreshInterval]);

  const refetch = useCallback(async () => {
    setTick((x) => x + 1);
  }, []);

  return {
    data,
    loading,
    error,
    isEmpty: !loading && !error && isEmpty(data as T),
    refetch,
  };
}
