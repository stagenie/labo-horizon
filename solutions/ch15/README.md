# Chapitre 15 — corrigés

Les versions complètes des fichiers modifiés sont dans `lab_billing/` ci-dessous.

## Exercice 15.1 — Facturer plusieurs demandes depuis la liste

Une action serveur, comme « Valider les demandes » au chapitre 11, dans un nouveau fichier de données
`data/lab_billing_actions.xml`, déclaré dans le manifeste après les vues :

```xml
<record id="action_server_lab_request_invoice" model="ir.actions.server">
    <field name="name">Facturer les demandes</field>
    <field name="model_id" ref="lab_core.model_lab_request"/>
    <field name="binding_model_id" ref="lab_core.model_lab_request"/>
    <field name="binding_view_types">list</field>
    <field name="group_ids" eval="[Command.link(ref('account.group_account_invoice'))]"/>
    <field name="state">code</field>
    <field name="code">records._create_invoices()</field>
</record>
```

Le code appelle `_create_invoices`, pas `action_create_invoices` : l'action serveur n'a pas à ouvrir la liste des
factures. Une demande non validée ou déjà facturée dans la sélection arrête tout, avec son message : aucune facture
n'est créée à moitié, la transaction est annulée.

Critère : le test `test_server_action_invoices_selection` passe.

## Exercice 15.2 — Une note dans le fil de la demande

Dans `_create_invoices`, après le lien entre la demande et ses factures :

```python
from markupsafe import Markup
...
partners = Markup(", ").join(Markup("<b>%s</b>") % move.partner_id.name for move in new_moves)
request.message_post(body=Markup(_("Factures brouillon créées pour %s.")) % partners)
```

Une facture brouillon n'a pas encore de numéro (il est attribué à la comptabilisation) : la note nomme donc les
clients facturés. Le piège du chapitre 8 revient : sans `Markup`, `message_post` échapperait les balises `<b>` ; avec
`Markup`, l'opérateur `%` échappe le nom inséré, et un nom contenant `<` reste du texte.

Critère : le test `test_invoicing_posts_note` passe.
