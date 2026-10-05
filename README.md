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
| `ch16` … `ch18` | + module `lab_portal` (Partie III) : portail patient, rendez-vous sur le site, courriels, action planifiée |
| `ch19` … `ch21` | + module `lab_owl` (Partie IV) : jauge OWL 3, API JSON-2 pour les automates (`scripts/automate.py`), tests |

```bash
git clone https://github.com/stagenie/labo-horizon.git
cd labo-horizon && git checkout ch01
```

Chaque module installe ceux dont il dépend : `lab_billing` installe `lab_core` et la Facturation ; `lab_portal`
installe `lab_billing`, le portail, le site web et le calendrier ; `lab_owl` ne dépend que de `lab_core` et du client
web. Au tag `ch21`, le dépôt contient les quatre modules.

`scripts/automate.py` simule un automate d'analyses qui envoie ses résultats par l'API (chapitre 20) ; la clé API se
lit dans la variable d'environnement `LAB_API_KEY`. Les tests JavaScript (chapitre 21) demandent le paquet Python
`websocket-client`.

Les solutions des exercices sont dans `solutions/chNN/` (fichiers complets, à comparer avec les vôtres).

## Prérequis

Odoo 20.0 Community, Python 3.12, PostgreSQL 16. Ajouter ce dossier à `addons_path`.

## Licence

LGPL-3 (voir `LICENSE`).
