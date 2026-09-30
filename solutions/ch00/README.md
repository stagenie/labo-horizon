# Chapitre 0 — corrigés

## Exercice 0.1 — Une seconde instance

Une option de ligne de commande l'emporte sur la valeur de `odoo.conf` :

```bash
cd ~/odoo20 && source venv/bin/activate
./odoo/odoo-bin -c odoo.conf -d vs20_lab_dev                    # terminal 1 : port 8069
./odoo/odoo-bin -c odoo.conf -d vs20_lab_dev --http-port=8070   # terminal 2 : port 8070
curl -s -o /dev/null -w "%{http_code}\n" http://localhost:8070/web/login   # → 200
```

Les deux serveurs partagent la même base : une fiche créée sur l'un est visible sur l'autre après rechargement.

## Exercice 0.2 — Installer le module généré

```bash
mkdir -p ~/odoo20/essais
./odoo/odoo-bin scaffold lab_essai ~/odoo20/essais
```

Dans `odoo.conf`, ajouter le dossier à `addons_path` :

```ini
addons_path = ~/odoo20/odoo/addons,
    ~/odoo20/labo-horizon,
    ~/odoo20/essais
```

Puis installer :

```bash
./odoo/odoo-bin -c odoo.conf -d vs20_lab_dev -i lab_essai --stop-after-init
```

Le journal signale `Missing license key in manifest for 'lab_essai', defaulting to LGPL-3` (le gabarit ne déclare pas
de licence) : ajouter `'license': 'LGPL-3'` au manifeste le fait taire. Dans Apps, retirer le filtre « Apps » et
chercher `lab_essai` : état « Installé », version `20.0.0.1`.

Ne pas décommenter la ligne `'security/ir.model.access.csv'` du manifeste : ce format n'existe plus en Odoo 20
(`KeyError: 'ir.model.access'`).
