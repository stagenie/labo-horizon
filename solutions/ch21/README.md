# Chapitre 21 — corrigés

Les versions complètes des fichiers modifiés ou ajoutés sont dans `lab_billing/` et `lab_core/` ci-dessous. Les deux
fichiers `tests/__init__.py` sont complets : ils remplacent ceux des modules et importent un fichier de test de plus.

## Exercice 21.1 — Un libellé de facture, test d'abord

La facture de la mutuelle porte, sur chaque ligne, « part mutuelle, 70.0 % » : le taux est un nombre décimal, écrit
tel quel. Le test d'abord : `tests/test_lab_invoice_label.py` facture une demande pour une mutuelle à 70 % et une à
65,5 %, en français, et attend « part mutuelle, 70 % » et « part mutuelle, 65,5 % ». Sur le code du chapitre, il est
rouge :

```text
FAIL: TestLabInvoiceLabel.test_insurer_line_label_decimal_rate
AssertionError: '(part mutuelle, 65,5 %)' not found in 'CHOL — Cholestérol total (part mutuelle, 65.5 %)'
FAIL: TestLabInvoiceLabel.test_insurer_line_label_integer_rate
AssertionError: '(part mutuelle, 70 %)' not found in 'CHOL — Cholestérol total (part mutuelle, 70.0 %)'
```

Le correctif, dans `lab_billing/models/lab_request.py`, écrit le taux avec le format `:g` (sans zéro inutile) et le
séparateur décimal de la langue de l'utilisateur, lu par `res.lang._get_data(code=…).decimal_point`. Ce séparateur
est vide si la langue de l'utilisateur n'est pas installée : le premier essai du corrigé a cassé neuf tests de
facturation sur `replace() argument 2 must be str, not bool`, d'où le repli `or '.'`. La suite complète a montré
l'erreur ; le test de l'exercice seul ne l'aurait pas vue.

Critères : les tests `test_insurer_line_label_integer_rate` et `test_insurer_line_label_decimal_rate` passent, et toute
la suite reste verte.

## Exercice 21.2 — Tester un formulaire avec `Form`

`tests/test_lab_form.py` remplit une nouvelle demande comme à l'écran, avec `Form` (`from odoo.tests import Form`) :
le patient, puis le bilan lipidique. L'onchange de `panel_ids` crée aussitôt les quatre lignes de résultats, alors que
la demande n'existe pas encore en base ; `form.save()` l'enregistre avec ses lignes CHOL, HDL, LDL et TG.

Ce test décrit un comportement qui existe déjà depuis la Partie I : il est vert dès le premier lancement. C'est un
test de caractérisation, qui protège l'onchange d'une modification future.

Critère : le test `test_form_panel_creates_result_lines` passe.
