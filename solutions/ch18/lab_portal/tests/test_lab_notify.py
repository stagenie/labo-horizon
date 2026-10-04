from datetime import date, datetime, timedelta
from zoneinfo import ZoneInfo

from odoo.exceptions import UserError
from odoo.fields import Command
from odoo.tests import TransactionCase, new_test_user, tagged

PARIS = ZoneInfo('Europe/Paris')
UTC = ZoneInfo('UTC')


@tagged('post_install', '-at_install')
class TestLabNotify(TransactionCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env.user.group_ids |= cls.env.ref('lab_core.group_lab_biologist')
        cls.Mail = cls.env['mail.mail']

    def _patient(self, name, email=None, portal=True, confidential=False):
        patient = self.env['lab.patient'].create({'name': name, 'birthdate': date(1990, 5, 5), 'gender': 'male',
                                                  'email': email, 'is_confidential': confidential})
        if portal:
            action = patient.action_open_portal_wizard()
            self.env['portal.wizard'].browse(action['res_id']).user_ids.action_grant_access()
        return patient

    def _analysed(self, patient):
        req = self.env['lab.request'].create({
            'patient_id': patient.id, 'panel_ids': [Command.set(self.env.ref('lab_core.panel_eal').ids)]})
        req._sync_results_from_panels()
        req.action_sample()
        req.result_ids.value_text = '1'
        req.action_analyse()
        return req

    def _mails_to(self, email):
        return self.Mail.search([('email_to', 'ilike', email)])

    def test_validation_sends_mail(self):
        req = self._analysed(self._patient('Sami Haddad', 'sami@example.com'))
        req.action_validate()
        mail = self._mails_to('sami@example.com').filtered(lambda m: req.name in (m.subject or ''))
        self.assertEqual(len(mail), 1)
        self.assertIn(f'/my/results/{req.id}', mail.body_html)
        self.assertNotIn('Cholestérol', mail.body_html)        # aucune valeur ni analyse dans le courriel
        self.assertEqual(mail.email_from, self.env.company.email_formatted)   # le laboratoire, pas l'utilisateur

    def test_no_mail_without_portal_access(self):
        cases = [self._patient('Sans Portail', 'sansportail@example.com', portal=False),
                 self._patient('Sans Courriel', portal=False),
                 self._patient('Dossier Y', 'y@example.com', portal=False, confidential=True)]
        for patient in cases:
            req = self._analysed(patient)
            req.action_validate()
            self.assertEqual(req.state, 'validated')
        self.assertFalse(self._mails_to('sansportail@example.com'))
        self.assertFalse(self._mails_to('y@example.com'))

    def test_biologist_validation_sends_mail(self):
        req = self._analysed(self._patient('Rita Blanc', 'rita@example.com'))
        biologist = new_test_user(self.env, 'biologiste_mail', groups='lab_core.group_lab_biologist')
        req.with_user(biologist).action_validate()
        self.assertTrue(self._mails_to('rita@example.com'))

    def _booking(self, start, email):
        """Rendez-vous à l'heure UTC donnée (sans fuseau, comme Odoo stocke les dates)."""
        return self.env['calendar.event'].create({'name': 'RDV', 'start': start, 'stop': start + timedelta(minutes=15),
                                                  'lab_booking': True, 'lab_contact_email': email})

    def _in(self, **delta):
        return (datetime.now(UTC) + timedelta(**delta)).replace(tzinfo=None, second=0, microsecond=0)

    def test_cron_reminds_next_24_hours(self):
        self.env['calendar.event'].search([('lab_booking', '=', True)]).unlink()
        self._booking(self._in(hours=20), 'bientot@example.com')
        self._booking(self._in(hours=30), 'plustard@example.com')
        self._booking(self._in(hours=-2), 'passe@example.com')
        self.assertEqual(self.env['calendar.event']._cron_lab_remind(), 1)
        self.assertTrue(self._mails_to('bientot@example.com'))
        self.assertFalse(self._mails_to('plustard@example.com'))
        self.assertFalse(self._mails_to('passe@example.com'))

    def test_late_booking_reminded(self):
        self.env['calendar.event'].search([('lab_booking', '=', True)]).unlink()
        Event = self.env['calendar.event']
        Event._cron_lab_remind()
        self._booking(self._in(hours=1), 'tardif@example.com')            # pris après le passage précédent
        self.assertEqual(Event._cron_lab_remind(), 1)
        self.assertTrue(self._mails_to('tardif@example.com'))

    def test_cron_reminds_once(self):
        self.env['calendar.event'].search([('lab_booking', '=', True)]).unlink()
        self._booking(self._in(hours=3), 'unefois@example.com')
        Event = self.env['calendar.event']
        self.assertEqual(Event._cron_lab_remind(), 1)
        self.assertEqual(Event._cron_lab_remind(), 0)
        mail = self._mails_to('unefois@example.com')
        self.assertEqual(len(mail), 1)
        self.assertEqual(mail.email_from, self.env.company.email_formatted)

    def test_reminder_time_in_paris(self):
        self.env.user.tz = False                    # un utilisateur sans fuseau
        self.env['calendar.event'].search([('lab_booking', '=', True)]).unlink()
        start = self._in(hours=5)
        self._booking(start, 'paris@example.com')
        self.env['calendar.event']._cron_lab_remind()
        local = start.replace(tzinfo=UTC).astimezone(PARIS)
        self.assertIn(local.strftime('%d/%m/%Y à %H:%M'), self._mails_to('paris@example.com').body_html)

    def test_cron_record(self):
        cron = self.env.ref('lab_portal.ir_cron_lab_remind')
        self.assertEqual((cron.interval_number, cron.interval_type), (1, 'hours'))
        self.assertTrue(cron.active)

    def test_booking_sends_confirmation(self):
        Slot = self.env['lab.slot']
        start = Slot._get_available_slots(Slot._lab_today())[0]
        event = self.env['lab.slot']._book(start, 'Léa Morel', '+33600000041', 'lea@example.com')
        mail = self._mails_to('lea@example.com')
        self.assertEqual(len(mail), 1)
        self.assertIn(event.lab_display_start(), mail.body_html)
        self.assertEqual(mail.email_from, self.env.company.email_formatted)

    def test_resend_results_mail(self):
        req = self._analysed(self._patient('Yanis Roche', 'yanis@example.com'))
        req.action_validate()
        secretary = new_test_user(self.env, 'secretaire_renvoi', groups='lab_core.group_lab_secretary')
        req.with_user(secretary).action_resend_results_mail()
        self.assertEqual(len(self._mails_to('yanis@example.com')), 2)

    def test_resend_refused_without_portal(self):
        req = self._analysed(self._patient('Hors Portail', 'horsportail@example.com', portal=False))
        req.action_validate()
        with self.assertRaises(UserError):
            req.action_resend_results_mail()
        self.assertFalse(self._mails_to('horsportail@example.com'))
