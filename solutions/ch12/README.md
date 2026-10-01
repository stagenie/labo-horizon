# Chapitre 12 — corrigés

Les versions complètes des fichiers modifiés sont dans `lab_core/` ci-dessous.

## Exercice 12.1 — L'âge et le sexe sur l'étiquette de tube

Une ligne de plus dans le gabarit de l'étiquette, `report/lab_sample_label.xml`, sous le nom du patient :

```xml
<t t-out="s.patient_id.age"/> ans · <span t-field="s.patient_id.gender"/><br/>
```

`age` est un entier calculé : `t-out` suffit. `gender` est un champ de sélection : `t-out` afficherait la
clé technique (`female`), `t-field` affiche le libellé dans la langue du rapport (« Femme »). Le sexe compte à
la paillasse : il choisit les valeurs de référence de l'hémoglobine (chapitre 6).

Critère : le test `test_label_shows_age_and_gender` passe.

## Exercice 12.2 — Le nom du fichier PDF

Dans `report/lab_request_report.xml`, l'expression `print_report_name` devient :

```xml
<field name="print_report_name">'CR-%s-%s' % (object.patient_id.ref, object.name)</field>
```

L'expression est évaluée par le contrôleur de téléchargement avec `object` (l'enregistrement imprimé) et
`time` ; elle n'est utilisée que pour l'impression d'un seul document. Le nom obtenu, par exemple
`CR-PAT00003-DEM/2026/00012`, est nettoyé par le navigateur (la barre oblique n'est pas permise dans un nom de
fichier).

Critère : le test `test_report_file_name` passe.
