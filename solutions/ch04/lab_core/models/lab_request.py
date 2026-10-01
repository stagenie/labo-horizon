from odoo import fields, models


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

    def _get_sample_types(self):
        """ Types de prélèvement nécessaires aux demandes, sans doublon, triés. """
        return sorted(set(self.result_ids.analysis_id.mapped('sample_type')))

    def _get_pending_results(self):
        """ Résultats encore sans valeur. """
        return self.result_ids.filtered(lambda r: not (r.value_text or '').strip())

    def _get_results_by_code(self):
        return self.result_ids.sorted('analysis_code')

    def _get_blood_results(self):
        """ Résultats des analyses faites sur un tube de sang. """
        return self.result_ids.filtered(lambda r: r.analysis_id.sample_type == 'blood')
