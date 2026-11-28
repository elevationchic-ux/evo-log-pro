"""117 : recolle les FK de livraisons / missions_sous_traitant sur les tables réelles.

Constat (audit transport_avance) : les tables ont été créées par une
génération antérieure des modèles. Leurs FK pointent vers des tables qui
ne correspondent plus aux modèles actuels :

  livraisons.tournee_id -> tournees.id   (alors que Tournée = tours.id)
  livraisons.client_id  -> tiers.id      (alors que le modèle vise clients.id)
  missions_sous_traitant.contrat_id -> contrats_sous_traitant.id
                                       (alors que le modèle vise
                                        contrats_sous_traitants.id)
  missions_sous_traitant.client_id était typé DATE (modèle corrigé :
                                       Integer FK clients.id)

Conséquence : tout INSERT via les endpoints réparés échouait en
FOREIGN KEY constraint failed. Cette migration recrée les deux tables
avec les colonnes existantes (union ancienne + nouvelle génération,
données préservées) et les FK conformes aux modèles.

SQLite : rebuild table (create/insert/drop/rename) — seul moyen de
changer une FK. PostgreSQL : DROP/ADD CONSTRAINT par nom conventionnel.
Idempotent : les rebuilds vérifient d'abord la cible actuelle des FK.
"""
from alembic import op
import sqlalchemy as sa

revision = "117_transport_avance_fks"
down_revision = "116_rbac_terrain_support"
branch_labels = None
depends_on = None


def _fk_targets(bind, table: str):
    """Retourne {colonne: table_cible} des FK existantes."""
    if bind.dialect.name == "sqlite":
        rows = bind.execute(sa.text(f"PRAGMA foreign_key_list({table})")).fetchall()
        return {r[3]: r[2] for r in rows}
    rows = bind.execute(sa.text(
        "SELECT kcu.column_name, ccu.table_name FROM information_schema.table_constraints tc "
        "JOIN information_schema.key_column_usage kcu ON tc.constraint_name = kcu.constraint_name "
        "JOIN information_schema.constraint_column_usage ccu ON tc.constraint_name = ccu.constraint_name "
        "WHERE tc.table_name = :t AND tc.constraint_type = 'FOREIGN KEY'"
    ), {"t": table}).fetchall()
    return {r[0]: r[1] for r in rows}


def _rebuild_sqlite(table: str, cols_ddl: str, col_list: str, inserts: str,
                    fks: str, indexes: str = ""):
    bind = op.get_bind()
    bind.execute(sa.text(f"ALTER TABLE {table} RENAME TO {table}__old117"))
    ddl = cols_ddl if not fks else f"{cols_ddl}, {fks}"
    bind.execute(sa.text(f"CREATE TABLE {table} ({ddl})"))
    bind.execute(sa.text(
        f"INSERT INTO {table} ({col_list}) SELECT {inserts} FROM {table}__old117"
    ))
    bind.execute(sa.text(f"DROP TABLE {table}__old117"))
    if indexes:
        for stmt in indexes.split(";"):
            stmt = stmt.strip()
            if stmt:
                bind.execute(sa.text(stmt))


def _fix_postgres(table: str, changes: dict):
    """changes: {colonne: (ancienne_cible, nouvelle_cible)}"""
    bind = op.get_bind()
    for col, (old_target, new_target) in changes.items():
        cname = f"{table}_{col}_fkey"
        bind.execute(sa.text(
            f"ALTER TABLE {table} DROP CONSTRAINT IF EXISTS {cname}"
        ))
        bind.execute(sa.text(
            f"ALTER TABLE {table} ADD CONSTRAINT {cname} "
            f"FOREIGN KEY ({col}) REFERENCES {new_target}(id)"
        ))


