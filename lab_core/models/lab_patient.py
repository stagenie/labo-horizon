from dateutil.relativedelta import relativedelta

from odoo import api, fields, models


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
    age = fields.Integer('Âge', compute='_compute_age')

    @api.depends('birthdate')
    def _compute_age(self):
        today = fields.Date.context_today(self)
        for patient in self:
            patient.age = relativedelta(today, patient.birthdate).years if patient.birthdate else 0
