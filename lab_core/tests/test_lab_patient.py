from odoo.exceptions import AccessError
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
