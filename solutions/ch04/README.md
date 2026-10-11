# Chapitre 4 — corrigés

Les versions complètes des fichiers modifiés sont dans `lab_core/` ci-dessous.

## Exercice 4.1 — Les résultats sanguins

```python
def _get_blood_results(self):
    """ Résultats des analyses faites sur un tube de sang. """
    return self.result_ids.filtered(lambda r: r.analysis_id.sample_type == 'blood')
```

`filtered` garde les lignes pour lesquelles la fonction renvoie vrai ; la fonction suit le Many2one `analysis_id` pour
lire le type de tube. Aucun champ n'est ajouté : relancer le shell suffit, il charge le code à son démarrage.

Critère, dans le shell :

```python
>>> from odoo.fields import Command
>>> req = env.ref('lab_core.request_demo_1')
>>> new = env['lab.request'].create({
...     'patient_id': req.patient_id.id,
...     'result_ids': [Command.create({'analysis_id': env.ref(f'lab_core.analysis_{c}').id}) for c in ['gly', 'ecbu', 'hb']],
... })
>>> new._get_blood_results().mapped('analysis_code')
['GLY', 'HB']
```

## Exercice 4.2 — Dupliquer une demande

Aucun code à écrire : l'exercice observe dans le shell l'effet des paramètres `copy` posés en section 4.2.

```python
>>> from odoo.fields import Command
>>> req = env.ref('lab_core.request_demo_1')
>>> req.sample_ids = [Command.create({'sample_type': 'blood'})]   # seulement si la demande n'a pas de tube
>>> dup = req.copy()
>>> sorted(dup.result_ids.mapped('analysis_code'))
['CRP', 'GLY', 'HB']
>>> dup.result_ids & req.result_ids
lab.result()
>>> dup.sample_ids
lab.sample()
```

`copy()` duplique la demande. `result_ids` porte `copy=True` : les lignes de résultat sont recréées sur la copie, pour
les mêmes analyses, mais ce sont de nouveaux enregistrements, d'où l'intersection vide. `sample_ids` porte
`copy=False` : la copie n'a aucun tube, un tube ne se prélève qu'une fois.

Contre-épreuve : retirer `copy=True` de `result_ids` dans `models/lab_request.py`, relancer le shell, refaire la
copie : `dup.result_ids` rend `lab.result()`. Remettre ensuite `copy=True`. `Ctrl+D` quitte sans rien enregistrer.
