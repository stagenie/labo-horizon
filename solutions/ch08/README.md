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

Critère : le test `test_sampling_posts_tube_count` passe ; le chatter de la demande affiche le nombre en gras.

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

`mail.mail_activity_data_call` est le type d'activité « Appel » livré par le module `mail`. Le test
`test_validate_closes_activity` ne vérifie plus qu'il ne reste aucune activité, mais qu'il ne reste plus
d'activité « Validation biologique » : la demande de test a des résultats hors normes et reçoit donc l'appel.

Critère : `--test-tags /lab_core` passe ; une demande validée avec un résultat hors normes porte l'activité
« Appeler le patient ».
