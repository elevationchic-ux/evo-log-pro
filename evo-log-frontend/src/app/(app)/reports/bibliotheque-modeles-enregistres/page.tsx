import ModuleLayout from '@/components/layout/ModuleLayout';

export default function BibliothequeModelesEnregistresPage() {
  return (
    <ModuleLayout>
      <div className="space-y-6">
        <div>
          <h1 className="text-headline-lg text-headline-lg text-on-surface">
            BibliothÃ¨que de ModÃ¨les EnregistrÃ©s
          </h1>
          <p className="text-body-md text-body-md text-on-surface-variant mt-1">
            BibliothÃ¨que de modÃ¨les de rapports enregistrÃ©s
          </p>
        </div>
        <div className="bg-surface-container-lowest border border-outline-variant rounded-lg p-6">
          <p className="text-body-md text-on-surface-variant">
            Interface de bibliothÃ¨que de modÃ¨les - En cours de dÃ©veloppement
          </p>
        </div>
      </div>
    </ModuleLayout>
  );
}
