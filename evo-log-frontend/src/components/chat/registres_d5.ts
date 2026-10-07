/**
 * Configs Registre pour chat (expansion generee).
 *
 * Chaque ConfigRegistre est passe en prop au composant generique
 * <RegistreGenerique /> pour rendre table, filtres, formulaire.
 */
"use client";

import * as Icons from 'lucide-react';
import type { ConfigRegistre, ColonneRegistre, ChampRegistre, FiltreRegistre } from '@/components/registre-generique/typesRegistre';
import { registreAPI } from '@/lib/api-client';

const api = registreAPI("chat");

function col(name: string, label: string, labelEn: string, opts: Partial<ColonneRegistre> = {}): ColonneRegistre {
  return { name, label, labelEn, ...opts } as ColonneRegistre;
}

function txt(name: string, label: string, labelEn: string, opts: Partial<ChampRegistre> = {}): ChampRegistre {
  return { name, label, labelEn, type: "texte", ...opts } as ChampRegistre;
}

function num(name: string, label: string, labelEn: string, opts: Partial<ChampRegistre> = {}): ChampRegistre {
  return { name, label, labelEn, type: "nombre", ...opts } as ChampRegistre;
}

function dt(name: string, label: string, labelEn: string): ChampRegistre {
  return { name, label, labelEn, type: "date" } as ChampRegistre;
}

function dtx(name: string, label: string, labelEn: string): ChampRegistre {
  return { name, label, labelEn, type: "date" } as ChampRegistre;
}

function area(name: string, label: string, labelEn: string): ChampRegistre {
  return { name, label, labelEn, type: "zone" } as ChampRegistre;
}

function chk(name: string, label: string, labelEn: string): ChampRegistre {
  return { name, label, labelEn, type: "booleen" } as ChampRegistre;
}

function sel(name: string, label: string, labelEn: string, nomKey: string): ChampRegistre {
  return { name, label, labelEn, type: "select", nomenclature: nomKey } as ChampRegistre;
}

function filtreSel(name: string, label: string, labelEn: string, nomKey: string): FiltreRegistre {
  return { name, label, labelEn, type: "select", nomenclature: nomKey } as FiltreRegistre;
}

export const registreChtAnnouncement: ConfigRegistre = {
  permModule: "communication",
  permSousModule: "announcement",
  tcode: "registre-announcements",
  icon: Icons.Megaphone,
  titre: "Communiques officiels",
  titreEn: "Official announcements",
  description: "Communique officiel diffuse par la direction ou un chef de service.",
  descriptionEn: "Official announcement issued by management or a department head.",
  aide: "La cible et l' epinglage reglent la portee de la diffusion.",
  aideEn: "Audience and pinning control the reach of the broadcast.",
  lister: (params) => api.lister("cht-announcements", params),
  creer: (data) => api.creer("cht-announcements", data),
  modifier: (id, data) => api.modifier("cht-announcements", id, data),
  unicite: "reference",
  fetchNomenclatures: () => api.getNomenclatures(),
  colonnes: [
    col("reference", "Reference", "Reference"),
    col("titre", "Titre", "Title"),
    col("contenu", "Contenu", "Body"),
    col("cible", "Cible", "Audience"),
    col("auteur", "Auteur", "Author"),
    col("epingle", "Epingle", "Pinned"),
    col("date_publication", "Publication", "Published on"),
    col("statut", "Statut", "Status"),
  ],
  champs: [
    txt("reference", "Reference", "Reference", { requisCreation: true }),
    txt("titre", "Titre", "Title"),
    txt("contenu", "Contenu", "Body"),
    txt("cible", "Cible", "Audience"),
    txt("auteur", "Auteur", "Author"),
    chk("epingle", "Epingle", "Pinned"),
    dtx("date_publication", "Publication", "Published on"),
    txt("statut", "Statut", "Status"),
  ],
};


export const registreChtChannel: ConfigRegistre = {
  permModule: "communication",
  permSousModule: "channel",
  tcode: "registre-channels",
  icon: Icons.Hash,
  titre: "Canaux thematiques",
  titreEn: "Thematic channels",
  description: "Canal de discussion thematique cree et administre dans le chat.",
  descriptionEn: "Thematic discussion channel created and administered in the chat.",
  aide: "Le type d' acces et le nombre de membres encadrent le canal.",
  aideEn: "Access type and member count govern the channel.",
  lister: (params) => api.lister("cht-channels", params),
  creer: (data) => api.creer("cht-channels", data),
  modifier: (id, data) => api.modifier("cht-channels", id, data),
  unicite: "reference",
  fetchNomenclatures: () => api.getNomenclatures(),
  colonnes: [
    col("reference", "Reference", "Reference"),
    col("nom", "Nom", "Name"),
    col("thematique", "Thematique", "Topic"),
    col("description", "Description", "Description"),
    col("createur", "Createur", "Creator"),
    col("membres", "Membres", "Members"),
    col("statut", "Statut", "Status"),
  ],
  champs: [
    txt("reference", "Reference", "Reference", { requisCreation: true }),
    txt("nom", "Nom", "Name"),
    txt("thematique", "Thematique", "Topic"),
    txt("description", "Description", "Description"),
    txt("createur", "Createur", "Creator"),
    num("membres", "Membres", "Members"),
    txt("statut", "Statut", "Status"),
  ],
};


export const registreChtContentReport: ConfigRegistre = {
  permModule: "communication",
  permSousModule: "content_report",
  tcode: "registre-content-reports",
  icon: Icons.Flag,
  titre: "Signalements de contenu",
  titreEn: "Content reports",
  description: "Signalement d' un message pour moderation par un habilité.",
  descriptionEn: "Report of a message for moderation by an authorized reviewer.",
  aide: "La severite et le motif conditionnent la decision de moderation.",
  aideEn: "Severity and reason drive the moderation decision.",
  lister: (params) => api.lister("cht-content-reports", params),
  creer: (data) => api.creer("cht-content-reports", data),
  modifier: (id, data) => api.modifier("cht-content-reports", id, data),
  unicite: "reference",
  fetchNomenclatures: () => api.getNomenclatures(),
  colonnes: [
    col("reference", "Reference", "Reference"),
    col("signalant", "Signalant", "Reporter"),
    col("contenu_signale", "Contenu signale", "Reported content"),
    col("motif", "Motif", "Reason"),
    col("severite", "Severite", "Severity"),
    col("date_signalement", "Signale le", "Reported on"),
    col("statut", "Statut", "Status"),
  ],
  champs: [
    txt("reference", "Reference", "Reference", { requisCreation: true }),
    txt("signalant", "Signalant", "Reporter"),
    txt("contenu_signale", "Contenu signale", "Reported content"),
    txt("motif", "Motif", "Reason"),
    txt("severite", "Severite", "Severity"),
    dtx("date_signalement", "Signale le", "Reported on"),
    txt("statut", "Statut", "Status"),
  ],
};

