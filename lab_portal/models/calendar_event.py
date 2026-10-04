from odoo import fields, models


class CalendarEvent(models.Model):
    _inherit = 'calendar.event'

    lab_booking = fields.Boolean('RDV laboratoire', index=True)
    lab_contact_name = fields.Char('Patient', groups='lab_core.group_lab_secretary')
    lab_contact_phone = fields.Char('Téléphone du patient', groups='lab_core.group_lab_secretary')
    lab_contact_email = fields.Char('E-mail du patient', groups='lab_core.group_lab_secretary')

    _lab_booking_start_uniq = models.UniqueIndex(
        "(start) WHERE lab_booking IS TRUE AND active IS TRUE", "Ce créneau est déjà réservé.")
