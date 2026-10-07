"""Manifest Vague D — batch D5 (« sobre & honnete », cas explicitement <20).

Deux modules volontairement sobres : on ne les gonfle PAS a 20 avec des ecrans
creux, conformement a la decision d'honnetete de la Vague D (Zero-Mock Policy).

  - chat        -> perm_module="communication". La messagerie temps reel (forum
    + DM) est deja l'interface maitresse (/chat?tab=...). On n'ajoute QUE les
    enregistrements d'administration reellement justifies d'un module de
    communication d'entreprise : communiques officiels, canaux thematiques,
    signalements de contenu a moderer. -> 2 existants + 3 = 5 (<20, motive).
    Chefs de departement / admin entreprise (bypass niveau 0/1) y ont acces.

  - departement -> perm_module="departments" (le module « departments.
    organisation » existe deja au catalogue). La page est une aggregation
    de service (fiche + roster). On ajoute les registres de pilotage qu'un chef
    de service tient reellement, DISTINCTS des tables maitresses rh-personnel :
    objectifs de service, reunions/CR, projets internes, demandes
    inter-services. -> 1 existant + 4 = 5 (<20, motive).

Aucune valeur fabriquee ; statut = cycle de vie metier explicite ; identifiants
d'enum sans point ni chiffre leading. Chaine Alembic 103-104 depuis
102_heavylift_e_deep. prefixes table/chat -> cht_, departement -> dep_ (neufs).
"""


def E(slug, table, cn, entite, perm, titre, titreEn, desc, descEn, aide, aideEn, icon,
      unicite, fields, enums=None):
    return dict(slug=slug, table=table, class_name=cn, entite=entite, perm=perm,
                titre=titre, titreEn=titreEn, description=desc, descriptionEn=descEn,
                aide=aide, aideEn=aideEn, icon=icon, unicite=unicite,
                fields=fields, enums=enums or [])


def F(name, typ, label, labelEn=None, required=False, search=False):
    d = dict(name=name, type=typ, label=label, labelEn=labelEn or label)
    if required:
        d["required"] = True
    if search:
        d["search"] = True
    return d


def EN(name, values, default=None):
    d = dict(name=name, values=values)
    if default:
        d["default"] = default
    return d


MODULES = {}

# ─── chat (+3 -> 5, sobre : administration de la communication) ──────────────
MODULES["chat_d5"] = dict(
    module_key="chat_d5", module_slug="chat",
    module_path="chat", perm_module="communication",
    registre_filename="registres_d5",
    revision="103", down_revision="102_heavylift_e_deep",
    entities=[
        E("announcements", "cht_announcements", "ChtAnnouncement", "cht-announcements",
          "announcement", "Communiques officiels", "Official announcements",
          "Communique officiel diffuse par la direction ou un chef de service.",
          "Official announcement issued by management or a department head.",
          "La cible et l' epinglage reglent la portee de la diffusion.",
          "Audience and pinning control the reach of the broadcast.",
          "Megaphone", "reference",
          [F("reference", "str", "Reference", "Reference", required=True, search=True),
           F("titre", "str", "Titre", "Title", search=True),
           F("contenu", "text", "Contenu", "Body"),
           F("cible", "str", "Cible", "Audience"),
           F("auteur", "str", "Auteur", "Author"),
           F("epingle", "bool", "Epingle", "Pinned"),
           F("date_publication", "datetime", "Publication", "Published on"),
           F("statut", "str", "Statut", "Status")],
          [EN("statut", ["BROUILLON", "PUBLIEE", "EPINGLEE", "DEPUBLEE"])]),

        E("channels", "cht_channels", "ChtChannel", "cht-channels",
          "channel", "Canaux thematiques", "Thematic channels",
          "Canal de discussion thematique cree et administre dans le chat.",
          "Thematic discussion channel created and administered in the chat.",
          "Le type d' acces et le nombre de membres encadrent le canal.",
          "Access type and member count govern the channel.",
          "Hash", "reference",
          [F("reference", "str", "Reference", "Reference", required=True, search=True),
           F("nom", "str", "Nom", "Name", search=True),
           F("thematique", "str", "Thematique", "Topic"),
           F("description", "text", "Description", "Description"),
           F("createur", "str", "Createur", "Creator"),
           F("membres", "int", "Membres", "Members"),
           F("statut", "str", "Statut", "Status")],
          [EN("statut", ["ACTIF", "ARCHIVE", "PRIVE", "PUBLIC"])]),

        E("content-reports", "cht_content_reports", "ChtContentReport", "cht-content-reports",
          "content_report", "Signalements de contenu", "Content reports",
          "Signalement d' un message pour moderation par un habilité.",
          "Report of a message for moderation by an authorized reviewer.",
          "La severite et le motif conditionnent la decision de moderation.",
          "Severity and reason drive the moderation decision.",
          "Flag", "reference",
          [F("reference", "str", "Reference", "Reference", required=True, search=True),
           F("signalant", "str", "Signalant", "Reporter"),
           F("contenu_signale", "text", "Contenu signale", "Reported content"),
           F("motif", "str", "Motif", "Reason"),
           F("severite", "str", "Severite", "Severity"),
           F("date_signalement", "datetime", "Signale le", "Reported on"),
           F("statut", "str", "Statut", "Status")],
          [EN("motif", ["HARCELEMENT", "INFORMATION_INTERDITE", "HORS_SUJET", "ABUS"]),
           EN("severite", ["BENIN", "SERIEUX", "CRITIQUE"]),
           EN("statut", ["OUVERT", "EN_COURS", "IGNORE", "SANCTIONNE"])]),
    ],
)

