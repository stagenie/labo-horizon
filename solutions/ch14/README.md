# Chapitre 14 — corrigés

Les versions complètes des fichiers modifiés sont dans `lab_billing/` ci-dessous.

## Exercice 14.1 — La mutuelle dans la liste et la recherche des patients

Deux vues héritées de plus dans `views/lab_patient_views.xml`. La liste reçoit une colonne après l'e-mail ; la
recherche, un filtre après « Hommes » :

```xml
<field name="email" position="after">
    <field name="insurer_id" optional="show"/>
</field>
```

```xml
<filter name="male" position="after">
    <filter name="no_insurer" string="Sans mutuelle" domain="[('insurer_id', '=', False)]"/>
</filter>
```

`optional="show"` rend la colonne masquable par l'utilisateur, visible par défaut. Le filtre s'ancre sur le `name`
d'un filtre existant : la même règle que pour les champs.

Critères : après la mise à jour du module, la liste Laboratoire › Patients montre la colonne Mutuelle après
l'e-mail, et le filtre « Sans mutuelle » ne laisse que les trois patients de démonstration sans mutuelle : Amel
Cherif, Chloé Garnier et Paul Mercier.

## Exercice 14.2 — Le bouton « Demandes » sur la fiche contact

Un champ calculé non stocké, `lab_request_count`, compte les demandes des fiches patient du contact ; la méthode
`action_view_lab_requests` ouvre leur liste. Dans la vue, le bouton entre **dans** la boîte à boutons de la fiche
contact, repérée par son `name` :

```xml
<div name="button_box" position="inside">
    <button name="action_view_lab_requests" type="object" class="oe_stat_button" icon="science"
            invisible="not lab_request_count" groups="lab_core.group_lab_secretary">
        <field name="lab_request_count" widget="statinfo" string="Demandes"/>
    </button>
</div>
```

`icon="science"` est un nom d'icône d'Odoo 20 (plus de FontAwesome) ; `groups` retire le bouton aux utilisateurs
sans accès au laboratoire.

Critère : sur le contact d'un patient, le bouton Demandes affiche le nombre de ses demandes et ouvre leur liste.
À ce stade, aucun patient n'a encore de contact (il naît à la première facture, chapitre 15) ; le shell en crée un
pour vérifier le calcul et l'action :

```python
>>> c = env.ref('lab_core.patient_demo_1')._get_or_create_partner()
>>> c.lab_request_count
1
>>> c.action_view_lab_requests()['domain']
[('patient_id', 'in', [1])]
>>> env.cr.rollback()
```

Julie Bernard a une demande sur une base de démonstration neuve ; le nombre suit celles créées depuis.
