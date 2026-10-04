from datetime import datetime, time, timedelta
from zoneinfo import ZoneInfo

from psycopg2 import IntegrityError

from odoo import _, api, fields, models
from odoo.fields import Command

WEEKDAYS = [('0', 'Lundi'), ('1', 'Mardi'), ('2', 'Mercredi'), ('3', 'Jeudi'),
            ('4', 'Vendredi'), ('5', 'Samedi'), ('6', 'Dimanche')]
LAB_TZ = 'Europe/Paris'          # heure des plages et de l'affichage
SLOT_FORMAT = '%Y-%m-%d %H:%M:%S'
BOOKING_DAYS = 7
UTC = ZoneInfo('UTC')


class LabSlot(models.Model):
    _name = 'lab.slot'
    _description = "Plage d'ouverture des prélèvements"
    _order = 'weekday, hour_from'

    weekday = fields.Selection(WEEKDAYS, 'Jour', required=True)
    hour_from = fields.Float('De', required=True)
    hour_to = fields.Float('À', required=True)
    duration = fields.Float('Durée', default=0.25, required=True)

    _check_hours = models.Constraint(
        'CHECK (hour_from >= 0 AND hour_to <= 24 AND hour_from < hour_to AND duration > 0)',
        "Une plage commence avant de finir, entre 0 h et 24 h, avec une durée positive.")

    @api.model
    def _booking_days(self):
        """Fenêtre de réservation, réglable par le paramètre système lab_portal.booking_days."""
        days = self.env['ir.config_parameter'].sudo().get_int('lab_portal.booking_days', BOOKING_DAYS)
        return days if days > 0 else BOOKING_DAYS

    @api.model
    def _get_available_slots(self, date_from, days=None):
        """Créneaux libres et futurs, en UTC sans fuseau (comme Odoo stocke les dates)."""
        days = days or self._booking_days()
        zone = ZoneInfo(LAB_TZ)
        plages = self.sudo().search([])
        taken = set(self.env['calendar.event'].sudo().search([
            ('lab_booking', '=', True),
            ('start', '>=', datetime.combine(date_from - timedelta(days=1), time.min)),
            ('start', '<', datetime.combine(date_from + timedelta(days=days + 1), time.min)),
        ]).mapped('start'))
        now = datetime.now(UTC).replace(tzinfo=None)
        slots = []
        for offset in range(days):
            day = date_from + timedelta(days=offset)
            for plage in plages.filtered(lambda p: int(p.weekday) == day.weekday()):
                hour = plage.hour_from
                while hour + plage.duration <= plage.hour_to + 1e-6:
                    minutes = round(hour * 60)
                    local = datetime.combine(day, time(minutes // 60, minutes % 60), tzinfo=zone)
                    start = local.astimezone(UTC).replace(tzinfo=None)
                    if start > now and start not in taken:
                        slots.append(start)
                    hour += plage.duration
        return sorted(slots)

    @api.model
    def _format_local(self, start_utc):
        local = start_utc.replace(tzinfo=UTC).astimezone(ZoneInfo(LAB_TZ))
        return f"{dict(WEEKDAYS)[str(local.weekday())]} {local:%d/%m} à {local:%H:%M}"

    @api.model
    def _lab_today(self):
        """La date du jour au laboratoire (le serveur compte en UTC)."""
        return datetime.now(ZoneInfo(LAB_TZ)).date()

    @api.model
    def _book(self, start_utc, name, phone, email, comment=''):
        """Rendez-vous créé si le créneau est proposé et encore libre ; False sinon.
        Le contrôle reprend la liste du formulaire : un créneau de la grille hors de la fenêtre
        de réservation n'est pas proposé, il est refusé."""
        if start_utc not in self._get_available_slots(self._lab_today()):
            return False
        try:
            with self.env.cr.savepoint():
                return self._create_booking_event(start_utc, name, phone, email, comment)
        except IntegrityError:          # réservé entre-temps par un autre visiteur
            return False

    @api.model
    def _create_booking_event(self, start_utc, name, phone, email, comment=''):
        """Le visiteur n'a aucun droit : le rendez-vous est créé en superutilisateur, champ par champ.
        Le nom du rendez-vous reste neutre : l'agenda est lu par tous les salariés, le contact du
        patient par le seul secrétariat."""
        return self.env['calendar.event'].sudo().create({
            'name': _("Prélèvement"),
            'lab_contact_name': name,
            'start': start_utc,
            'stop': start_utc + timedelta(minutes=15),
            'lab_booking': True,
            'lab_contact_phone': phone,
            'lab_contact_email': email,
            'description': comment,
            'user_id': False,
            'partner_ids': [Command.clear()],
        })
