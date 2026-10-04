from odoo.exceptions import AccessError, MissingError
from odoo.http import request, route

from odoo.addons.portal.controllers.portal import CustomerPortal


class LabPortal(CustomerPortal):

    def _prepare_portal_counter_values(self, counter):
        if counter == 'lab_result_count':
            return 'lab.request', request.env['lab.request']._lab_portal_domain(), 'read'
        return super()._prepare_portal_counter_values(counter)

    def _lab_request_check_access(self, request_id):
        """La demande ET ses résultats. _document_check_access ne contrôle que la demande et la rend
        en superutilisateur : sans le second contrôle, ses résultats se liraient sans droit."""
        request_sudo = self._document_check_access('lab.request', request_id)
        request.env['lab.result'].browse(request_sudo.result_ids.ids).check_access('read')
        return request_sudo

    @route('/my/results', type='http', auth='user', website=True)
    def portal_my_lab_results(self, **kw):
        LabRequest = request.env['lab.request']
        values = self._prepare_portal_layout_values()
        values.update({
            'lab_requests': LabRequest.search(LabRequest._lab_portal_domain()),
            'page_name': 'lab_results',
        })
        return request.render('lab_portal.portal_my_lab_results', values)

    @route('/my/results/<int:request_id>', type='http', auth='user', website=True)
    def portal_my_lab_result(self, request_id, **kw):
        try:
            request_sudo = self._lab_request_check_access(request_id)
        except (AccessError, MissingError):
            return request.redirect('/my')
        values = self._prepare_portal_layout_values()
        values.update({'lab_request': request_sudo, 'page_name': 'lab_result'})
        return request.render('lab_portal.portal_my_lab_result', values)

    @route('/my/results/<int:request_id>/pdf', type='http', auth='user', website=True)
    def portal_my_lab_result_pdf(self, request_id, **kw):
        try:
            request_sudo = self._lab_request_check_access(request_id)
        except (AccessError, MissingError):
            return request.redirect('/my')
        return self._show_report(model=request_sudo, report_type='pdf',
                                 report_ref='lab_core.action_report_lab_request', download=True)
