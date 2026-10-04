from odoo import _, models
from odoo.exceptions import UserError


class LabPatient(models.Model):
    _inherit = 'lab.patient'

    def action_open_portal_wizard(self):
        """Ouvre l'assistant standard d'accès au portail sur le contact du patient, créé au besoin."""
        self.ensure_one()
        if self.is_confidential:
            raise UserError(_("%s : un dossier confidentiel ne s'ouvre pas au portail.", self.name))
        if not self.email:
            raise UserError(_("%s : renseignez l'e-mail du patient avant d'ouvrir son accès.", self.name))
        partner = self._get_or_create_partner()
        if partner.email != self.email:     # contact créé à la facture, e-mail saisi ou corrigé depuis
            partner.email = self.email
        return self.env['portal.wizard'].with_context(default_partner_ids=partner.ids).action_open_wizard()
