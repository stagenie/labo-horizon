# Chapitre 11 — corrigés

Les versions complètes des fichiers modifiés sont dans `lab_core/` ci-dessous.

## Exercice 11.1 — Un commentaire de paillasse

Un champ de plus dans l'assistant, `wizard/lab_result_entry.py` :

```python
comment = fields.Text('Commentaire')
```

placé sous la liste dans la vue de l'assistant, puis publié sur la demande au moment d'appliquer, avant le
passage à l'état Analysée :

```python
if self.comment:
    self.request_id.message_post(body=self.comment)
```

Le texte saisi est une chaîne simple : `message_post` l'échappe (chapitre 8), aucun balisage n'arrive dans le
fil de discussion. Le commentaire survit à l'assistant, qui sera effacé par le nettoyage des modèles
transitoires : seule la demande garde une trace durable.

Critère, à l'écran : après « Enregistrer et terminer », le fil de la demande affiche le commentaire, comme une note.
Dans le shell, une saisie appliquée par le technicien avec
`entry.comment = 'Sérum légèrement hémolysé'` laisse :

```python
>>> entry.action_apply()
{'type': 'ir.actions.act_window_close'}
>>> req.message_ids[0].body
Markup('<p>Sérum légèrement hémolysé</p>')
```

## Exercice 11.2 — « Remettre en brouillon » depuis la liste

Un second enregistrement `ir.actions.server` dans `data/lab_actions.xml`, sur le modèle de « Valider les
demandes » : même `binding_model_id`, même `binding_view_types` (`list`), `group_ids` réservé au biologiste, et
le code `records.action_reset_draft()`.

`group_ids` ne fait que masquer l'action dans le menu Actions des autres utilisateurs. Le contrôle qui protège
vraiment reste le `has_group` d'`action_reset_draft` (chapitre 10) : une action serveur exécute le code avec les
droits de l'utilisateur qui la lance.

Critère, à l'écran : connecté en administrateur, biologiste, le menu Actions de la liste des demandes propose
« Remettre en brouillon » ; connecté en `technicien`, non. Une demande prélevée cochée revient à l'état Brouillon.
Dans le shell :

```python
>>> reset = env.ref('lab_core.action_server_lab_request_reset_draft')
>>> reset.name, reset.group_ids.full_name, reset.binding_view_types
('Remettre en brouillon', 'Laboratoire / Biologiste', 'list')
>>> req.action_sample()
>>> reset.with_context(active_model='lab.request', active_ids=req.ids).run()
False
>>> req.state
'draft'
```
