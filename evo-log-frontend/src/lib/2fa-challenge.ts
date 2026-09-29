// src/lib/2fa-challenge.ts  Transit de l'attente 2FA entre /login et /mfa.
//
// Le jeton `two_factor_token` delivre par POST /auth/login n'est PAS un token
// de session : il ne sert qu'a presenter une tentative de second facteur et
// expire cote backend au bout de 5 minutes (TWO_FACTOR_TOKEN_EXPIRE_MINUTES).
// On le garde donc en sessionStorage (jamais en URL, pour ne pas le laisser
// trainer dans l'historique ou les logs) et on le jette au premier succes.
// L'appelant ne lit jamais le jeton pour en deduire un etat « connecte » : la
// seule session possible est celle que delivre /auth/2fa/verify.

const STORAGE_KEY = 'evo_2fa_challenge_v1'

/** Le TTL backend est de 5 min ; on se coupe a 4 pour eviter d'afficher un
 *  champ de code qui ne pourra plus etre valide. */
const MAX_AGE_MS = 4 * 60 * 1000

export interface TwoFactorChallenge {
  two_factor_token: string
  /** Identifiant saisi a l'etape precedente, affiche pour rappel seulement. */
  identifier: string
  saved_at: number
}

export function saveTwoFactorChallenge(challenge: { two_factor_token: string; identifier: string }): void {
  if (typeof window === 'undefined') return;
  try {
    const payload: TwoFactorChallenge = { ...challenge, saved_at: Date.now() };
    window.sessionStorage.setItem(STORAGE_KEY, JSON.stringify(payload));
  } catch {
    // sessionStorage indisponible (navigation privee, quota) : l'etape 2FA
    // sera simplement indisponible, la page /mfa le dira plutôt que de mentir.
  }
}

export function readTwoFactorChallenge(): TwoFactorChallenge | null {
  if (typeof window === 'undefined') return null;
  try {
    const brut = window.sessionStorage.getItem(STORAGE_KEY);
    if (!brut) return null;
    const parsed = JSON.parse(brut) as TwoFactorChallenge;
    if (!parsed?.two_factor_token) {
      window.sessionStorage.removeItem(STORAGE_KEY);
      return null;
    }
    if (Date.now() - Number(parsed.saved_at || 0) > MAX_AGE_MS) {
      window.sessionStorage.removeItem(STORAGE_KEY);
      return null;
    }
    return parsed;
  } catch {
    return null;
  }
}

export function clearTwoFactorChallenge(): void {
  if (typeof window === 'undefined') return;
  try {
    window.sessionStorage.removeItem(STORAGE_KEY);
  } catch {
    // Rien a nettoyer si le stockage est inaccessible.
  }
}
