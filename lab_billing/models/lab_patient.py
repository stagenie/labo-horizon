from odoo import fields, models


class LabPatient(models.Model):
    _inherit = 'lab.patient'

    partner_id = fields.Many2one('res.partner', 'Contact', readonly=True, copy=False)
    insurer_id = fields.Many2one('lab.insurer', 'Mutuelle')

    def _get_or_create_partner(self):
        """Contact Odoo du patient, créé au premier besoin (la première facture, Ch.15)."""
        self.ensure_one()
        if not self.partner_id:
            self.partner_id = self.env['res.partner'].create({
                'name': self.name,
                'phone': self.phone,
                'email': self.email,
            })
        return self.partner_id
