"""Automate d'analyses simulé : pousse ses résultats vers Labo Horizon par l'API JSON-2 d'Odoo 20.

La clé API se lit dans la variable d'environnement LAB_API_KEY, jamais en argument : une ligne de
commande se lit dans la liste des processus et dans l'historique du shell.

Exemple :
    export LAB_API_KEY=...        # clé de l'utilisateur « Automate CHIM-1 »
    python3 scripts/automate.py --url http://localhost:9025 --db vs20_lab_dev \\
        --request DEM/2026/00007 --result CHOL=2,4 --result TG=1,1
"""
import argparse
import json
import os
import sys
import urllib.error
import urllib.request


def parse_results(items):
    """['CHOL=2,4', 'TG=1,1'] → {'CHOL': '2,4', 'TG': '1,1'}."""
    results = {}
    for item in items:
        code, sep, value = item.partition('=')
        if not sep or not code.strip() or not value.strip():
            raise ValueError(f"résultat illisible : {item!r} (attendu CODE=VALEUR)")
        results[code.strip().upper()] = value.strip()
    return results


def read_csv(path):
    """Fichier de l'automate, une ligne CODE;VALEUR ; en-tête « code;valeur » facultatif, lignes vides ignorées."""
    items = []
    try:
        handle = open(path, encoding='utf-8')
    except OSError as err:       # pas d'OSError plus bas : HTTPError en hérite
        raise ValueError(f"fichier {path} illisible : {err.strerror}") from err
    with handle:
        for number, line in enumerate(handle, start=1):
            line = line.strip()
            if not line or (number == 1 and line.lower().startswith('code;')):
                continue
            code, sep, value = line.partition(';')
            if not sep:
                raise ValueError(f"ligne {number} illisible : {line!r} (attendu CODE;VALEUR)")
            items.append(f"{code}={value}")
    return items


def push(url, db, key, request_ref, results):
    body = json.dumps({'request_ref': request_ref, 'results': results}).encode()
    request = urllib.request.Request(
        f"{url.rstrip('/')}/json/2/lab.request/api_push_results",
        data=body,
        method='POST',
        headers={
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {key}',
            'X-Odoo-Database': db,
        },
    )
    with urllib.request.urlopen(request, timeout=30) as response:
        return json.load(response)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument('--url', required=True, help="adresse d'Odoo, ex. http://localhost:9025")
    parser.add_argument('--db', required=True, help="nom de la base")
    parser.add_argument('--request', required=True, help="numéro de la demande, ex. DEM/2026/00007")
    parser.add_argument('--result', action='append', default=[], help="CODE=VALEUR, répétable")
    parser.add_argument('--csv', help="fichier CODE;VALEUR exporté par l'automate")
    args = parser.parse_args(argv)
    key = os.environ.get('LAB_API_KEY')
    if not key:
        print("LAB_API_KEY absente : exportez la clé API de l'automate.", file=sys.stderr)
        return 2
    try:
        items = args.result + (read_csv(args.csv) if args.csv else [])
        results = parse_results(items)
        print(json.dumps(push(args.url, args.db, key, args.request, results), ensure_ascii=False))
        return 0
    except ValueError as err:
        print(f"Erreur : {err}", file=sys.stderr)
        return 2
    except urllib.error.HTTPError as err:
        try:
            message = json.loads(err.read()).get('message', err.reason)
        except ValueError:
            message = err.reason
        print(f"Refusé ({err.code}) : {message}", file=sys.stderr)
        return 1
    except urllib.error.URLError as err:
        print(f"Serveur injoignable : {err.reason}", file=sys.stderr)
        return 1


if __name__ == '__main__':
    sys.exit(main())
