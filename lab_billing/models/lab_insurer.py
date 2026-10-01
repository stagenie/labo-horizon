from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class LabInsurer(models.Model):
    _name = 'lab.insurer'
    _description = 'Mutuelle'
    _inherits = {'res.partner': 'partner_id'}

    partner_id = fields.Many2one('res.partner', 'Contact', required=True, ondelete='cascade')
    coverage_rate = fields.Float('Prise en charge (%)', default=60.0)

    @api.constrains('coverage_rate')
    def _check_coverage_rate(self):
        for insurer in self:
            if not 0 <= insurer.coverage_rate <= 100:
                raise ValidationError(_("Le taux de prise en charge doit être compris entre 0 et 100."))
