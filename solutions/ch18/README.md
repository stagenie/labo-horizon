# Chapitre 18 — corrigés

Les versions complètes des fichiers modifiés sont dans `lab_portal/` ci-dessous.

## Exercice 18.1 — Un e-mail de confirmation immédiate

Un troisième gabarit, `mail_template_booking_confirmed`, sur le modèle `calendar.event`, reprend la forme du rappel :
`use_default_to` à `False`, destinataire `{{ object.lab_contact_email }}`, heure par `lab_display_start()`.

`_create_booking_event` l'envoie juste après la création du rendez-vous. Le gabarit est lu en `sudo()` : la méthode
s'exécute pour le visiteur anonyme, qui ne lit pas `mail.template`. L'envoi a lieu à l'intérieur du `savepoint` de
`_book` : si l'index unique refuse le rendez-vous, le courriel préparé disparaît avec lui, et le visiteur qui voit
« Ce créneau vient d'être réservé » ne reçoit pas de confirmation.

Le gabarit étant en `noupdate`, une base déjà installée le reçoit quand même au `-u` : c'est un nouvel identifiant XML.

Critère : le test `test_booking_sends_confirmation` passe.

## Exercice 18.2 — Renvoyer l'e-mail des résultats

Une vue héritée ajoute à l'en-tête de la demande un bouton « Renvoyer l'e-mail des résultats », visible sur une
demande validée, pour le secrétariat (`groups="lab_core.group_lab_secretary"`, donc aussi technicien et biologiste).

`action_resend_results_mail` refuse explicitement, par une `UserError`, le patient sans e-mail, au dossier
confidentiel ou sans accès au portail : à la validation, ce cas se taisait (la validation ne devait pas échouer pour
un courriel) ; ici, la secrétaire a demandé un envoi, elle doit savoir qu'il n'a pas lieu. Sinon, la méthode appelle
`_notify_results_ready`, la même que la validation.

Critères : les tests `test_resend_results_mail` et `test_resend_refused_without_portal` passent.
