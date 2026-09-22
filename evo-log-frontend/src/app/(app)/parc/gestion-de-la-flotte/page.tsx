'use client';

import { useEffect } from 'react';
import { useRouter } from 'next/navigation';

export default function ClientRedirectPage() {
  const router = useRouter();
  useEffect(() => {
    router.replace('/transport/flotte');
  }, [router]);

  return (
    <div className="p-8 text-center text-slate-500 font-mono">
      Redirection vers /transport/flotte...
    </div>
  );
}
