from datetime import date

from odoo.exceptions import UserError
from odoo.fields import Command
from odoo.tests import HttpCase, new_test_user, tagged


@tagged('post_install', '-at_install')
class TestLabPortal(HttpCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env.user.group_ids |= cls.env.ref('lab_core.group_lab_biologist')
        Patient = cls.env['lab.patient']
        cls.pa = Patient.create({'name': 'Patient A', 'birthdate': date(1980, 1, 1), 'gender': 'male',
                                 'email': 'pa@example.com'})
        cls.pb = Patient.create({'name': 'Patient B', 'birthdate': date(1981, 1, 1), 'gender': 'female',
                                 'email': 'pb@example.com'})
        cls.user_a = cls._grant_portal(cls.pa)
        cls.user_a.password = 'patient_a_pwd'
        cls.req_a = cls._validated(cls.pa)
        cls.req_b = cls._validated(cls.pb)
        cls.req_a_draft = cls.env['lab.request'].create({
            'patient_id': cls.pa.id, 'panel_ids': [Command.set(cls.env.ref('lab_core.panel_eal').ids)]})

    @classmethod
    def _grant_portal(cls, patient):
        action = patient.action_open_portal_wizard()
        wizard = cls.env['portal.wizard'].browse(action['res_id'])
        wizard.user_ids.action_grant_access()
        return patient.partner_id.user_ids

    @classmethod
    def _validated(cls, patient):
        req = cls.env['lab.request'].create({
            'patient_id': patient.id, 'panel_ids': [Command.set(cls.env.ref('lab_core.panel_eal').ids)]})
        req._sync_results_from_panels()
        req.action_sample()
        req.result_ids.value_text = '1,8'
        req.action_analyse()
        req.action_validate()
        return req

    def test_portal_wizard_targets_patient_contact(self):
        never_invoiced = self.env['lab.patient'].create({'name': 'Léa Martin', 'gender': 'female',
                                                         'email': 'lea@example.com'})
        self.assertFalse(never_invoiced.partner_id)
        action = never_invoiced.action_open_portal_wizard()
        wizard = self.env['portal.wizard'].browse(action['res_id'])
        self.assertEqual(wizard.user_ids.partner_id, never_invoiced.partner_id)
        self.assertEqual(never_invoiced.partner_id.email, 'lea@example.com')
        self.assertTrue(self.user_a._is_portal())

    def test_portal_wizard_uses_patient_email(self):
        invoiced_first = self.env['lab.patient'].create({'name': 'Hugo Blanc', 'gender': 'male'})
        invoiced_first._get_or_create_partner()            # contact créé à la facture, sans e-mail
        invoiced_first.email = 'hugo@example.com'          # e-mail saisi ensuite sur la fiche patient
        action = invoiced_first.action_open_portal_wizard()
        wizard = self.env['portal.wizard'].browse(action['res_id'])
        self.assertEqual(wizard.user_ids.email, 'hugo@example.com')

    def test_confidential_patient_not_opened_to_portal(self):
        secret = self.env['lab.patient'].create({'name': 'Dossier X', 'gender': 'male', 'email': 'x@example.com',
                                                 'is_confidential': True})
        with self.assertRaisesRegex(UserError, 'confidentiel'):
            secret.action_open_portal_wizard()
        self.assertFalse(secret.partner_id)

    def test_patient_without_email_refused(self):
        no_mail = self.env['lab.patient'].create({'name': 'Sans Courriel', 'gender': 'male'})
        with self.assertRaisesRegex(UserError, 'e-mail'):
            no_mail.action_open_portal_wizard()

    def test_portal_list_shows_only_own_validated(self):
        self.authenticate(self.user_a.login, 'patient_a_pwd')
        res = self.url_open('/my/results')
        self.assertEqual(res.status_code, 200)
        self.assertIn(self.req_a.name, res.text)
        self.assertNotIn(self.req_b.name, res.text)
        self.assertNotIn(self.req_a_draft.name, res.text)

    def test_portal_detail_and_pdf(self):
        self.authenticate(self.user_a.login, 'patient_a_pwd')
        res = self.url_open(f'/my/results/{self.req_a.id}')
        self.assertIn('Cholestérol total', res.text)
        pdf = self.url_open(f'/my/results/{self.req_a.id}/pdf')
        self.assertEqual(pdf.headers.get('Content-Type'), 'application/pdf')
        self.assertIn('Compte_rendu', pdf.headers.get('Content-Disposition'))

    def test_portal_other_patient_denied(self):
        self.authenticate(self.user_a.login, 'patient_a_pwd')
        res = self.url_open(f'/my/results/{self.req_b.id}', allow_redirects=False)
        self.assertIn(res.status_code, (302, 303))
        self.assertNotIn(self.req_b.name, res.text)
        pdf = self.url_open(f'/my/results/{self.req_b.id}/pdf', allow_redirects=False)
        self.assertNotEqual(pdf.headers.get('Content-Type'), 'application/pdf')

    def test_confidential_after_access_hides_results(self):
        self.pa.is_confidential = True                     # dossier devenu confidentiel après l'ouverture du portail
        self.assertFalse(self.env['lab.request'].with_user(self.user_a).search([]))
        self.authenticate(self.user_a.login, 'patient_a_pwd')
        self.assertNotIn(self.req_a.name, self.url_open('/my/results').text)
        res = self.url_open(f'/my/results/{self.req_a.id}', allow_redirects=False)
        self.assertIn(res.status_code, (302, 303))
        pdf = self.url_open(f'/my/results/{self.req_a.id}/pdf', allow_redirects=False)
        self.assertNotEqual(pdf.headers.get('Content-Type'), 'application/pdf')

    def test_portal_record_rule(self):
        self.assertEqual(self.env['lab.request'].with_user(self.user_a).search([]), self.req_a)

    def test_portal_counter(self):
        self.authenticate(self.user_a.login, 'patient_a_pwd')
        res = self.make_jsonrpc_request('/my/counters', {'counters': {'lab_result_count': 'client_category'}})
        self.assertEqual(res['lab_result_count'], 1)

    def test_internal_user_lists_only_own(self):
        new_test_user(self.env, 'biologiste_portail', password='biologiste_pwd', groups='lab_core.group_lab_biologist')
        self.authenticate('biologiste_portail', 'biologiste_pwd')
        res = self.url_open('/my/results')
        self.assertEqual(res.status_code, 200)
        self.assertNotIn(self.req_a.name, res.text)
        self.assertNotIn(self.req_b.name, res.text)

    def test_secretary_cannot_read_results_via_portal(self):
        new_test_user(self.env, 'secretaire_portail', password='secretaire_pwd', groups='lab_core.group_lab_secretary')
        self.authenticate('secretaire_portail', 'secretaire_pwd')
        res = self.url_open(f'/my/results/{self.req_a.id}', allow_redirects=False)
        self.assertNotIn('Cholestérol total', res.text)
        pdf = self.url_open(f'/my/results/{self.req_a.id}/pdf', allow_redirects=False)
        self.assertNotEqual(pdf.headers.get('Content-Type'), 'application/pdf')

    def test_list_has_download_links(self):
        self.authenticate(self.user_a.login, 'patient_a_pwd')
        res = self.url_open('/my/results')
        self.assertIn(f'/my/results/{self.req_a.id}/pdf', res.text)

    def test_list_sorted_by_name(self):
        second = self._validated(self.pa)
        self.authenticate(self.user_a.login, 'patient_a_pwd')
        text = self.url_open('/my/results?sortby=name').text
        self.assertLess(text.index(self.req_a.name), text.index(second.name))
        text = self.url_open('/my/results?sortby=date').text
        self.assertLess(text.index(second.name), text.index(self.req_a.name))
