"""Restore le template facture.html.j2 (2880 octets NUL dans HEAD).

Le fichier corrompu resiste aux ecritures de l'editeur (outil Write/Delete
rapportant succes sans effet disque, sans doute a cause du contenu binaire
nul-patche). On ecrit donc via Python, source fiable au niveau octets.

Usage : python scripts/restore_facture_template.py
"""
from pathlib import Path

TPL = Path(__file__).resolve().parent.parent / "app" / "templates" / "pdf" / "facture.html.j2"


TEMPLATE = """<!DOCTYPE html>
<html lang="fr">
<head>
  <meta charset="utf-8"/>
  <title>Facture {{ facture.numero_facture }}</title>
  <style>
    @page { size: A4; margin: 18mm 15mm; }
    * { box-sizing: border-box; margin: 0; padding: 0; }
    body { font-family: Helvetica, Arial, sans-serif; font-size: 10.5pt; color: #1a1a2e; }
    .entete { display: flex; justify-content: space-between; align-items: flex-start;
              border-bottom: 3px solid #0f4c81; padding-bottom: 12px; margin-bottom: 18px; }
    .emetteur h1 { font-size: 15pt; color: #0f4c81; margin-bottom: 2px; }
    .emetteur .details { font-size: 8.5pt; color: #444; line-height: 1.45; }
    .titre { text-align: right; }
    .titre .doc { font-size: 17pt; font-weight: bold; color: #0f4c81; text-transform: uppercase; }
    .titre .numero { font-size: 11pt; margin-top: 3px; }
    .badge { display: inline-block; margin-top: 6px; padding: 3px 10px; border-radius: 10px;
             font-size: 8pt; font-weight: bold; text-transform: uppercase; }
    .badge-payee { background: #d9f2e3; color: #1e7d3e; }
    .badge-partiel { background: #fff3d6; color: #9a6b00; }
    .badge-brouillon { background: #e8e8ee; color: #555; }
    .badge-annulee { background: #fde3e3; color: #a02020; }
    .dates { font-size: 8.5pt; color: #444; margin-top: 6px; line-height: 1.5; }
    .parties { display: flex; justify-content: space-between; margin-bottom: 18px; gap: 24px; }
    .bloc { flex: 1; border: 1px solid #d8dce3; border-radius: 4px; padding: 10px 12px; }
    .bloc .label { font-size: 7.5pt; text-transform: uppercase; letter-spacing: .5px;
                   color: #0f4c81; font-weight: bold; margin-bottom: 4px; }
    .bloc .contenu { font-size: 9.5pt; line-height: 1.5; }
    table.lignes { width: 100%; border-collapse: collapse; margin-bottom: 14px; }
    table.lignes th { background: #0f4c81; color: #fff; font-size: 8pt; text-transform: uppercase;
                      padding: 6px 8px; text-align: left; }
    table.lignes td { padding: 6px 8px; font-size: 9pt; border-bottom: 1px solid #e3e6ea; }
    table.lignes .num { text-align: right; white-space: nowrap; }
    table.lignes th.num { text-align: right; }
    .totaux { width: 55%; margin-left: auto; margin-bottom: 16px; }
    .totaux .ligne { display: flex; justify-content: space-between; padding: 4px 8px;
                     font-size: 9.5pt; border-bottom: 1px solid #eceff3; }
    .totaux .ligne.ttc { background: #0f4c81; color: #fff; font-weight: bold;
                         font-size: 11pt; border-bottom: none; border-radius: 3px; }
    .lettres { font-size: 9.5pt; font-style: italic; margin-bottom: 14px; padding: 8px 10px;
               background: #f4f7fb; border-left: 3px solid #0f4c81; }
    .notes { font-size: 8.5pt; color: #444; line-height: 1.5; margin-bottom: 14px; }
    .mentions { font-size: 7.5pt; color: #666; line-height: 1.5; border-top: 1px solid #d8dce3;
                padding-top: 8px; margin-top: 10px; }
    .signature { text-align: right; margin-top: 26px; font-size: 9pt; color: #444; }
    .signature .zone { display: inline-block; min-width: 180px; border-top: 1px solid #999;
                       padding-top: 4px; }
    .vide { text-align: center; color: #888; font-style: italic; padding: 14px; }
  </style>
</head>
<body>
  <div class="entete">
    <div class="emetteur">
      {% if company %}
        <h1>{{ company.nom or company.sigle or 'Entreprise' }}</h1>
        <div class="details">
          {% if company.sigle and company.nom and company.sigle != company.nom %}({{ company.sigle }})<br/>{% endif %}
          {% if company.legal_form %}{{ company.legal_form }}<br/>{% endif %}
          {% if company.capital_social %}Capital : {{ "{:,.2f}".format(company.capital_social | float) }} FCFA<br/>{% endif %}
          {% if company.adresse %}{{ company.adresse }}{% if company.ville %}, {{ company.ville }}{% endif %}<br/>{% endif %}
          {% if company.telephone %}Tél. : {{ company.telephone }}<br/>{% endif %}
          {% if company.email %}{{ company.email }}<br/>{% endif %}
          {% if company.tax_id %}NIF : {{ company.tax_id }}<br/>{% endif %}
          {% if company.rccm %}RCCM : {{ company.rccm }}<br/>{% endif %}
          {% if company.rib %}RIB : {{ company.rib }}<br/>{% endif %}
        </div>
      {% else %}
        <h1>Facture</h1>
        <div class="details">Profil émetteur (entreprise) non renseigné dans le système.</div>
      {% endif %}
    </div>
    <div class="titre">
      <div class="doc">
        {% if facture.type_facture and 'avoir' in facture.type_facture|string %}Avoir{% else %}Facture{% endif %}
      </div>
      <div class="numero">N° {{ facture.numero_facture }}</div>
      {% if facture.statut == 'payee' %}
        <span class="badge badge-payee">Payée</span>
      {% elif facture.statut == 'payee_partiel' %}
        <span class="badge badge-partiel">Payée partiellement</span>
      {% elif facture.statut == 'brouillon' %}
        <span class="badge badge-brouillon">Brouillon</span>
      {% elif facture.statut == 'annulee' %}
        <span class="badge badge-annulee">Annulée</span>
      {% elif facture.statut in ('impayee', 'en_retard') %}
        <span class="badge badge-annulee">Impayée</span>
      {% elif facture.statut %}
        <span class="badge badge-brouillon">{{ facture.statut }}</span>
      {% endif %}
      <div class="dates">
        Émise le : {{ facture.date_emission or '' }}<br/>
        {% if facture.date_echeance %}Échéance : {{ facture.date_echeance }}<br/>{% endif %}
        {% if facture.date_paiement %}Payée le : {{ facture.date_paiement }}<br/>{% endif %}
      </div>
    </div>
  </div>

  <div class="parties">
    <div class="bloc">
      <div class="label">Client</div>
      <div class="contenu">
        {% if client %}
          <strong>{{ client.name or '' }}</strong><br/>
          {% if client.legal_form %}{{ client.legal_form }}<br/>{% endif %}
          {% if client.address %}{{ client.address }}{% if client.city %}, {{ client.city }}{% endif %}<br/>{% endif %}
          {% if client.tax_id %}NIF : {{ client.tax_id }}<br/>{% endif %}
          {% if client.email %}{{ client.email }}<br/>{% endif %}
          {% if client.phone %}Tél. : {{ client.phone }}{% endif %}
        {% else %}
          <em>Client non renseigné</em>
        {% endif %}
      </div>
    </div>
  </div>

  <table class="lignes">
    <thead>
      <tr>
        <th style="width: 38%">Désignation</th>
        <th class="num">Qté</th>
        <th>Unité</th>
        <th class="num">P.U. HT</th>
        <th class="num">Montant HT</th>
        <th class="num">TVA</th>
        <th class="num">Montant TTC</th>
      </tr>
    </thead>
    <tbody>
      {% for ligne in lignes %}
      <tr>
        <td>
          {{ ligne.designation or 'Ligne sans désignation' }}
          {% if ligne.description %}<br/><span style="font-size: 8pt; color: #666;">{{ ligne.description }}</span>{% endif %}
        </td>
        <td class="num">{{ "{:g}".format(ligne.quantite | float) }}</td>
        <td>{{ ligne.unite or '' }}</td>
        <td class="num">{{ "{:,.2f}".format(ligne.prix_unitaire_ht | float) }}</td>
        <td class="num">{{ "{:,.2f}".format(ligne.montant_ht | float) }}</td>
        <td class="num">{{ "{:g}".format(ligne.taux_tva | float if ligne.taux_tva is not none else taux_tva) }}%</td>
        <td class="num">{{ "{:,.2f}".format(ligne.montant_ttc | float) }}</td>
      </tr>
      {% else %}
      <tr><td colspan="7" class="vide">Aucune ligne de détail enregistrée sur cette facture.</td></tr>
      {% endfor %}
    </tbody>
  </table>

  <div class="totaux">
    <div class="ligne"><span>Total HT</span><span>{{ "{:,.2f}".format(facture.montant_ht | float) }} {{ facture.devise or 'XAF' }}</span></div>
    <div class="ligne"><span>TVA ({{ "{:g}".format(facture.taux_tva | float) }} %)</span><span>{{ "{:,.2f}".format(facture.montant_tva | float) }} {{ facture.devise or 'XAF' }}</span></div>
    <div class="ligne ttc"><span>Total TTC</span><span>{{ "{:,.2f}".format(facture.montant_ttc | float) }} {{ facture.devise or 'XAF' }}</span></div>
    {% if facture.reglement_partiel and facture.reglement_partiel | float > 0 %}
      <div class="ligne"><span>Acomptes / règlements reçus</span><span>- {{ "{:,.2f}".format(facture.reglement_partiel | float) }}</span></div>
    {% endif %}
    {% if facture.solde_restant and facture.solde_restant | float > 0 %}
      <div class="ligne"><span>Solde restant dû</span><span>{{ "{:,.2f}".format(facture.solde_restant | float) }}</span></div>
    {% endif %}
  </div>

  {% if montant_en_lettres %}
  <div class="lettres">
    Arrêtée la présente facture à la somme de : {{ montant_en_lettres }}.
  </div>
  {% endif %}

  {% if facture.conditions_paiement or facture.notes %}
  <div class="notes">
    {% if facture.conditions_paiement %}<strong>Conditions de règlement :</strong> {{ facture.conditions_paiement }}<br/>{% endif %}
    {% if facture.notes %}<strong>Notes :</strong> {{ facture.notes }}{% endif %}
  </div>
  {% endif %}

  <div class="mentions">
    {% if facture.statut == 'brouillon' %}
      <strong>Document provisoire (brouillon)  ne constitue pas une facture définitive opposable.</strong><br/>
    {% endif %}
    Facture émise conformément à la réglementation OHADA et aux dispositions du Code général des impôts
    du Cameroun (art. 289 ter et suivants). TVA applicable : {{ "{:g}".format(facture.taux_tva | float) }} %.
    En cas de retard de paiement, des pénalités et majorations seront appliquées conformément aux
    dispositions légales en vigueur.
  </div>

  <div class="signature">
    <span class="zone">Cachet et signature</span>
  </div>
</body>
</html>
"""


def main() -> None:
    TPL.write_bytes(TEMPLATE.encode("utf-8"))
    b = TPL.read_bytes()
    assert b.count(b"\x00") == 0, "Le fichier contient encore des octets NUL"
    print(f"OK : {TPL} restauré ({len(b)} octets, {b.decode('utf-8').count(chr(10)) + 1} lignes)")


if __name__ == "__main__":
    main()
