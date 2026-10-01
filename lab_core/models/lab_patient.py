from dateutil.relativedelta import relativedelta

from odoo import api, fields, models


class LabPatient(models.Model):
    _name = 'lab.patient'
    _description = 'Patient'
    _order = 'name'
    _inherit = ['mail.thread']

    name = fields.Char('Nom', required=True, tracking=True)
    ref = fields.Char('Référence', readonly=True, copy=False, index=True)
    birthdate = fields.Date('Date de naissance')
    phone = fields.Char('Téléphone', tracking=True)
    gender = fields.Selection([('female', 'Femme'), ('male', 'Homme')], 'Sexe')
    email = fields.Char('E-mail', tracking=True)
    is_confidential = fields.Boolean('Dossier confidentiel', tracking=True)
    notes = fields.Html('Notes internes', help="Informations utiles à l'accueil ; jamais transmises au patient.")
    request_ids = fields.One2many('lab.request', 'patient_id', 'Demandes')
    age = fields.Integer('Âge', compute='_compute_age')

    @api.depends('birthdate')
    def _compute_age(self):
        today = fields.Date.context_today(self)
        for patient in self:
            patient.age = relativedelta(today, patient.birthdate).years if patient.birthdate else 0

    _ref_uniq = models.Constraint('UNIQUE (ref)', "Cette référence patient existe déjà.")

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if not vals.get('ref'):
                vals['ref'] = self.env['ir.sequence'].next_by_code('lab.patient')
        return super().create(vals_list)

    @api.model
    def _assign_missing_refs(self):
        """ Numérote les patients créés avant l'arrivée de la séquence (bases des chapitres 1 à 6). """
        for patient in self.search([('ref', '=', False)]):
            patient.ref = self.env['ir.sequence'].next_by_code('lab.patient')
