from datetime import date, datetime

from odoo import _
from odoo.http import Controller, request, route
from odoo.tools import email_normalize

from ..models.lab_slot import SLOT_FORMAT


class LabBooking(Controller):

    def _render_form(self, error=None, values=None):
        Slot = request.env['lab.slot']
        return request.render('lab_portal.booking_form', {
            'choices': [(s.strftime(SLOT_FORMAT), Slot._format_local(s)) for s in Slot._get_available_slots(date.today())],
            'error': error,
            'values': values or {},
        })

    @route('/rdv', type='http', auth='public', website=True, sitemap=True)
    def booking_form(self, **kw):
        return self._render_form()

    @route('/rdv/confirmer', type='http', auth='public', website=True, methods=['POST'], sitemap=False)
    def booking_confirm(self, slot='', name='', phone='', email='', comment='', **kw):
        values = {'name': name.strip(), 'phone': phone.strip(), 'email': email.strip(), 'comment': comment.strip()}
        try:
            start = datetime.strptime(slot, SLOT_FORMAT)
        except ValueError:
            return self._render_form(_("Choisissez un créneau dans la liste."), values)
        if not (values['name'] and values['phone'] and email_normalize(values['email'])):
            return self._render_form(_("Indiquez votre nom, votre téléphone et une adresse e-mail valide."), values)
        event = request.env['lab.slot']._book(start, **values)
        if not event:
            return self._render_form(_("Ce créneau vient d'être réservé : choisissez-en un autre."), values)
        return request.render('lab_portal.booking_done', {'event': event})
