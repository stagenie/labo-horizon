# Chapitre 16 — corrigés

Les versions complètes des fichiers modifiés sont dans `lab_portal/` ci-dessous.

## Exercice 16.1 — Télécharger depuis la liste

Dans le gabarit `portal_my_lab_results`, une colonne de plus, dans l'en-tête et dans chaque ligne :

```xml
<td class="text-end"><a t-att-href="'%s/pdf' % req.access_url">Télécharger</a></td>
```

Le lien vise la même route que le bouton du compte rendu : le contrôle des droits reste celui de
`_lab_request_check_access`, rien n'est ajouté côté serveur.

Critère : le test `test_list_has_download_links` passe.

## Exercice 16.2 — Trier la liste

La route reçoit `sortby` (paramètre d'adresse `?sortby=name`), choisit un ordre dans un dictionnaire et le passe à
`search(..., order=...)`. Le même dictionnaire, `searchbar_sortings`, alimente la barre du portail
(`portal.portal_searchbar`), qui affiche le menu de tri et fabrique les liens :

```python
searchbar_sortings = {
    'date': {'label': 'Date de validation', 'order': 'validated_date desc, id desc'},
    'name': {'label': 'Numéro', 'order': 'name'},
}
if sortby not in searchbar_sortings:
    sortby = 'date'
```

Une valeur inconnue (`?sortby=n_importe_quoi`) retombe sur le tri par date : un paramètre d'adresse se modifie à la
main, il ne doit jamais arriver tel quel dans une requête.

Critère : le test `test_list_sorted_by_name` passe.
