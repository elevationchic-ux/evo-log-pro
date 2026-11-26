/**
 * Ancien écran « Tracking GPS & e-POD Signatures » du menu `transport-flotte`.
 *
 * Écran mort et, pire, bavard : il parcourait `EPOD_DATA`, tableau
 * littéralement vide, tandis que le bouton « Exporter Dossiers e-POD »
 * annonçait « Bordereaux e-POD certifiés exportés en archive PDF » et que
 * chaque ligne promettait « Affichage du procès-verbal »  sans un seul appel
 * au backend. Pour une table vide, cela voulait dire certifier des bordereaux
 * qui n'existent pas.
 *
 * La preuve de livraison existe pourtant bien côté réel : `transport/epod`
 * s'appuie sur les missions et sur `POST /api/transport/missions/{id}/livrer`,
 * qui enregistre `signature_receptionnaire` ; et le service POD complet
 * (numero_pod, photo_signature, nom_receveur, hash_preuve, validation,
 * archivage légal) répond sur `/api/v1/transport-avance-complete/pod`. Seule
 * la colonne « Scellé Intact » renvoie à l'acconage (`scelle`, `date_scelle`),
 * pas au transport.
 */
import { redirect } from 'next/navigation';

export default function TransportFlotteTrackingEpodPage() {
  redirect('/transport/epod');
}
