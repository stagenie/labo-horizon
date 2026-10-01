# Chapitre 9 — corrigés

Les versions complètes des fichiers modifiés sont dans `lab_core/` ci-dessous.

## Exercice 9.1 — Filtre « Mes validations »

Dans la vue de recherche des demandes, à côté des autres filtres :

```xml
<filter name="my_validations" string="Mes validations" domain="[('activity_user_id', '=', uid)]"/>
```

`activity_user_id` est un champ du mixin `mail.activity.mixin` : le responsable de la prochaine activité du
document. Il n'est pas stocké, mais il a une méthode de recherche, ce qui permet de l'employer dans un domaine.
`uid` est, dans un domaine de vue, l'identifiant de l'utilisateur connecté.

Critère : le test `test_my_validations_filter` passe ; le filtre ne montre que les demandes analysées dont
l'activité « Validation biologique » revient à l'utilisateur.

## Exercice 9.2 — Les demandes par semaine

Une vue graphique en courbe, ajoutée à l'action des demandes (`view_mode` se termine par `graph`) :

```xml
<graph string="Demandes par semaine" type="line">
    <field name="date_request" interval="week"/>
</graph>
```

Sans mesure déclarée, le graphique compte les enregistrements. `interval="week"` regroupe les dates par semaine
(les autres valeurs : `hour`, `day`, `month`, `quarter`, `year`).

Critère : `--test-tags /lab_core` passe ; l'icône graphique de la vue Demandes affiche une courbe par semaine.
