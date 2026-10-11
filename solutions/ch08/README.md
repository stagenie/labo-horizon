# Chapitre 8 — corrigés

Les versions complètes des fichiers modifiés sont dans `lab_core/` ci-dessous.

## Exercice 8.1 — Annoncer les tubes prélevés

En fin de boucle d'`action_sample`, une fois les tubes créés :

```python
from markupsafe import Markup
...
request.message_post(body=Markup(_("<b>%s</b> tube(s) prélevé(s).")) % len(request.sample_ids))
```

`message_post` traite une chaîne ordinaire comme du texte : les balises seraient échappées et le chatter
afficherait `<b>3</b>` en toutes lettres. `Markup` déclare la chaîne sûre ; l'opérateur `%` appliqué à un
`Markup` échappe, lui, la valeur insérée.

Critère, à l'écran : après « Prélever », le fil de la demande affiche « **1** tube(s) prélevé(s). » (ou 2, 3…
selon les types de prélèvement), le nombre en gras et sans balise visible. Dans le shell, juste après
`req.action_sample()` :

```python
>>> req.message_ids[0].body
Markup('<span><b>1</b> tube(s) prélevé(s).</span>')
```

## Exercice 8.2 — Appeler le patient en cas de résultat hors normes

Dans `action_validate`, après `activity_feedback` :

```python
for request in to_validate.filtered('abnormal_count'):
    request.activity_schedule(
        'mail.mail_activity_data_call',
        summary=_("Appeler le patient"),
        user_id=self.env.uid,
    )
```

`mail.mail_activity_data_call` est le type d'activité « Appel » livré par le module `mail`. Après la validation, une
demande hors normes ne garde donc plus l'activité « Validation biologique », mais porte l'appel.

Critère, à l'écran : une demande validée avec un résultat hors normes montre, dans son chatter, l'activité
« Appeler le patient » ; une demande aux résultats normaux n'a plus aucune activité. Dans le shell, sur une demande
du bilan de base dont toutes les valeurs valent `1` (l'hémoglobine est alors basse) :

```python
>>> req.abnormal_count
1
>>> req.action_validate()
True
>>> req.activity_ids.summary
'Appeler le patient'
```

et, sur une demande aux valeurs normales (glycémie `0,90`, hémoglobine `13`, CRP `2`), `req.activity_ids` vaut
`mail.activity()` après la validation.
