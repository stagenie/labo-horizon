from odoo import fields, models


class AccountMove(models.Model):
    _inherit = 'account.move'

    lab_request_ids = fields.Many2many(
        'lab.request', 'lab_request_account_move_rel', 'move_id', 'request_id',
        string='Demandes du laboratoire', readonly=True, copy=False)
