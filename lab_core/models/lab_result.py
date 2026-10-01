import re

from odoo import api, fields, models

FLAGS = [
    ('pending', 'En attente'),
    ('low', 'Bas'),
    ('normal', 'Normal'),
    ('high', 'Haut'),
    ('text', 'Qualitatif'),
]
NUMBER_RE = re.compile(r'^\s*-?\d+(?:[.,]\d+)?\s*$')


class LabResult(models.Model):
    _name = 'lab.result'
    _description = "Résultat d'analyse"
    _order = 'request_id, analysis_code'

    request_id = fields.Many2one('lab.request', 'Demande', required=True, ondelete='cascade', index=True)
    analysis_id = fields.Many2one('lab.analysis', 'Analyse', required=True)
    analysis_code = fields.Char(related='analysis_id.code', store=True)
    unit = fields.Char(related='analysis_id.unit')
    value_text = fields.Char('Résultat')
    value = fields.Float('Valeur', compute='_compute_value_flag', store=True, digits=(10, 2))
    range_min = fields.Float('Min', compute='_compute_value_flag', store=True, digits=(10, 2))
    range_max = fields.Float('Max', compute='_compute_value_flag', store=True, digits=(10, 2))
    flag = fields.Selection(FLAGS, 'Interprétation', compute='_compute_value_flag', store=True)

    @api.depends('value_text', 'analysis_id.ref_min', 'analysis_id.ref_max',
                 'analysis_id.ref_min_female', 'analysis_id.ref_max_female',
                 'request_id.patient_id.gender')
    def _compute_value_flag(self):
        for result in self:
            low, high = result.analysis_id._get_range(result.request_id.patient_id.gender) \
                if result.analysis_id else (0.0, 0.0)
            result.range_min, result.range_max = low, high
            text = (result.value_text or '').strip()
            if not text:
                result.value, result.flag = 0.0, 'pending'
            elif not NUMBER_RE.match(text):
                result.value, result.flag = 0.0, 'text'
            else:
                value = float(text.replace(',', '.'))
                result.value = value
                if high and value > high:
                    result.flag = 'high'
                elif value < low:
                    result.flag = 'low'
                else:
                    result.flag = 'normal'
