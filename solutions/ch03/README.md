# Chapitre 3 — corrigés

Les deux exercices modifient la demande : les versions complètes sont dans `lab_core/` ci-dessous.

## Exercice 3.1 — Le téléphone du patient sur la demande

`patient_phone = fields.Char(related='patient_id.phone', string='Téléphone du patient')`, puis
`<field name="patient_phone"/>` sous le patient dans le formulaire. Un champ `related` suit la relation : il n'est pas
stocké (pas de colonne), il affiche la valeur courante de la fiche patient, en lecture seule par défaut.

Critère : choisir un autre patient sur la demande change aussitôt le téléphone affiché.

## Exercice 3.2 — Le préleveur

`collector_id = fields.Many2one('res.users', 'Préleveur', default=lambda self: self.env.user)` : la `lambda` est
évaluée à chaque création, avec l'utilisateur connecté. Écrire `default=self.env.user` ne fonctionnerait pas : `self`
n'existe pas au moment où la classe est définie.

Critère : une nouvelle demande propose l'utilisateur connecté comme préleveur.
