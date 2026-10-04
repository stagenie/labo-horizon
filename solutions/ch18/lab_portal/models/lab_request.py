from odoo import _, api, models
from odoo.exceptions import UserError


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

    def action_validate(self):
        to_notify = self.filtered(lambda r: r.state == 'analysed')
        res = super().action_validate()
        to_notify.filtered(lambda r: r.state == 'validated')._notify_results_ready()
        return res

    def _notify_results_ready(self):
        """Courriel « résultats disponibles » : un lien, aucune valeur, et seulement à qui peut l'ouvrir."""
        template = self.env.ref('lab_portal.mail_template_results_ready')
        for request in self:
            patient = request.patient_id
            if patient.email and not patient.is_confidential and patient._has_portal_access():
                template.send_mail(request.id)

    def action_resend_results_mail(self):
        """Exercice 18.2 : renvoyer l'e-mail des résultats, seulement à un patient qui peut l'ouvrir."""
        for request in self:
            patient = request.patient_id
            if not (patient.email and not patient.is_confidential and patient._has_portal_access()):
                raise UserError(_("%s : le patient n'a pas d'accès au portail, aucun e-mail n'est envoyé.", patient.name))
        self.filtered(lambda r: r.state == 'validated')._notify_results_ready()
        return True
