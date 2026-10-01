# Chapitre 4 — corrigés

Les versions complètes des fichiers modifiés sont dans `lab_core/` ci-dessous.

## Exercice 4.1 — Les résultats sanguins

```python
def _get_blood_results(self):
    """ Résultats des analyses faites sur un tube de sang. """
    return self.result_ids.filtered(lambda r: r.analysis_id.sample_type == 'blood')
```

`filtered` garde les lignes pour lesquelles la fonction renvoie vrai ; la fonction suit le Many2one `analysis_id` pour
lire le type de tube. Le test `test_blood_results` crée une demande GLY + ECBU + HB et attend `['GLY', 'HB']`.

Critère : les tests du module passent (`--test-tags /lab_core` sur une base neuve, section 4.8 du livre).

## Exercice 4.2 — Dupliquer une demande

```python
def test_copy_keeps_results_not_samples(self):
    req = self._request_with(['gly', 'hb'])
    req.sample_ids = [Command.create({'sample_type': 'blood'})]
    dup = req.copy()
    self.assertEqual(dup.result_ids.mapped('analysis_code'), ['GLY', 'HB'])
    self.assertNotEqual(dup.result_ids, req.result_ids)
    self.assertFalse(dup.sample_ids)
```

`copy()` duplique la demande. `result_ids` porte `copy=True` : les lignes de résultat sont recréées sur la copie (de
nouveaux enregistrements, d'où le `assertNotEqual`). `sample_ids` porte `copy=False` : la copie n'a aucun tube, un tube
ne se prélève qu'une fois.

Critère : les tests du module passent (`--test-tags /lab_core` sur une base neuve, section 4.8 du livre).
