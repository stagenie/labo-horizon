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