def upgrade():
    bind = op.get_bind()
    dialect = bind.dialect.name

    # --- livraisons ---
    targets = _fk_targets(bind, "livraisons")
    need = (targets.get("tournee_id") != "tours" or targets.get("client_id") != "clients")
    if need:
        if dialect == "sqlite":
            _rebuild_sqlite(
                "livraisons",
                cols_ddl=(
                    "id INTEGER PRIMARY KEY, "
                    "tournee_id INTEGER NOT NULL REFERENCES tours(id), "
                    "client_id INTEGER NOT NULL REFERENCES clients(id), "
                    "adresse VARCHAR, ordre_arret INTEGER, "
                    "fenetre_horaire_debut DATETIME, fenetre_horaire_fin DATETIME, "
                    "statut VARCHAR, date_livraison_reelle DATETIME, "
                    "signature VARCHAR, photo_preuve VARCHAR, "
                    "numero_livraison VARCHAR(50), point_dechargement VARCHAR(200), "
                    "heure_debut_prevue VARCHAR(10), heure_fin_prevue VARCHAR(10), "
                    "heure_debut_reelle VARCHAR(10), heure_fin_reelle VARCHAR(10), "
                    "nombre_colis INTEGER, poids_total NUMERIC, "
                    "preuve_livraison TEXT, commentaire TEXT, created_at DATETIME"
                ),
                col_list=(
                    "id, tournee_id, client_id, adresse, ordre_arret, "
                    "fenetre_horaire_debut, fenetre_horaire_fin, statut, "
                    "date_livraison_reelle, signature, photo_preuve, numero_livraison, "
                    "point_dechargement, heure_debut_prevue, heure_fin_prevue, "
                    "heure_debut_reelle, heure_fin_reelle, nombre_colis, poids_total, "
                    "preuve_livraison, commentaire, created_at"
                ),
                inserts=(
                    "id, tournee_id, client_id, adresse, ordre_arret, "
                    "fenetre_horaire_debut, fenetre_horaire_fin, statut, "
                    "date_livraison_reelle, signature, photo_preuve, numero_livraison, "
                    "point_dechargement, heure_debut_prevue, heure_fin_prevue, "
                    "heure_debut_reelle, heure_fin_reelle, nombre_colis, poids_total, "
                    "preuve_livraison, commentaire, created_at"
                ),
                fks=""
            )
        else:
            _fix_postgres("livraisons", {
                "tournee_id": ("tournees", "tours"),
                "client_id": ("tiers", "clients"),
            })

    # --- pods ---
    # Effet de bord SQLite : ALTER TABLE ... RENAME propage les FK des tables
    # dépendantes vers le nom temporaire. Après le rebuild de livraisons,
    # pods.livraison_id pointe vers livraisons__old117 (table supprimée) :
    # tout INSERT dans pods échoue. On reconstruit pods avec la bonne cible.
    if dialect == "sqlite":
        targets = _fk_targets(bind, "pods")
        if targets.get("livraison_id") != "livraisons":
            _rebuild_sqlite(
                "pods",
                cols_ddl=(
                    "id INTEGER PRIMARY KEY, "
                    "numero_pod VARCHAR(50) NOT NULL, "
                    "livraison_id INTEGER NOT NULL REFERENCES livraisons(id), "
                    "date_pod DATETIME DEFAULT CURRENT_TIMESTAMP, "
                    "statut VARCHAR(20), "
                    "signature_client TEXT, photo_marchandise TEXT, photo_signature TEXT, "
                    "coordonnes_livraison VARCHAR(200), "
                    "horodatage DATETIME, nom_receveur VARCHAR(100), "
                    "fonction_receveur VARCHAR(100), commentaire_client TEXT, "
                    "commentaire_chauffeur TEXT, conditions_livraison TEXT, "
                    "documents_attaches TEXT, "
                    "valide_par INTEGER REFERENCES users(id), "
                    "date_validation DATETIME, hash_preuve VARCHAR(255), "
                    "created_at DATETIME DEFAULT CURRENT_TIMESTAMP, "
                    "updated_at DATETIME, coordonnees_livraison VARCHAR(200)"
                ),
                col_list=(
                    "id, numero_pod, livraison_id, date_pod, statut, signature_client, "
                    "photo_marchandise, photo_signature, coordonnes_livraison, horodatage, "
                    "nom_receveur, fonction_receveur, commentaire_client, "
                    "commentaire_chauffeur, conditions_livraison, documents_attaches, "
                    "valide_par, date_validation, hash_preuve, created_at, updated_at, "
                    "coordonnees_livraison"
                ),
                inserts=(
                    "id, numero_pod, livraison_id, date_pod, statut, signature_client, "
                    "photo_marchandise, photo_signature, coordonnes_livraison, horodatage, "
                    "nom_receveur, fonction_receveur, commentaire_client, "
                    "commentaire_chauffeur, conditions_livraison, documents_attaches, "
                    "valide_par, date_validation, hash_preuve, created_at, updated_at, "
                    "coordonnees_livraison"
                ),
                fks=""
            )
    else:
        targets = _fk_targets(bind, "pods")
        if targets.get("livraison_id") != "livraisons":
            _fix_postgres("pods", {"livraison_id": (None, "livraisons")})

    # --- documents_pod ---
    # Même cascade : pod_id pointait vers pods__old117 après le rebuild pods.
    if dialect == "sqlite":
        targets = _fk_targets(bind, "documents_pod")
        if targets.get("pod_id") != "pods":
            _rebuild_sqlite(
                "documents_pod",
                cols_ddl=(
                    "id INTEGER PRIMARY KEY, "
                    "pod_id INTEGER NOT NULL REFERENCES pods(id), "
                    "type_document VARCHAR(50), type_preuve VARCHAR(50), "
                    "nom_fichier VARCHAR(200), url_fichier VARCHAR(500), "
                    "taille_fichier INTEGER, type_mime VARCHAR(100), "
                    "hash_fichier VARCHAR(255), "
                    "upload_par INTEGER REFERENCES users(id), "
                    "created_at DATETIME DEFAULT CURRENT_TIMESTAMP"
                ),
                col_list=(
                    "id, pod_id, type_document, type_preuve, nom_fichier, url_fichier, "
                    "taille_fichier, type_mime, hash_fichier, upload_par, created_at"
                ),
                inserts=(
                    "id, pod_id, type_document, type_preuve, nom_fichier, url_fichier, "
                    "taille_fichier, type_mime, hash_fichier, upload_par, created_at"
                ),
                fks=""
            )
    else:
        targets = _fk_targets(bind, "documents_pod")
        if targets.get("pod_id") != "pods":
            _fix_postgres("documents_pod", {"pod_id": (None, "pods")})

    # --- missions_sous_traitant ---
    targets = _fk_targets(bind, "missions_sous_traitant")
    need = (
        targets.get("contrat_id") != "contrats_sous_traitants"
        or targets.get("sous_traitant_id") != "sous_traitants"
        or targets.get("client_id") != "clients"
    )
    if need:
        if dialect == "sqlite":
            _rebuild_sqlite(
                "missions_sous_traitant",
                cols_ddl=(
                    "id INTEGER PRIMARY KEY, "
                    "contrat_id INTEGER REFERENCES contrats_sous_traitants(id), "
                    "mission_id INTEGER, "
                    "kilometrage_estime FLOAT, kilometrage_reel FLOAT, "
                    "date_livraison_prevue DATE, date_livraison_reelle DATE, "
                    "date_creation DATETIME, statut VARCHAR, "
                    "numero_mission VARCHAR(50), "
                    "sous_traitant_id INTEGER REFERENCES sous_traitants(id), "
                    "client_id INTEGER REFERENCES clients(id), "
                    "date_mission DATE, point_depart VARCHAR(200), "
                    "point_arrivee VARCHAR(200), distance NUMERIC, "
                    "type_marchandise VARCHAR(100), poids NUMERIC, "
                    "cout_estime NUMERIC, cout_reel NUMERIC, "
                    "qualite_service NUMERIC, ponctualite NUMERIC, "
                    "notes TEXT, created_at DATETIME, updated_at DATETIME"
                ),
                col_list=(
                    "id, contrat_id, mission_id, kilometrage_estime, kilometrage_reel, "
                    "date_livraison_prevue, date_livraison_reelle, date_creation, statut, "
                    "numero_mission, sous_traitant_id, client_id, date_mission, "
                    "point_depart, point_arrivee, distance, type_marchandise, poids, "
                    "cout_estime, cout_reel, qualite_service, ponctualite, notes, "
                    "created_at, updated_at"
                ),
                inserts=(
                    "id, contrat_id, mission_id, kilometrage_estime, kilometrage_reel, "
                    "date_livraison_prevue, date_livraison_reelle, date_creation, statut, "
                    "numero_mission, sous_traitant_id, client_id, date_mission, "
                    "point_depart, point_arrivee, distance, type_marchandise, poids, "
                    "cout_estime, cout_reel, qualite_service, ponctualite, notes, "
                    "created_at, updated_at"
                ),
                fks=""
            )
        else:
            _fix_postgres("missions_sous_traitant", {
                "contrat_id": ("contrats_sous_traitant", "contrats_sous_traitants"),
                "sous_traitant_id": ("sous_traitants", "sous_traitants"),
                "client_id": (None, "clients"),
            })


def downgrade():
    # Les FK d'origine étaient erronées : on ne les restaure pas.
    pass
