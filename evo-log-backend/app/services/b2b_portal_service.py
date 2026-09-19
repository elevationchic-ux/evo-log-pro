"""
Service Portail B2B Client EVO-LOG
- Suivi temps réel des dossiers (transit, transport, manutention)
- Accès factures, devis et documents associés
- Calculateur de cotations instantané
- Réservation e-Booking en ligne (créneau enlèvement)
- Tracking conteneur ISO 6346 & B/L avec décompte franchise surestaries
- Passerelle de paiement en ligne (Mobile Money MTN/Orange, CB Visa/Mastercard)
- Gestion des alertes multi-canaux (SMS, WhatsApp, Email)
"""
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import random


class B2BPortalService:

    @staticmethod
    def get_dossiers_client(db, client_id: int) -> List[Dict[str, Any]]:
        return [
            {
                "dossier_id": "DOS-2026-00841",
                "type": "TRANSIT_IMPORT",
                "description": "40 containers EVP · Marchandises diverses · Port de Douala",
                "statut": "EN_COURS",
                "progression_pct": 65,
                "conteneur_no": "MSKU9823412",
                "bl_no": "BL-OCEAN-7842",
                "consignataire": "MAERSK CAMEROUN",
                "franchise_jours_restants": 5,
                "etapes": [
                    {"nom": "Débarquement Quai PAD", "statut": "DONE", "date": "18/08/2026", "heure": "06:30"},
                    {"nom": "Réception déclaration DUM & Guce", "statut": "DONE", "date": "20/08/2026", "heure": "11:15"},
                    {"nom": "Entrée Magasin Sous Douane (MAD)", "statut": "DONE", "date": "22/08/2026", "heure": "15:40"},
                    {"nom": "Visite douanière & BAE Accordé", "statut": "IN_PROGRESS", "date": "27/08/2026", "heure": "09:00"},
                    {"nom": "Chargement Camion & Départ Bassa", "statut": "PENDING", "date": "Prévu 30/08/2026", "heure": "--:--"},
                    {"nom": "Livraison Client finale + e-POD", "statut": "PENDING", "date": "Prévu 02/09/2026", "heure": "--:--"},
                ],
                "montant_ht_xaf": 4850000,
                "devise": "XAF",
                "commercial": "Paul MBARGA",
                "contact_tel": "+237 6 88 12 34 56",
                "epod": {
                    "signed": False,
                    "recipient": "Inconnu",
                    "timestamp": None,
                    "signature_url": None
                },
                "documents": [
                    {"nom": "DUM-2026-00841.pdf", "type": "DOUANE", "taille": "1.2 MB"},
                    {"nom": "Facture-PRO-0284.pdf", "type": "FACTURE", "taille": "450 KB"},
                    {"nom": "BL-OCEAN-7842.pdf", "type": "TRANSPORT", "taille": "890 KB"},
                    {"nom": "Bon-Sortie-PAD.pdf", "type": "PORT", "taille": "620 KB"}
                ]
            },
            {
                "dossier_id": "DOS-2026-00815",
                "type": "TRANSPORT_ROUTE",
                "description": "Mission Douala → Yaoundé · Marchandises fragiles (32T)",
                "statut": "LIVRE",
                "progression_pct": 100,
                "conteneur_no": "CMAU7461920",
                "bl_no": "BL-CMA-9921",
                "consignataire": "CMA CGM",
                "franchise_jours_restants": 0,
                "etapes": [
                    {"nom": "Chargement MAG3 Douala", "statut": "DONE", "date": "15/08/2026", "heure": "08:00"},
                    {"nom": "Départ mission convoi N°3", "statut": "DONE", "date": "15/08/2026", "heure": "10:30"},
                    {"nom": "Contrôle pesage Edéa", "statut": "DONE", "date": "15/08/2026", "heure": "14:15"},
                    {"nom": "Arrivée client Yaoundé Nsam", "statut": "DONE", "date": "16/08/2026", "heure": "09:45"},
                    {"nom": "Livraison + e-POD signé", "statut": "DONE", "date": "16/08/2026", "heure": "11:20"},
                ],
                "montant_ht_xaf": 650000,
                "devise": "XAF",
                "commercial": "Sylvie NKODO",
                "contact_tel": "+237 6 55 78 90 12",
                "epod": {
                    "signed": True,
                    "recipient": "Jean-Marc MVONDO",
                    "timestamp": "2026-08-16T11:20:00Z",
                    "signature_url": "/signatures/epod-00815.png",
                    "plomb_status": "CONFORME_INTACT",
                    "geoloc": "3.8480° N, 11.5021° E (Yaoundé)"
                },
                "documents": [
                    {"nom": "ePOD-MIS-2026-0815.pdf", "type": "LIVRAISON", "taille": "780 KB"},
                    {"nom": "Facture-0271.pdf", "type": "FACTURE", "taille": "420 KB"},
                    {"nom": "Lettre-Voiture-CMR.pdf", "type": "TRANSPORT", "taille": "510 KB"}
                ]
            }
        ]

    @staticmethod
    def get_factures_client(db, client_id: int) -> List[Dict[str, Any]]:
        return [
            {
                "id": "FAC-2026-0284",
                "dossier": "DOS-2026-00841",
                "desc": "Transit Import 40 EVP · Port Douala",
                "montant_ht": 4850000,
                "tva_19_25_pct": 933625,
                "montant_ttc": 5783625,
                "statut": "EN_ATTENTE",
                "echeance": "30/09/2026",
                "devise": "XAF",
                "eligible_momo": True,
                "eligible_cb": True
            },
            {
                "id": "FAC-2026-0271",
                "dossier": "DOS-2026-00815",
                "desc": "Transport Douala → Yaoundé 32T",
                "montant_ht": 650000,
                "tva_19_25_pct": 125125,
                "montant_ttc": 775125,
                "statut": "PAYEE",
                "echeance": "31/08/2026",
                "devise": "XAF",
                "reference_paiement": "MOMO-CM-89218491",
                "date_paiement": "2026-08-20T14:32:00Z",
                "eligible_momo": False,
                "eligible_cb": False
            },
            {
                "id": "FAC-2026-0245",
                "dossier": "DOS-2026-00782",
                "desc": "Manutention portuaire 20 conteneurs",
                "montant_ht": 2200000,
                "tva_19_25_pct": 423500,
                "montant_ttc": 2623500,
                "statut": "PAYEE",
                "echeance": "15/08/2026",
                "devise": "XAF",
                "reference_paiement": "VIR-BGFI-772184",
                "date_paiement": "2026-08-14T09:12:00Z",
                "eligible_momo": False,
                "eligible_cb": False
            },
            {
                "id": "FAC-2026-0198",
                "dossier": "DOS-2026-00710",
                "desc": "Transit Export · Marchandises Agro",
                "montant_ht": 1750000,
                "tva_19_25_pct": 336875,
                "montant_ttc": 2086875,
                "statut": "PAYEE",
                "echeance": "20/07/2026",
                "devise": "XAF",
                "reference_paiement": "CB-VISA-482910",
                "date_paiement": "2026-07-18T16:45:00Z",
                "eligible_momo": False,
                "eligible_cb": False
            }
        ]

    @staticmethod
    def calculate_instant_quote(payload: Dict[str, Any]) -> Dict[str, Any]:
        """Calcule instantanément une cotation B2B pour le fret, manutention et transit."""
        poids_kg = float(payload.get("poids_estime_kg", 1000.0))
        volume_cbm = float(payload.get("volume_cbm", 5.0))
        type_fret = payload.get("type_fret", "MARITIME").upper()
        origine = payload.get("origine", "Port de Douala")
        destination = payload.get("destination", "Yaoundé")
        tc_type = payload.get("tc_type", "40FT")

        base_rate = 350000 if tc_type == "20FT" else 550000 if tc_type == "40FT" else 250000
        transit_taxe = 120000
        manutention = 85000
        assurance_valeur = max(25000, int(poids_kg * 15))
        distance_km = 260 if "yaoundé" in destination.lower() else 1100 if "ndjamena" in destination.lower() else 150
        fret_km = distance_km * (950 if tc_type == "40FT" else 750)

        total_ht = base_rate + transit_taxe + manutention + assurance_valeur + fret_km
        tva_19_25 = total_ht * 0.1925
        total_ttc = total_ht + tva_19_25

        quote_ref = f"DEV-{datetime.now().strftime('%Y%m')}-{random.randint(1000, 9999)}"

        return {
            "reference_devis": quote_ref,
            "date_emission": datetime.now().isoformat(),
            "validite_jours": 30,
            "lignes": [
                {"designation": f"Fret de base ({type_fret} - {tc_type})", "montant_ht": base_rate},
                {"designation": f"Transport routier corridor ({origine} → {destination}, {distance_km} km)", "montant_ht": fret_km},
                {"designation": "Passage portuaire & Acconage Douala", "montant_ht": manutention},
                {"designation": "Prestation transit douane DUM & GUCE", "montant_ht": transit_taxe},
                {"designation": "Assurance tiers fret sous douane", "montant_ht": assurance_valeur}
            ],
            "total_ht_xaf": round(total_ht),
            "tva_19_25_xaf": round(tva_19_25),
            "total_ttc_xaf": round(total_ttc),
            "devise": "XAF",
            "statut": "EMIS_EN_LIGNE"
        }

    @staticmethod
    def create_ebooking(payload: Dict[str, Any]) -> Dict[str, Any]:
        """Enregistre une réservation en ligne (e-Booking) d'enlèvement conteneur."""
        booking_ref = f"BKG-{datetime.now().strftime('%Y%m')}-{random.randint(100, 999)}"
        return {
            "booking_ref": booking_ref,
            "statut": "CONFIRME",
            "date_creation": datetime.now().isoformat(),
            "creneau_horaire": payload.get("creneau_horaire", "08:00 - 12:00"),
            "date_enlevement": payload.get("date_enlevement", (datetime.now() + timedelta(days=2)).strftime("%Y-%m-%d")),
            "terminal": payload.get("terminal", "DIT Terminal Douala"),
            "consignataire": payload.get("consignataire", "MAERSK"),
            "conteneur_no": payload.get("conteneur_no", "MSKU0000000"),
            "camion_immatriculation": payload.get("camion_immatriculation", "LT-TR-842-AA"),
            "chauffeur": payload.get("chauffeur", "Chauffeur assigné par EVO-LOG"),
            "message": "Réservation e-Booking confirmée. Bon d'enlèvement transmis au terminal portuaire."
        }

    @staticmethod
    def track_cargo(query: str) -> Dict[str, Any]:
        """Tracking temps réel par conteneur ISO 6346 ou par BL."""
        clean_q = query.strip().upper()
        now = datetime.now()

        return {
            "query": clean_q,
            "type_recherche": "CONTENEUR_ISO" if len(clean_q) == 11 else "BILL_OF_LADING",
            "statut_actuel": "EN_TRANSIT_SOUS_DOUANE",
            "position_actuelle": "Corridor Douala-Edéa PK 45",
            "navire": "MSC CRISTINA - VOY 2608W",
            "port_dechargement": "Port Autonome de Douala (PAD)",
            "terminal_acconage": "DIT Terminal Quai 15",
            "compagnie_maritime": "MSC MEDITERRANEAN SHIPPING",
            "franchise_surestaries": {
                "jours_accordes": 14,
                "jours_ecoules": 8,
                "jours_restants": 6,
                "alerte_depassement": False,
                "cout_par_jour_supplementaire_xaf": 35000
            },
            "jalons": [
                {"etape": "Arrivée Navire en Rade de Douala", "date": (now - timedelta(days=6)).strftime("%d/%m/%Y %H:%M"), "statut": "DONE"},
                {"etape": "Accostage Quai 15 & Débarquement Conteneur", "date": (now - timedelta(days=5)).strftime("%d/%m/%Y %H:%M"), "statut": "DONE"},
                {"etape": "Transfert sous Douane MAD EVO-LOG Bassa", "date": (now - timedelta(days=3)).strftime("%d/%m/%Y %H:%M"), "statut": "DONE"},
                {"etape": "Visite Douanière & Scanner GUCE", "date": (now - timedelta(days=1)).strftime("%d/%m/%Y %H:%M"), "statut": "DONE"},
                {"etape": "Octroi Bon à Enlever (BAE) Douane", "date": (now - timedelta(hours=8)).strftime("%d/%m/%Y %H:%M"), "statut": "DONE"},
                {"etape": "Chargement sur Tracteur Routier EVO-LOG", "date": (now - timedelta(hours=3)).strftime("%d/%m/%Y %H:%M"), "statut": "DONE"},
                {"etape": "En route vers destination finale (Entrepôt Client)", "date": "En cours", "statut": "IN_PROGRESS"},
                {"etape": "Livraison Client & Signature e-POD sur Tablette", "date": "Prévu demain 10:00", "statut": "PENDING"},
                {"etape": "Restitution Conteneur Vide au Parc Armateur", "date": "Prévu J+2", "statut": "PENDING"}
            ]
        }

    @staticmethod
    def process_checkout_payment(payload: Dict[str, Any]) -> Dict[str, Any]:
        """Paiement en ligne sécurisé (MTN/Orange MoMo, Carte Bancaire, Virement)."""
        facture_id = payload.get("facture_id", "FAC-2026-0284")
        mode = payload.get("mode_paiement", "MOMO_MTN")
        montant = payload.get("montant_xaf", 5783625)
        telephone = payload.get("telephone", "+237 6 70 00 00 00")

        tx_id = f"PAY-{mode[:4]}-{datetime.now().strftime('%Y%m%d%H%M%S')}-{random.randint(100, 999)}"

        return {
            "transaction_id": tx_id,
            "facture_id": facture_id,
            "montant_paye_xaf": montant,
            "mode_paiement": mode,
            "telephone_ou_compte": telephone,
            "statut_paiement": "SUCCES_VALIDE",
            "date_reglement": datetime.now().isoformat(),
            "quittance_recu_url": f"/receipts/{tx_id}.pdf",
            "bon_de_sortie_debloque": True,
            "message": f"Paiement de {montant:,} XAF validé avec succès. Quittance officielle émise et Bon de Sortie débloqué automatiquement."
        }

    @staticmethod
    def get_notification_preferences(client_id: int) -> Dict[str, Any]:
        return {
            "client_id": client_id,
            "alertes_sms": True,
            "telephone_sms": "+237 6 99 11 22 33",
            "alertes_whatsapp": True,
            "telephone_whatsapp": "+237 6 77 88 99 00",
            "alertes_email": True,
            "email_notifications": "direction.logistique@bocom-ci.cm",
            "declencheurs": {
                "sur_bae_douane": True,
                "sur_depart_camion": True,
                "sur_arrivee_site": True,
                "sur_franchise_surestaries_alerte_j3": True,
                "sur_emission_facture": True
            }
        }

    @staticmethod
    def update_notification_preferences(client_id: int, prefs: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "success": True,
            "message": "Préférences de notification mises à jour avec succès",
            "preferences": prefs
        }
