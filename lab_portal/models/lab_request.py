from odoo import api, models


class LabRequest(models.Model):
    _name = 'lab.request'
    _inherit = ['lab.request', 'portal.mixin']

    def _compute_access_url(self):
        super()._compute_access_url()
        for request in self:
            request.access_url = f'/my/results/{request.id}'

    def _get_report_base_filename(self):
        """Nom du PDF téléchargé depuis le portail (_show_report l'exige)."""
        self.ensure_one()
        return f"Compte rendu - {self.name}"

    @api.model
    def _lab_portal_domain(self):
        """Les demandes de « Mes résultats » : celles du patient connecté, une fois validées.
        Le patient du portail ne lit pas les fiches patients : la lecture privilégiée se limite
        à retrouver les identifiants de ses propres fiches."""
        patients = self.env['lab.patient'].sudo().search([('partner_id', '=', self.env.user.partner_id.id)])
        return [('patient_id', 'in', patients.ids), ('state', '=', 'validated')]
