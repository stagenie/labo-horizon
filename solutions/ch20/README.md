# Chapitre 20 — corrigés

Les versions complètes des fichiers modifiés sont dans `scripts/` et `lab_owl/` ci-dessous.

## Exercice 20.1 — Lire le fichier de l'automate

`scripts/automate.py` gagne une option `--csv FICHIER`. La fonction `read_csv` lit une ligne `CODE;VALEUR` par ligne,
ignore les lignes vides et un en-tête `code;valeur` en première ligne, et transforme chaque ligne en `CODE=VALEUR` :
la suite du script ne change pas, `parse_results` reçoit la même forme que pour `--result`. Les deux options se
combinent.

Une ligne sans point-virgule arrête le script **avant** tout envoi, avec son numéro de ligne et le code de retour 2 :
rien n'est écrit dans Odoo. Un fichier introuvable est traité de la même façon. Attention à l'ordre des `except` :
`urllib.error.HTTPError` hérite d'`OSError` ; un `except OSError` placé avant celui de `HTTPError` avalerait les refus
du serveur. Le corrigé convertit donc l'erreur de fichier en `ValueError` dans `read_csv`.

Critères : `python3 scripts/automate.py … --csv resultats.csv` avec un fichier de quatre lignes affiche la réponse
d'Odoo et rend le code 0 (`echo $?`), et les quatre valeurs apparaissent dans la demande ; une ligne sans
point-virgule affiche son numéro, rend le code 2, et la demande, rouverte à l'écran, n'a pas changé.

## Exercice 20.2 — Ce qui reste à mesurer

`lab.request.api_pending_analyses(request_ref)` renvoie la liste triée des codes d'analyse encore sans valeur
(`_get_pending_results` de `lab_core`). La recherche de la demande est extraite dans `_lab_find_request`, partagée
avec `_lab_push_results` : même message « Demande … introuvable. », même refus 422, même absence de trace grâce à
`conceal_debug_traceback`. Aucun `sudo` : l'automate lit avec ses droits de technicien.

Appel : `POST /json/2/lab.request/api_pending_analyses` avec le corps `{"request_ref": "DEM/2026/00007"}`.

Vérification avec `curl`, la clé dans `LAB_API_KEY` :

```text
curl -s -X POST http://localhost:8069/json/2/lab.request/api_pending_analyses \
    -H "Authorization: Bearer $LAB_API_KEY" -H "X-Odoo-Database: vs20_lab_dev" \
    -H "Content-Type: application/json" -d '{"request_ref": "DEM/2026/00007"}'
```

Critères : après l'envoi du seul cholestérol total, la réponse est `["HDL", "LDL", "TG"]` ; pour une demande
inconnue, `-w '%{http_code}'` affiche 422, et le champ `debug` de la réponse tient en une ligne, sans trace Python.
