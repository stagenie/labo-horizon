from odoo import fields, models


class LabPatient(models.Model):
    _name = 'lab.patient'
    _description = 'Patient'
    _order = 'name'

    name = fields.Char('Nom', required=True)
    birthdate = fields.Date('Date de naissance')
    phone = fields.Char('Téléphone')
