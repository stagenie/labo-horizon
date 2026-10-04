# Chapitre 17 — corrigés

Les versions complètes des fichiers modifiés sont dans `lab_portal/` ci-dessous.

## Exercice 17.1 — Un commentaire facultatif

Le formulaire gagne une zone de texte, `<textarea name="comment">`, qui reprend la saisie en cas d'erreur
(`t-out="values.get('comment')"`). Le contrôleur reçoit `comment`, le nettoie par `.strip()` comme les autres champs,
et le transmet à `_book`, qui le passe à `_create_booking_event` ; le rendez-vous le range dans son champ `description`.

Le commentaire reste facultatif : il n'entre pas dans les contrôles du contrôleur. Il passe par la liste des champs
écrits en superutilisateur, la seule porte d'entrée du visiteur ; un champ que le formulaire n'envoie pas ne peut pas
y arriver.

Critère : le test `test_booking_keeps_comment` passe.

## Exercice 17.2 — Une fenêtre de réservation réglable

Le paramètre système `lab_portal.booking_days` (Paramètres › Technique › Paramètres système, en mode développeur)
remplace la constante `BOOKING_DAYS`, qui reste la valeur par défaut :

```python
@api.model
def _booking_days(self):
    days = self.env['ir.config_parameter'].sudo().get_int('lab_portal.booking_days', BOOKING_DAYS)
    return days if days > 0 else BOOKING_DAYS
```

En Odoo 20, `get_param` et `set_param` n'existent plus : un paramètre se lit avec le type attendu, `get_int`,
`get_float`, `get_bool` ou `get_str`, et s'écrit avec `set_int`, etc. `get_int` renvoie la valeur par défaut quand le
paramètre est absent ou n'est pas un entier (avec un avertissement dans le journal). `ir.config_parameter` n'est
lisible que par l'administrateur : la lecture se fait en `sudo()`, un usage technique. Une valeur nulle ou négative
retombe aussi sur 7 jours : un paramètre se modifie à la main, une faute de frappe ne doit pas fermer la prise de
rendez-vous. `_get_available_slots` prend `days=None` et appelle
`_booking_days()` quand aucune durée n'est donnée. `_book` contrôle le créneau sur cette même liste : la fenêtre
réglée vaut aussi pour le formulaire envoyé à la main.

Critère : le test `test_booking_window_parameter` passe.
