from odoo import fields, models


class ResPartner(models.Model):
    _inherit = 'res.partner'

    lab_patient_ids = fields.One2many('lab.patient', 'partner_id', 'Fiches patient')
    lab_insurer_ids = fields.One2many('lab.insurer', 'partner_id', 'Fiche mutuelle')
