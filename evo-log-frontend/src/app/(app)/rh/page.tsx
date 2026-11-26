'use client';

import { useEffect } from 'react';
import { useRouter } from 'next/navigation';

export default function ClientRedirectPage() {
  const router = useRouter();
  useEffect(() => {
    router.replace('/rh/dashboard');
  }, [router]);

  return (
    <div className="p-8 text-center text-slate-500 font-mono">
      Redirection vers /rh/dashboard...
    </div>
  );
}
