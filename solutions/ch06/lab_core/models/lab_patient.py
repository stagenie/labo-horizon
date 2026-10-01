from dateutil.relativedelta import relativedelta

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError
from odoo.fields import Domain


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
    is_minor = fields.Boolean('Mineur', compute='_compute_age', search='_search_is_minor')

    @api.depends('birthdate')
    def _compute_age(self):
        today = fields.Date.context_today(self)
        for patient in self:
            patient.age = relativedelta(today, patient.birthdate).years if patient.birthdate else 0
            patient.is_minor = bool(patient.birthdate) and patient.age < 18

    def _search_is_minor(self, operator, value):
        if operator != 'in':
            return NotImplemented
        limit = fields.Date.context_today(self) - relativedelta(years=18)
        domains = []
        if True in value:
            domains.append(Domain('birthdate', '>', limit))
        if False in value:
            domains.append(Domain('birthdate', '=', False) | Domain('birthdate', '<=', limit))
        return Domain.OR(domains)

    @api.constrains('birthdate')
    def _check_birthdate(self):
        today = fields.Date.context_today(self)
        for patient in self:
            if patient.birthdate and patient.birthdate > today:
                raise ValidationError(_("%s : la date de naissance est dans le futur.", patient.name))
