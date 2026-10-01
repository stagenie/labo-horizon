from odoo import fields, models


class LabResultEntry(models.TransientModel):
    _name = 'lab.result.entry'
    _description = 'Saisie des résultats'
    _transient_max_hours = 1.0

    request_id = fields.Many2one('lab.request', required=True, readonly=True)
    line_ids = fields.One2many('lab.result.entry.line', 'entry_id', 'Résultats')
    comment = fields.Text('Commentaire')

    def action_apply(self):
        self.ensure_one()
        for line in self.line_ids:
            line.result_id.value_text = line.value_text
        if self.comment:
            self.request_id.message_post(body=self.comment)
        self.request_id.action_analyse()
        return {'type': 'ir.actions.act_window_close'}


class LabResultEntryLine(models.TransientModel):
    _name = 'lab.result.entry.line'
    _description = 'Ligne de saisie'

    entry_id = fields.Many2one('lab.result.entry', required=True, ondelete='cascade')
    result_id = fields.Many2one('lab.result', required=True, readonly=True)
    analysis_id = fields.Many2one(related='result_id.analysis_id')
    unit = fields.Char(related='result_id.unit')
    value_text = fields.Char('Résultat')
