# Chapitre 2 — corrigés

Les deux exercices modifient le catalogue : les versions complètes sont dans `lab_core/` ci-dessous.

## Exercice 2.1 — La technique d'analyse

- `models/lab_analysis.py` : `method = fields.Selection([('auto', 'Automate'), ('manual', 'Manuelle')], 'Technique',
  default='auto')`.
- `views/lab_catalog_views.xml` : `<field name="method"/>` dans le groupe « Analyse » du formulaire.
- Nouveau champ : redémarrer puis `-u lab_core`. Les 30 analyses existantes reçoivent la valeur par défaut `auto` à la
  création de la colonne.

Critère : le formulaire d'une analyse affiche « Technique : Automate » et la valeur se modifie.

## Exercice 2.2 — Les bornes femme visibles par défaut

Dans la vue liste, `optional="show"` au lieu de `optional="hide"` sur `ref_min_female` et `ref_max_female` : les deux
colonnes s'affichent d'emblée, et restent masquables par le sélecteur de colonnes. Vue seule : `-u lab_core`.

Critère : à la première ouverture de **Configuration › Analyses**, les colonnes « Borne basse (femme) » et « Borne
haute (femme) » sont visibles.
