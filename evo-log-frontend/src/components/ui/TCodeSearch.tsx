'use client';
import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { getRouteFromTCode } from '@/lib/tcodes';
import { toast } from 'sonner';

export function TCodeSearch() {
  const [tcode, setTcode] = useState('');
  const router = useRouter();

  const handleKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === 'Enter' && tcode.trim() !== '') {
      const route = getRouteFromTCode(tcode);
      if (route) {
        router.push(route);
      } else {
        // Optional: show a small toast or shake animation for invalid T-Code
        toast.error(`T-Code Invalide: ${tcode}`);
      }
    }
  };

  return (
    <div className="relative focus-within:ring-2 focus-within:ring-primary rounded-md">
      <span className="material-symbols-outlined absolute left-3 top-1/2 -translate-y-1/2 text-secondary">search</span>
      <input 
        className="pl-10 pr-4 py-2 border border-outline-variant rounded-md text-sm w-64 bg-surface-container-lowest focus:outline-none font-mono-data text-mono-data" 
        placeholder="Rechercher T-Code (ex: M01)" 
        type="text"
        value={tcode}
        onChange={(e) => setTcode(e.target.value)}
        onKeyDown={handleKeyDown}
      />
    </div>
  );
}
