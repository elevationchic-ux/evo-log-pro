'use client';

import { createContext, useContext, ReactNode, useState, useEffect, useCallback } from 'react';
import { UserRole } from '@/utils/tcodeLookup';
import { useSession, signOut } from 'next-auth/react';
import { authAPI, setAuthToken } from '@/lib/api-client';

interface User {
  id: string;
  email: string;
  roles: string[];
  modulesAllowed: string[];
  fullName: string;
  agencyId: number;
}

interface AuthContextType {
  user: User | null;
  loading: boolean;
  logout: () => void;
  sessionExpiresAt: Date | null;
  renewSession: () => void;
  sessionExpired: boolean;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: ReactNode }) {
  const { data: session, status } = useSession();
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);
  const [sessionExpiresAt, setSessionExpiresAt] = useState<Date | null>(null);
  const [sessionExpired, setSessionExpired] = useState(false);

  useEffect(() => {
    if (status === 'loading') {
      setLoading(true);
      return;
    }

    if (session?.user) {
      const accessToken = (session.user as any).accessToken as string | null;
      
      // 🔑 CRITICAL FIX: Inject the Bearer token into all axios calls
      // This fixes non-admin roles being auto-disconnected after login
      setAuthToken(accessToken || null);

      setUser({
        id: (session.user as any).id || '',
        email: session.user.email || '',
        roles: ((session.user as any).roles as string[]) || [],
        modulesAllowed: ((session.user as any).modules_allowed as string[]) || [],
        fullName: (session.user as any).nom || '',
        agencyId: 1, // Default fallback
      });
      // La durée de session est gérée par NextAuth (12h).
      setSessionExpiresAt(new Date(Date.now() + 12 * 3600 * 1000));
      setSessionExpired(false);
      setLoading(false);
    } else {
      // Clear token when session ends
      setAuthToken(null);
      setUser(null);
      setLoading(false);
    }
  }, [session, status]);

  const logout = useCallback(async () => {
    setUser(null);
    setSessionExpiresAt(null);
    setSessionExpired(false);
    
    // Clear the axios bearer token
    setAuthToken(null);
    
    // Nettoyer le localStorage
    localStorage.removeItem('access_token');
    localStorage.removeItem('evolog_token');
    localStorage.removeItem('refresh_token');
    
    // Nettoyer les cookies backend
    try {
      await authAPI.logout();
    } catch (e) {
      console.error("Backend logout failed", e);
    }

    // Déconnexion NextAuth sans redirection immédiate (pour voir la belle page de logout)
    signOut({ redirect: false });
  }, []);

  const renewSession = useCallback(() => {
    if (user) {
      const newExpiry = new Date();
      newExpiry.setMinutes(newExpiry.getMinutes() + 30);
      setSessionExpiresAt(newExpiry);
      setSessionExpired(false);
      console.log('Session renewed until:', newExpiry.toLocaleTimeString());
    }
  }, [user]);

  // Monitor session expiration locally and listen for 401 api errors
  // Grace period: don't react to auth-error events in the first 5 seconds after session establishment
  useEffect(() => {
    let graceTimeout: NodeJS.Timeout | null = null;
    let isListening = false;

    const handleAuthError = (e: Event) => {
      if (!isListening) return; // Skip during grace period
      console.warn("401 Unauthorized intercepted, logging out...");
      logout();
      if (window.location.pathname !== '/login') {
        window.location.href = '/login?expired=true';
      }
    };
    
    // Activate listener after grace period only if user is logged in
    if (user) {
      graceTimeout = setTimeout(() => {
        isListening = true;
      }, 5000);
    }

    window.addEventListener('auth-error', handleAuthError);

    let timer: NodeJS.Timeout | null = null;
    if (sessionExpiresAt && !sessionExpired) {
      timer = setInterval(() => {
        if (Date.now() >= sessionExpiresAt.getTime()) {
          setSessionExpired(true);
          isListening = true; // Force listen for expiry-driven logout
          handleAuthError(new Event('auth-error'));
          if (timer) clearInterval(timer);
        }
      }, 1000);
    }

    return () => {
      window.removeEventListener('auth-error', handleAuthError);
      if (timer) clearInterval(timer);
      if (graceTimeout) clearTimeout(graceTimeout);
    };
  }, [sessionExpiresAt, sessionExpired, logout, user]);

  return (
    <AuthContext.Provider value={{ user, loading, logout, sessionExpiresAt, renewSession, sessionExpired }}>
      {children}
    </AuthContext.Provider>
  );
}

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) throw new Error('useAuth must be used within an AuthProvider');
  return context;
};