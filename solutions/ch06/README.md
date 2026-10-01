# Chapitre 6 — corrigés

Les versions complètes des fichiers modifiés sont dans `lab_core/` ci-dessous.

## Exercice 6.1 — Les patients mineurs

```python
is_minor = fields.Boolean('Mineur', compute='_compute_age', search='_search_is_minor')
```

Le champ est calculé par la même méthode que l'âge (`patient.is_minor = bool(patient.birthdate) and patient.age < 18`),
donc sans stockage. Pour qu'un filtre puisse le chercher, il faut lui donner une **méthode de recherche** : elle
traduit la condition en un domaine sur un champ stocké, ici `birthdate`.

```python
def _search_is_minor(self, operator, value):
    if operator != 'in':
        return NotImplemented
    limit = fields.Date.context_today(self) - relativedelta(years=18)
    domains = []
    if True in value:
        domains.append(Domain('birthdate', '>', limit))
    if False in value:
        domains.append(Domain('birthdate', '=', False) | Domain('birthdate', '<=', limit))
    return Domain.OR(domains)
```

Odoo 20 présente toujours la condition sous la forme `in` : `('is_minor', '=', True)` arrive comme
`operator='in'`, `value={True}` ; la négation est prise en charge par l'ORM. Le filtre « Mineurs » s'ajoute à une
vue de recherche des patients, créée pour l'occasion.

Critère : le test `test_minor_search` passe, et le filtre « Mineurs » n'affiche que les patients de moins de 18 ans.

## Exercice 6.2 — Pas de naissance dans le futur

```python
@api.constrains('birthdate')
def _check_birthdate(self):
    today = fields.Date.context_today(self)
    for patient in self:
        if patient.birthdate and patient.birthdate > today:
            raise ValidationError(_("%s : la date de naissance est dans le futur.", patient.name))
```

Critère : le test `test_future_birthdate_refused` passe ; dans l'interface, enregistrer une date future affiche le
message.
