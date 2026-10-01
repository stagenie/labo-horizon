# Chapitre 5 — corrigés

Les versions complètes des fichiers modifiés sont dans `lab_core/` ci-dessous.

## Exercice 5.1 — Le bilan thyroïdien

Un sixième enregistrement dans `data/lab_panel_data.xml` :

```xml
<record id="panel_thy" model="lab.panel">
    <field name="code">THY</field>
    <field name="name">Bilan thyroïdien</field>
    <field name="analysis_ids" eval="[Command.set([ref('analysis_tsh')])]"/>
</record>
```

Le test `test_panels_data` comptait 5 bilans : il en attend désormais 6 (`tests/test_lab_catalog.py`).

Attention : le fichier est en `noupdate="1"`, mais un enregistrement **nouveau** est bien créé par `-u lab_core`
(chapitre 3). Critère : **Configuration › Bilans** affiche « Bilan thyroïdien » avec l'étiquette TSH.

## Exercice 5.2 — Retirer les lignes vides

```python
def action_clear_empty_results(self):
    """ Supprime les lignes de résultat encore sans valeur. """
    self._get_pending_results().unlink()
```

et, dans l'en-tête du formulaire, `<button name="action_clear_empty_results" type="object" string="Retirer les lignes
vides"/>`. La méthode réutilise `_get_pending_results()` du chapitre 4 : `unlink()` supprime d'un coup toutes les
lignes du recordset. Le test `test_clear_empty_results` charge le bilan de base, saisit la glycémie, et vérifie
qu'il ne reste qu'elle.

Critère : les tests du module passent (`--test-tags /lab_core` sur une base neuve, section 4.8 du livre).
