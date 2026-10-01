from datetime import date

from dateutil.relativedelta import relativedelta

from odoo.exceptions import AccessError, ValidationError
from odoo.tests import new_test_user, tagged

from .common import LabCoreCommon


@tagged('post_install', '-at_install')
class TestLabPatient(LabCoreCommon):

    def test_patient_is_searchable(self):
        self.assertEqual(self.Patient.search([('name', '=', 'Alice Martin')]), self.alice)

    def test_default_order_by_name(self):
        self.Patient.create({'name': 'Zoé Arnaud'})
        names = self.Patient.search([('name', 'in', ['Alice Martin', 'Zoé Arnaud'])]).mapped('name')
        self.assertEqual(names, ['Alice Martin', 'Zoé Arnaud'])

    def test_action_opens_patients(self):
        action = self.env.ref('lab_core.lab_patient_action')
        self.assertEqual((action.res_model, action.view_mode), ('lab.patient', 'list,form'))

    def test_internal_user_has_access(self):
        user = new_test_user(self.env, 'lab_internal', groups='base.group_user')
        self.Patient.with_user(user).create({'name': 'Bob Leroy'})

    def test_portal_user_has_no_access(self):
        portal = new_test_user(self.env, 'lab_portal_user', groups='base.group_portal')
        with self.assertRaises(AccessError):
            self.Patient.with_user(portal).search([])

    def test_notes_html_is_sanitized(self):
        self.alice.notes = '<p>Allergie au latex</p><script>alert(1)</script>'
        self.assertIn('Allergie au latex', self.alice.notes)
        self.assertNotIn('<script', self.alice.notes)

    def test_age(self):
        self.assertEqual(self.alice.age, relativedelta(date.today(), date(1992, 3, 14)).years)

    def test_age_without_birthdate(self):
        self.assertEqual(self.Patient.create({'name': 'Sans date'}).age, 0)

    def test_minor_search(self):
        child = self.Patient.create({'name': 'Léo Petit', 'birthdate': date.today() - relativedelta(years=10)})
        minors = self.Patient.search([('is_minor', '=', True)])
        self.assertIn(child, minors)
        self.assertNotIn(self.alice, minors)
        self.assertIn(self.alice, self.Patient.search([('is_minor', '=', False)]))

    def test_future_birthdate_refused(self):
        with self.assertRaises(ValidationError):
            self.Patient.create({'name': 'Futur', 'birthdate': date.today() + relativedelta(days=1)})
