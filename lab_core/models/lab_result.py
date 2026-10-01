from odoo import fields, models


class LabResult(models.Model):
    _name = 'lab.result'
    _description = "Résultat d'analyse"
    _order = 'request_id, analysis_code'

    request_id = fields.Many2one('lab.request', 'Demande', required=True, ondelete='cascade', index=True)
    analysis_id = fields.Many2one('lab.analysis', 'Analyse', required=True)
    analysis_code = fields.Char(related='analysis_id.code', store=True)
    unit = fields.Char(related='analysis_id.unit')
    value_text = fields.Char('Résultat')
