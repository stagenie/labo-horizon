from odoo import api, fields, models


class LabPanel(models.Model):
    _name = 'lab.panel'
    _description = "Bilan (groupe d'analyses)"
    _order = 'name'

    code = fields.Char('Code', required=True)
    name = fields.Char('Nom', required=True, translate=True)
    analysis_ids = fields.Many2many('lab.analysis', string='Analyses')
    analysis_count = fields.Integer("Nombre d'analyses", compute='_compute_analysis_count')

    @api.depends('analysis_ids')
    def _compute_analysis_count(self):
        for panel in self:
            panel.analysis_count = len(panel.analysis_ids)
