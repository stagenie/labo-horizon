from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

from odoo import api, fields, models

from .lab_slot import LAB_TZ


class CalendarEvent(models.Model):
    _inherit = 'calendar.event'

    lab_booking = fields.Boolean('RDV laboratoire', index=True)
    lab_contact_name = fields.Char('Patient', groups='lab_core.group_lab_secretary')
    lab_contact_phone = fields.Char('Téléphone du patient', groups='lab_core.group_lab_secretary')
    lab_contact_email = fields.Char('E-mail du patient', groups='lab_core.group_lab_secretary')
    lab_reminder_sent = fields.Boolean('Rappel envoyé', copy=False)

    _lab_booking_start_uniq = models.UniqueIndex(
        "(start) WHERE lab_booking IS TRUE AND active IS TRUE", "Ce créneau est déjà réservé.")

    def lab_display_start(self):
        """Heure locale du rendez-vous pour les courriels. get_display_time_tz() ne convient pas :
        l'heure y est formatée dans le fuseau de l'utilisateur, pas dans celui demandé."""
        self.ensure_one()
        local = self.start.replace(tzinfo=ZoneInfo('UTC')).astimezone(ZoneInfo(LAB_TZ))
        return local.strftime('%d/%m/%Y à %H:%M')

    @api.model
    def _cron_lab_remind(self):
        """Rappel des rendez-vous des prochaines 24 heures, une seule fois par rendez-vous.
        L'action planifiée passe toutes les heures : un rendez-vous pris tard pour le lendemain
        matin reçoit son rappel au passage suivant."""
        now = datetime.now(ZoneInfo('UTC')).replace(tzinfo=None)
        events = self.search([
            ('lab_booking', '=', True),
            ('lab_reminder_sent', '=', False),
            ('lab_contact_email', '!=', False),
            ('start', '>=', now),
            ('start', '<', now + timedelta(hours=24)),
        ])
        template = self.env.ref('lab_portal.mail_template_booking_reminder')
        for event in events:
            template.send_mail(event.id)
        events.lab_reminder_sent = True
        return len(events)
