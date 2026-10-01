from odoo import fields, models


class LabPatient(models.Model):
    _name = 'lab.patient'
    _description = 'Patient'
    _order = 'name'

    name = fields.Char('Nom', required=True)
    birthdate = fields.Date('Date de naissance')
    phone = fields.Char('Téléphone')
    gender = fields.Selection([('female', 'Femme'), ('male', 'Homme')], 'Sexe')
    email = fields.Char('E-mail')
    notes = fields.Html('Notes internes', help="Informations utiles à l'accueil ; jamais transmises au patient.")
    request_ids = fields.One2many('lab.request', 'patient_id', 'Demandes')
