from odoo import fields, models


class CalendarEvent(models.Model):
    _inherit = 'calendar.event'

    lab_booking = fields.Boolean('RDV laboratoire', index=True)
    lab_contact_phone = fields.Char('Téléphone du patient')
    lab_contact_email = fields.Char('E-mail du patient')

    _lab_booking_start_uniq = models.UniqueIndex(
        "(start) WHERE lab_booking IS TRUE", "Ce créneau est déjà réservé.")
