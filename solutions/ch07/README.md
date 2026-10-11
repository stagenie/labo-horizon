# Chapitre 7 — corrigés

Les versions complètes des fichiers modifiés sont dans `lab_core/` ci-dessous.

## Exercice 7.1 — Annuler une demande

Un cinquième état dans `STATES`, `('cancelled', 'Annulée')`, sa place dans le cycle (`STATE_FROM`, section 7.7 :
`'cancelled': ('draft', 'sampled')`, et `'cancelled'` ajouté aux origines de `'draft'`), et une méthode :

```python
def action_cancel(self):
    self.filtered(lambda r: r.state in ('draft', 'sampled')).write({'state': 'cancelled'})
```

Le bouton « Annuler » n'est visible qu'en brouillon ou prélevée (`invisible="state not in ('draft', 'sampled')"`).
`statusbar_visible="draft,sampled,analysed,validated"` garde la barre d'état lisible : l'état « Annulée » ne s'y
affiche que lorsqu'une demande l'atteint. « Remettre en brouillon » fonctionne aussi depuis l'état annulé.

Critère, à l'écran : le bouton « Annuler » apparaît à côté de « Prélever » sur une demande en brouillon, et reste
sur une demande prélevée, qu'il fait passer à l'état Annulée ; « Remettre en brouillon » la ramène en brouillon. Une
demande validée n'affiche plus aucun bouton. Dans le shell, sur une demande d'essai :

```python
>>> req.action_sample()
>>> req.action_cancel()
>>> req.state
'cancelled'
>>> req.action_reset_draft()
>>> req.state
'draft'
```

et, sur une demande validée, `req.action_cancel()` ne fait rien : `req.state` reste `'validated'`. Un
`req.write({'state': 'cancelled'})` sur cette demande est refusé par le cycle :
`odoo.exceptions.UserError: Ce changement d'état ne suit pas le cycle de la demande.`

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

Critère, à l'écran : sur une demande enregistrée avec un prescripteur, vider le champ ouvre la fenêtre
« Prescripteur retiré », avec le message « Une demande sans prescripteur ne pourra pas être remboursée. » et le
bouton « Fermer » ; la saisie continue ensuite normalement.
