# Chapitre 13 — corrigés

Les versions complètes des fichiers modifiés sont dans `lab_billing/` ci-dessous.

## Exercice 13.1 — Reprendre un contact existant

Avant de créer le contact du patient, `_get_or_create_partner` cherche un contact de même e-mail :

```python
partner = self.email and self.env['res.partner'].search([('email', '=ilike', self.email)], limit=1)
self.partner_id = partner or self.env['res.partner'].create({...})
```

L'opérateur `=ilike` compare sans tenir compte de la casse (`ALICE@example.com` et `alice@example.com` sont la
même adresse). Sans e-mail, rien n'est cherché : deux patients sans adresse ne doivent pas partager un contact.

Critère, dans le shell (section 13.3) :

```python
>>> c = env['res.partner'].create({'name': 'J. Bernard', 'email': 'JULIE.BERNARD@example.com'})
>>> p = env.ref('lab_core.patient_demo_1')
>>> p._get_or_create_partner() == c
True
>>> env.cr.rollback()
```

## Exercice 13.2 — Le numéro d'organisme de la mutuelle

Un champ `code` sur `lab.insurer` et une contrainte SQL d'unicité, comme le code d'une analyse au chapitre 6 :

```python
code = fields.Char("N° d'organisme")

_code_uniq = models.Constraint('UNIQUE (code)', "Ce numéro d'organisme existe déjà.")
```

Le champ appartient à la mutuelle, pas au contact : il est stocké dans la table `lab_insurer`. Plusieurs mutuelles
sans numéro restent permises (en SQL, deux valeurs vides ne sont pas égales).

Critère, dans le shell après la mise à jour du module (le champ n'est pas encore dans le formulaire) :

```python
>>> env['lab.insurer'].search([('name', '=', 'Mutuelle Horizon Santé')]).code = 'AMC-75'
>>> env['lab.insurer'].create({'name': 'Mutuelle Doublon', 'code': 'AMC-75', 'coverage_rate': 50})
psycopg2.errors.UniqueViolation: duplicate key value violates unique constraint "lab_insurer_code_uniq"
DETAIL:  Key (code)=(AMC-75) already exists.
>>> env.cr.rollback()
```

Le shell montre l'erreur brute de PostgreSQL ; à l'écran, Odoo la remplace par le message de la contrainte, « Ce
numéro d'organisme existe déjà. »
