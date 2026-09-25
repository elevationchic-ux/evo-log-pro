import Link from 'next/link';

export default function Forbidden() {
  return (
    <div className="flex flex-col items-center justify-center min-h-screen bg-slate-800">
      <h1 className="text-6xl font-bold text-red-600">403</h1>
      <p className="mt-4 text-xl text-slate-200">Acces interdit</p>
      <p className="mt-2 text-slate-400">Vous n&apos;avez pas les permissions necessaires pour acceder a cette page.</p>
      <Link href="/" className="mt-6 px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors">
        Retour a l&apos;accueil
      </Link>
    </div>
  );
}