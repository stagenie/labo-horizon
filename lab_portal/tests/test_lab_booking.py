from datetime import date, datetime, timedelta

from psycopg2 import IntegrityError

from odoo.exceptions import AccessError
from odoo.tests import HttpCase, new_test_user, tagged
from odoo.tools import mute_logger


@tagged('post_install', '-at_install')
class TestLabBooking(HttpCase):

    def _next_weekday(self):
        """Prochain jour de semaine (lundi-vendredi, 7 h 30 - 10 h 30), dans la fenêtre de réservation."""
        day = self.env['lab.slot']._lab_today() + timedelta(days=1)
        while day.weekday() > 4:
            day += timedelta(days=1)
        return day

    def _day_slots(self):
        return self.env['lab.slot']._get_available_slots(self._next_weekday(), days=1)

    def _post(self, **data):
        page = self.url_open('/rdv').text
        data['csrf_token'] = page.split('name="csrf_token" value="')[1].split('"')[0]
        return self.url_open('/rdv/confirmer', data=data)

    def _bookings(self):
        return self.env['calendar.event'].search([('lab_booking', '=', True)])

    def test_slots_generated(self):
        self.assertEqual(len(self._day_slots()), 12)      # 7 h 30 - 10 h 30, pas de 15 min

    def test_slot_format_local(self):
        start = self._day_slots()[0]
        self.assertRegex(self.env['lab.slot']._format_local(start), r'^(Lundi|Mardi|Mercredi|Jeudi|Vendredi) \d\d/\d\d à 07:30$')

    def test_booking_same_slot_twice(self):
        Slot = self.env['lab.slot']
        start = self._day_slots()[0]
        first = Slot._book(start, 'Emma Roux', '+33600000031', 'emma@example.com')
        second = Slot._book(start, 'Paul Roux', '+33600000032', 'paul@example.com')
        self.assertTrue(first.lab_booking)
        self.assertFalse(second)
        self.assertNotIn(start, self._day_slots())

    def test_duplicate_booking_refused_by_database(self):
        start = self._day_slots()[2]
        vals = {'name': 'RDV', 'start': start, 'stop': start + timedelta(minutes=15), 'lab_booking': True}
        self.env['calendar.event'].create(vals)
        with self.assertRaises(IntegrityError), mute_logger('odoo.sql_db'):
            with self.env.cr.savepoint():
                self.env['calendar.event'].create(vals)

    def test_public_booking_page(self):
        res = self.url_open('/rdv')
        self.assertEqual(res.status_code, 200)
        self.assertIn('Prendre rendez-vous', res.text)

    def test_public_booking_post(self):
        start = self._day_slots()[1]
        res = self._post(slot=start.strftime('%Y-%m-%d %H:%M:%S'), name='Inès Laurent',
                         phone='+33600000033', email='ines@example.com')
        self.assertEqual(res.status_code, 200)
        self.assertIn('Rendez-vous confirmé', res.text)
        event = self._bookings().filtered(lambda e: e.start == start)
        self.assertEqual(event.lab_contact_email, 'ines@example.com')
        self.assertFalse(event.partner_ids)

    def test_booking_rejects_forged_slot(self):
        before = len(self._bookings())
        day = self._next_weekday()
        night = datetime.combine(day, datetime.min.time()).replace(hour=1)          # 3 h à Paris : jamais proposé
        past = datetime.combine(date.today() - timedelta(days=7), datetime.min.time()).replace(hour=6)
        for slot in ('demain matin', night.strftime('%Y-%m-%d %H:%M:%S'), past.strftime('%Y-%m-%d %H:%M:%S')):
            res = self._post(slot=slot, name='Faux', phone='+33600000034', email='faux@example.com')
            self.assertEqual(res.status_code, 200)
            self.assertIn('alert', res.text)
        self.assertEqual(len(self._bookings()), before)

    def test_booking_rejects_slot_outside_window(self):
        before = len(self._bookings())
        far_day = self._next_weekday() + timedelta(days=28)            # créneau de la grille, hors des 7 jours
        far = self.env['lab.slot']._get_available_slots(far_day, days=1)[0]
        for slot in (far.strftime('%Y-%m-%d %H:%M:%S'), '9999-12-31 07:30:00'):
            res = self._post(slot=slot, name='Trop Tôt', phone='+33600000038', email='tot@example.com')
            self.assertEqual(res.status_code, 200)
            self.assertIn('alert', res.text)
        self.assertEqual(len(self._bookings()), before)

    def test_archived_booking_frees_slot(self):
        Slot = self.env['lab.slot']
        start = self._day_slots()[6]
        first = Slot._book(start, 'Emma Roux', '+33600000031', 'emma@example.com')
        first.active = False                                             # rendez-vous annulé, archivé
        self.assertIn(start, self._day_slots())
        self.assertTrue(Slot._book(start, 'Paul Roux', '+33600000032', 'paul@example.com'))

    def test_contact_hidden_from_other_staff(self):
        start = self._day_slots()[7]
        event = self.env['lab.slot']._book(start, 'Nina Petit', '+33600000036', 'nina@example.com')
        self.assertEqual(event.lab_contact_name, 'Nina Petit')
        self.assertNotIn('Nina', event.name)
        employee = new_test_user(self.env, 'salarie_rdv', groups='base.group_user')
        event = event.with_user(employee)
        self.assertEqual(event.name, 'Prélèvement')
        for field in ('lab_contact_name', 'lab_contact_phone', 'lab_contact_email'):
            with self.assertRaises(AccessError):
                event[field]
            event.invalidate_recordset()

    def test_booking_rejects_bad_contact(self):
        start = self._day_slots()[3].strftime('%Y-%m-%d %H:%M:%S')
        before = len(self._bookings())
        for name, email in (('   ', 'vide@example.com'), ('Sans Arobase', 'pas-une-adresse')):
            res = self._post(slot=start, name=name, phone='+33600000035', email=email)
            self.assertEqual(res.status_code, 200)
            self.assertIn('adresse e-mail valide', res.text)
        self.assertEqual(len(self._bookings()), before)

    def test_slot_hours_checked(self):
        with self.assertRaises(IntegrityError), mute_logger('odoo.sql_db'):
            with self.env.cr.savepoint():
                self.env['lab.slot'].create({'weekday': '0', 'hour_from': 11.0, 'hour_to': 9.0})

    def test_secretary_sees_bookings(self):
        start = self._day_slots()[4]
        self.env['lab.slot']._book(start, 'Nina Petit', '+33600000036', 'nina@example.com')
        secretary = new_test_user(self.env, 'secretaire_rdv', groups='lab_core.group_lab_secretary')
        found = self.env['calendar.event'].with_user(secretary).search([('lab_booking', '=', True), ('start', '=', start)])
        self.assertEqual(found.lab_contact_email, 'nina@example.com')

    def test_booking_list_labels(self):
        arch = self.env['calendar.event'].get_views([(self.env.ref('lab_portal.calendar_event_view_list_lab').id, 'list')])
        arch = arch['views']['list']['arch']
        self.assertIn('string="Début"', arch)
        self.assertIn('string="Rendez-vous"', arch)

    def test_booking_list_in_day_order(self):
        # calendar.event est trié « start desc » : l'accueil lit la journée dans l'ordre
        arch = self.env['calendar.event'].get_views([(self.env.ref('lab_portal.calendar_event_view_list_lab').id, 'list')])
        self.assertIn('default_order="start"', arch['views']['list']['arch'])
