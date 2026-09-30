# Chapitre 1 — corrigés

Les deux exercices modifient les mêmes fichiers : les versions complètes sont dans `lab_core/` ci-dessous, à comparer
avec les vôtres (`diff -u ~/odoo20/labo-horizon/lab_core/views/lab_patient_views.xml solutions/ch01/lab_core/views/lab_patient_views.xml`).

## Exercice 1.1 — L'e-mail du patient

- `models/lab_patient.py` : `email = fields.Char('E-mail')`.
- `views/lab_patient_views.xml` : `<field name="email"/>` dans la liste, `<field name="email" widget="email"/>` dans le
  formulaire (le widget rend l'adresse cliquable).
- Nouveau champ Python **et** vue modifiée : redémarrer puis `-u lab_core` (la colonne est créée à la mise à jour).

Critère : l'e-mail saisi sur la fiche s'enregistre et apparaît dans la liste.

## Exercice 1.2 — Trier par date de naissance

`<list default_order="birthdate desc">` : l'ordre de la vue l'emporte sur `_order` du modèle, qui reste `name` partout
ailleurs (recherches, listes déroulantes). Seule la vue change : `-u lab_core` suffit (ou un simple rechargement avec
`dev_mode = xml`).

Critère : le patient le plus jeune (Chloé Garnier, née en 2012) est en tête de liste.
