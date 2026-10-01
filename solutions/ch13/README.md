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

Critère : le test `test_partner_reused_by_email` passe.

## Exercice 13.2 — Le numéro d'organisme de la mutuelle

Un champ `code` sur `lab.insurer` et une contrainte SQL d'unicité, comme le code d'une analyse au chapitre 6 :

```python
code = fields.Char("N° d'organisme")

_code_uniq = models.Constraint('UNIQUE (code)', "Ce numéro d'organisme existe déjà.")
```

Le champ appartient à la mutuelle, pas au contact : il est stocké dans la table `lab_insurer`. Plusieurs mutuelles
sans numéro restent permises (en SQL, deux valeurs vides ne sont pas égales).

Critère : le test `test_insurer_code_unique` passe.
