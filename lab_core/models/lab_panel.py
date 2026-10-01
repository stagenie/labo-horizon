from odoo import fields, models


class LabPanel(models.Model):
    _name = 'lab.panel'
    _description = "Bilan (groupe d'analyses)"
    _order = 'name'

    code = fields.Char('Code', required=True)
    name = fields.Char('Nom', required=True, translate=True)
    analysis_ids = fields.Many2many('lab.analysis', string='Analyses')
