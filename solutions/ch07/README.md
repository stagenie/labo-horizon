# Chapitre 7 — corrigés

Les versions complètes des fichiers modifiés sont dans `lab_core/` ci-dessous.

## Exercice 7.1 — Annuler une demande

Un cinquième état dans `STATES`, `('cancelled', 'Annulée')`, et une méthode :

```python
def action_cancel(self):
    self.filtered(lambda r: r.state in ('draft', 'sampled')).write({'state': 'cancelled'})
```

Le bouton « Annuler » n'est visible qu'en brouillon ou prélevée (`invisible="state not in ('draft', 'sampled')"`).
`statusbar_visible="draft,sampled,analysed,validated"` garde la barre d'état lisible : l'état « Annulée » ne s'y
affiche que lorsqu'une demande l'atteint. « Remettre en brouillon » fonctionne aussi depuis l'état annulé.

Critère : le test `test_cancel` passe ; une demande validée ne peut pas être annulée.

## Exercice 7.2 — Prévenir quand le prescripteur est retiré

```python
@api.onchange('prescriber_id')
def _onchange_prescriber_id(self):
    if not self.prescriber_id and self._origin.prescriber_id:
        return {'warning': {
            'title': _("Prescripteur retiré"),
            'message': _("Une demande sans prescripteur ne pourra pas être remboursée."),
        }}
```

Une méthode `onchange` peut renvoyer un dictionnaire `warning` : le client web l'affiche dans une fenêtre, sans
bloquer la saisie. `self._origin` est l'enregistrement tel qu'il est en base : l'avertissement ne s'affiche que si
un prescripteur enregistré vient d'être retiré.

Critère : sur une demande enregistrée avec un prescripteur, vider le champ affiche l'avertissement.
