# Labo Horizon — une suite Odoo 20 construite chapitre par chapitre

Code source du livre **« Développer sur Odoo 20 — Le parcours pratique pour devenir développeur Odoo
opérationnel »** (OdooSkills, 2026) : <https://odooskills.com>.

Labo Horizon est un laboratoire d'analyses médicales **fictif** : patients, prescripteurs, mutuelles et résultats sont
inventés. Le code n'est pas destiné à un usage médical réel.

## Un tag par chapitre

| Tag | Contenu |
|---|---|
| `ch00` | dépôt vide : point de départ du chapitre 1 |
| `ch01` … `ch12` | module `lab_core` (Partie I), état à la fin de chaque chapitre |
| `ch13` … `ch15` | + module `lab_billing` (Partie II) : contacts, articles, mutuelles, factures |

```bash
git clone https://github.com/stagenie/labo-horizon.git
cd labo-horizon && git checkout ch01
```

À partir de `ch13`, le dépôt contient deux modules : installez `lab_billing`, qui installe `lab_core` et la
Facturation s'ils manquent.

Les solutions des exercices sont dans `solutions/chNN/` (fichiers complets, à comparer avec les vôtres).

## Prérequis

Odoo 20.0 Community, Python 3.12, PostgreSQL 16. Ajouter ce dossier à `addons_path`.

## Licence

LGPL-3 (voir `LICENSE`).
