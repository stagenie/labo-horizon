from odoo import fields, models

from .lab_analysis import SAMPLE_TYPES


class LabSample(models.Model):
    _name = 'lab.sample'
    _description = 'Tube'
    _order = 'id'

    request_id = fields.Many2one('lab.request', 'Demande', required=True, ondelete='cascade', index=True)
    patient_id = fields.Many2one(related='request_id.patient_id')
    sample_type = fields.Selection(SAMPLE_TYPES, 'Type', required=True)
    collected_at = fields.Datetime('Prélevé le', default=fields.Datetime.now)
