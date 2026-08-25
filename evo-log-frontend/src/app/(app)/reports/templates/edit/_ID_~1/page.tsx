export default function EditTemplatePage({ params }: { params: { id: string } }) {
  return (
    <div className="min-h-screen bg-surface-container-low p-6">
      <div className="max-w-7xl mx-auto space-y-6">
        <div>
          <h1 className="text-headline-lg text-headline-lg text-on-surface">
            Modifier le Modèle de Rapport
          </h1>
          <p className="text-body-md text-body-md text-on-surface-variant mt-1">
            Modification du modèle #{params.id}
          </p>
        </div>
        <div className="bg-surface-container-lowest border border-outline-variant rounded-lg p-6">
          <p className="text-body-md text-on-surface-variant">
            Page de modification de modèle - En cours de développement
          </p>
        </div>
      </div>
    </div>
  );
}
