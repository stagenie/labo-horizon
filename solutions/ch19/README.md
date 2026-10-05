# Chapitre 19 — corrigés

Les versions complètes des fichiers modifiés ou ajoutés sont dans `lab_owl/` ci-dessous.

## Exercice 19.1 — La liste des résultats hors norme

Une vue liste de `lab.result` (`lab_result_view_list_out_of_range`) affiche la demande, l'analyse, le résultat, l'unité,
la jauge et l'interprétation. L'action « Résultats hors norme » l'ouvre avec le domaine
`[('flag', 'in', ('low', 'high'))]`, et un menu sous Laboratoire la propose aux techniciens et aux biologistes
(`groups="lab_core.group_lab_technician"` : le biologiste hérite du technicien). La liste est en lecture seule
(`create="0" edit="0"`) : un résultat se saisit dans sa demande.

La jauge fonctionne alors que la liste n'affiche ni Min ni Max : le widget déclare ces champs dans
`fieldDependencies`, le client web les charge de lui-même.

**Attention au piège du § 19.8.** Le corrigé ajoute une **nouvelle** vue au module. Sur une base où `website` est
installé (la vôtre depuis le chapitre 16), `-u lab_owl` échoue alors sur
`NotNullViolation: null value in column "visibility" of relation "ir_ui_view"`. Contournement : désinstaller
`lab_owl` (Applications › Labo Horizon — Aller plus loin › Désinstaller), puis l'installer de nouveau. Une base neuve
(`-i`) n'est pas concernée.

Critères : les tests `test_out_of_range_action_domain` et `test_out_of_range_list_uses_gauge` passent.

## Exercice 19.2 — Une jauge compacte

Le composant reçoit une propriété de plus, `compact`, déclarée avec les autres :
`useProps({ ...standardFieldProps, compact: t.boolean().optional(false) })`. La fonction `extractProps` de
`labGaugeField` la lit dans les options de la vue (`options="{'compact': True}"`) ; le gabarit ajoute alors la classe
`o_lab_gauge_compact`, que le SCSS réduit à 80 px.

Le test JavaScript `static/tests/lab_gauge_compact.test.js` monte une liste avec et sans l'option ; le manifeste
déclare le dossier des tests dans le bundle `web.assets_unit_tests`. Le test se lance à l'installation du module avec
`--test-tags /lab_owl` (paquet Python `websocket-client` requis, voir le chapitre 21).

Critère : les tests hoot `compact option narrows the gauge` et `gauge is wide by default` passent.
