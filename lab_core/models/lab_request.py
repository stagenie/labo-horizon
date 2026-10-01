from odoo import api, fields, models
from odoo.fields import Command


class LabRequest(models.Model):
    _name = 'lab.request'
    _description = "Demande d'analyses"
    _order = 'date_request desc, id desc'

    name = fields.Char('Numéro', required=True, readonly=True, copy=False, default='Nouvelle')
    patient_id = fields.Many2one('lab.patient', 'Patient', required=True, index=True, ondelete='restrict')
    prescriber_id = fields.Many2one('res.partner', 'Prescripteur', domain=[('is_company', '=', False)])
    date_request = fields.Datetime('Date', required=True, default=fields.Datetime.now)
    note = fields.Text('Renseignements cliniques')
    result_ids = fields.One2many('lab.result', 'request_id', 'Résultats', copy=True)
    sample_ids = fields.One2many('lab.sample', 'request_id', 'Tubes', copy=False)
    panel_ids = fields.Many2many('lab.panel', string='Bilans')
    patient_gender = fields.Selection(related='patient_id.gender')
    abnormal_count = fields.Integer('Hors normes', compute='_compute_abnormal_count', store=True)

    @api.depends('result_ids.flag')
    def _compute_abnormal_count(self):
        for request in self:
            request.abnormal_count = len(request.result_ids.filtered(lambda r: r.flag in ('low', 'high')))

    def _get_sample_types(self):
        """ Types de prélèvement nécessaires aux demandes, sans doublon, triés. """
        return sorted(set(self.result_ids.analysis_id.mapped('sample_type')))

    def _get_pending_results(self):
        """ Résultats encore sans valeur. """
        return self.result_ids.filtered(lambda r: not (r.value_text or '').strip())

    def _get_results_by_code(self):
        return self.result_ids.sorted('analysis_code')

    def _sync_results_from_panels(self):
        """ Ajoute une ligne de résultat pour chaque analyse des bilans qui n'en a pas encore. """
        for request in self:
            missing = request.panel_ids.analysis_ids - request.result_ids.analysis_id
            if missing:
                request.result_ids = [Command.create({'analysis_id': a.id}) for a in missing]

    def action_load_panels(self):
        self._sync_results_from_panels()
