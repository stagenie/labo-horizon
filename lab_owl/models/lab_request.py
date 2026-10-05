from odoo import _, api, models
from odoo.exceptions import UserError
from odoo.http.dispatcher import conceal_debug_traceback


class LabRequest(models.Model):
    _inherit = 'lab.request'

    @api.model
    def api_push_results(self, request_ref, results):
        """Point d'entrée des automates : {code d'analyse: valeur lue}. Tout ou rien, sans trace Python en retour."""
        with conceal_debug_traceback(UserError):
            return self._lab_push_results(request_ref, results)

    @api.model
    def _lab_push_results(self, request_ref, results):
        if not isinstance(results, dict) or not results:
            raise UserError(_("Aucun résultat reçu pour la demande %s.", request_ref))
        request = self.search([('name', '=', request_ref)], limit=1)
        if not request:
            raise UserError(_("Demande %s introuvable.", request_ref))
        if request.state == 'draft':
            raise UserError(_("Demande %s pas encore prélevée : elle n'attend pas de résultats.", request.name))
        if request.state == 'validated':
            raise UserError(_("Demande %s déjà validée : résultats verrouillés.", request.name))
        by_code = {result.analysis_code: result for result in request.result_ids}
        unknown = sorted(set(results) - set(by_code))
        if unknown:
            raise UserError(_("Analyses absentes de la demande %(req)s : %(codes)s.",
                              req=request.name, codes=', '.join(unknown)))
        unreadable = sorted(code for code, value in results.items()
                            if isinstance(value, bool) or not isinstance(value, (str, int, float))
                            or not str(value).strip())
        if unreadable:
            raise UserError(_("Valeurs illisibles pour la demande %(req)s : %(codes)s.",
                              req=request.name, codes=', '.join(unreadable)))
        for code, value in results.items():
            by_code[code].value_text = str(value)
        request.message_post(body=_("Résultats reçus de l'automate : %s.", ', '.join(sorted(results))))
        if request.state == 'sampled' and not request._get_pending_results():
            request.action_analyse()
        return {'request': request.name, 'state': request.state, 'abnormal': request.abnormal_count}
