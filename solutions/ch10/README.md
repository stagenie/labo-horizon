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

Critère : le test `test_validated_request_cannot_be_deleted` passe.

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
et sert aussi au suivant (le test le montre). Puis, sur le bouton Valider, `invisible="state != 'analysed' or not can_validate"` à la place de `groups`, avec
`<field name="can_validate" invisible="1"/>` dans l'en-tête pour que le client web connaisse la valeur.

Comparaison : `groups` retire le bouton de l'architecture envoyée au navigateur ; `invisible` le cache, mais il
reste dans la page. Les deux ne sont que de l'affichage : le contrôle `has_group` d'`action_validate` reste
indispensable. Sur une page qui contient un champ illisible pour l'utilisateur, comme l'onglet Résultats pour la
secrétaire, seul `groups` convient : avec `invisible`, le formulaire chargerait quand même les résultats et
lèverait une erreur d'accès.

Critère : `--test-tags /lab_core` passe ; le bouton Valider reste réservé au biologiste.
