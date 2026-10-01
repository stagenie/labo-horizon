from odoo import api, fields, models

from .lab_analysis import SAMPLE_TYPES


class LabSample(models.Model):
    _name = 'lab.sample'
    _description = 'Tube'
    _order = 'id'

    request_id = fields.Many2one('lab.request', 'Demande', required=True, ondelete='cascade', index=True)
    patient_id = fields.Many2one(related='request_id.patient_id')
    sample_type = fields.Selection(SAMPLE_TYPES, 'Type', required=True)
    collected_at = fields.Datetime('Prélevé le', default=fields.Datetime.now)
    barcode = fields.Char('Code-barres', readonly=True, copy=False)

    _barcode_uniq = models.Constraint('UNIQUE (barcode)', "Ce code-barres existe déjà.")

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if not vals.get('barcode'):
                vals['barcode'] = self.env['ir.sequence'].next_by_code('lab.sample')
        return super().create(vals_list)

    @api.model
    def _assign_missing_barcodes(self):
        for sample in self.search([('barcode', '=', False)]):
            sample.barcode = self.env['ir.sequence'].next_by_code('lab.sample')
