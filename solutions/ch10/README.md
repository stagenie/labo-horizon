# Chapitre 10 — corrigés

Les versions complètes des fichiers modifiés sont dans `lab_core/` ci-dessous.

## Exercice 10.1 — Une demande validée ne se supprime plus

Une ligne **sans groupe** dans `security/ir.access.csv` :

```csv
restrict_lab_request_validated_delete,Demande validée : jamais supprimée,lab.request,,d,"[('state', '!=', 'validated')]"
```

Sans groupe, la ligne est une **restriction** : elle s'applique à tous les utilisateurs, en ET avec leurs
permissions. Pour l'opération `d` (suppression), seules les demandes non validées restent permises, même au
biologiste qui a le droit `crud`. Seul le superutilisateur y échappe.

Critère, à l'écran : connecté en administrateur (biologiste), une demande en brouillon se supprime ; sur une
demande validée, la suppression est refusée par le dialogue « Erreur d'accès ». Dans le shell,
en administrateur (`env['lab.request'].with_user(env.ref('base.user_admin'))`), `unlink()` renvoie `True` sur une
demande en brouillon, et refuse une demande validée :

```text
odoo.exceptions.AccessError: Oups ! On dirait que vous êtes tombé sur des enregistrements top secrets.
Désolé, Mitchell Admin (id=2) n'a pas d'accès 'delete' à :
- Demande d'analyses (lab.request)
Si vous avez vraiment besoin d'un accès, vous pouvez peut-être convaincre votre sympathique administrateur en lui offrant des cookies maison.
```

L'opération y reste en anglais (`'delete'`), telle qu'Odoo 20 l'écrit dans ce message.

## Exercice 10.2 — `groups` ou `invisible` ?

Un champ calculé non stocké, recalculé à chaque lecture pour l'utilisateur courant :

```python
can_validate = fields.Boolean(compute='_compute_can_validate')

@api.depends_context('uid')
def _compute_can_validate(self):
    is_biologist = self.env.user.has_group('lab_core.group_lab_biologist')
    for request in self:
        request.can_validate = is_biologist
```

`@api.depends_context('uid')` est indispensable : sans lui, la valeur calculée pour un utilisateur reste en cache
et sert aussi au suivant. Puis, sur le bouton Valider, `invisible="state != 'analysed' or not can_validate"` à la place de `groups`, avec
`<field name="can_validate" invisible="1"/>` dans l'en-tête pour que le client web connaisse la valeur.

Comparaison : `groups` retire le bouton de l'architecture envoyée au navigateur ; `invisible` le cache, mais il
reste dans la page. Les deux ne sont que de l'affichage : le contrôle `has_group` d'`action_validate` reste
indispensable. Sur une page qui contient un champ illisible pour l'utilisateur, comme l'onglet Résultats pour la
secrétaire, seul `groups` convient : avec `invisible`, le formulaire chargerait quand même les résultats et
lèverait une erreur d'accès.

Critère, à l'écran : sur une demande analysée, le bouton « Valider » apparaît pour l'administrateur, biologiste, et
non pour le compte `technicien`. Dans le shell, sur une demande `req` :

```python
>>> req.with_user(env.ref('base.user_admin')).can_validate, req.with_user(tech).can_validate
(True, False)
```

avec `tech = env['res.users'].search([('login', '=', 'technicien')])`.
