from odoo import _, api, fields, models


class ResPartner(models.Model):
    _inherit = 'res.partner'

    lab_patient_ids = fields.One2many('lab.patient', 'partner_id', 'Fiches patient')
    lab_insurer_ids = fields.One2many('lab.insurer', 'partner_id', 'Fiche mutuelle')
    lab_request_count = fields.Integer('Demandes du laboratoire', compute='_compute_lab_request_count')

    @api.depends('lab_patient_ids.request_ids')
    def _compute_lab_request_count(self):
        for partner in self:
            partner.lab_request_count = len(partner.lab_patient_ids.request_ids)

    def action_view_lab_requests(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': _("Demandes"),
            'res_model': 'lab.request',
            'view_mode': 'list,form',
            'domain': [('patient_id', 'in', self.lab_patient_ids.ids)],
        }