# ─── departement (+4 -> 5, sobre : pilotage de service) ──────────────────────
MODULES["departement_d5"] = dict(
    module_key="departement_d5", module_slug="departement",
    module_path="departement", perm_module="departments",
    registre_filename="registres_d5",
    revision="104", down_revision="103_chat_d5_deep",
    entities=[
        E("objectives", "dep_objectives", "DepObjective", "dep-objectives",
          "objective", "Objectifs de service", "Department objectives",
          "Objectif de service suivi par le chef de departement.",
          "Department objective tracked by the department head.",
          "L' ecart entre cible et realise mesure l' atteinte.",
          "Gap between target and actual measures attainment.",
          "Target", "reference",
          [F("reference", "str", "Reference", "Reference", required=True, search=True),
           F("libelle", "str", "Libelle", "Label", search=True),
           F("indicateur", "str", "Indicateur", "Indicator"),
           F("cible", "num", "Cible", "Target"),
           F("realise", "num", "Realise", "Actual"),
           F("trimestre", "str", "Trimestre", "Quarter"),
           F("statut", "str", "Statut", "Status")],
          [EN("statut", ["PLANIFIE", "EN_COURS", "ATTEINT", "MANQUE"])]),

        E("service-meetings", "dep_service_meetings", "DepServiceMeeting", "dep-service-meetings",
          "service_meeting", "Reunions de service", "Service meetings",
          "Reunion de service avec ordre du jour et compte rendu.",
          "Department meeting with agenda and minutes.",
          "Le compte rendu valide la tenue et les decisions.",
          "The minutes validate the meeting and its decisions.",
          "CalendarClock", "reference",
          [F("reference", "str", "Reference", "Reference", required=True, search=True),
           F("objet", "str", "Objet", "Subject", search=True),
           F("date", "datetime", "Date", "Date"),
           F("participants", "int", "Participants", "Attendees"),
           F("compte_rendu", "text", "Compte rendu", "Minutes"),
           F("statut", "str", "Statut", "Status")],
          [EN("statut", ["PLANIFIEE", "TENUE", "REDIGEE", "CLOTUREE"])]),

        E("projects", "dep_projects", "DepProject", "dep-projects",
          "project", "Projets internes du service", "Department projects",
          "Projet interne porte par le departement.",
          "Internal project owned by the department.",
          "Le budget et l' echeance cadrent la realisation.",
          "Budget and deadline frame the delivery.",
          "FolderKanban", "reference",
          [F("reference", "str", "Reference", "Reference", required=True, search=True),
           F("nom", "str", "Nom", "Name", search=True),
           F("responsable", "str", "Responsable", "Owner"),
           F("budget", "num", "Budget", "Budget"),
           F("echeance", "date", "Echeance", "Deadline"),
           F("statut", "str", "Statut", "Status")],
          [EN("statut", ["INITIE", "EN_COURS", "SUSPENDU", "LIVRE"])]),

        E("inter-service-requests", "dep_service_requests", "DepServiceRequest", "dep-service-requests",
          "service_request", "Demandes inter-services", "Inter-service requests",
          "Demande formelle d' un service vers un autre service.",
          "Formal request from one department to another.",
          "L' urgence et le service destinataire pilotent le traitement.",
          "Urgency and target department drive the handling.",
          "ArrowLeftRight", "reference",
          [F("reference", "str", "Reference", "Reference", required=True, search=True),
           F("objet", "str", "Objet", "Subject", search=True),
           F("service_destinataire", "str", "Service destinataire", "Target department"),
           F("urgence", "str", "Urgence", "Urgency"),
           F("date_demande", "date", "Demande le", "Requested on"),
           F("statut", "str", "Statut", "Status")],
          [EN("urgence", ["BASSE", "MOYENNE", "HAUTE", "CRITIQUE"]),
           EN("statut", ["SOUMISE", "TRAITEE", "RETORNEE", "CLOTUREE"])]),
    ],
)
