from odoo.exceptions import AccessError, UserError
from odoo.tests import new_test_user, tagged

from .common import LabCoreCommon


@tagged('post_install', '-at_install')
class TestLabSecurity(LabCoreCommon):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.secretary = new_test_user(cls.env, 'lab_sec', groups='lab_core.group_lab_secretary')
        cls.technician = new_test_user(cls.env, 'lab_tech', groups='lab_core.group_lab_technician')
        cls.biologist = new_test_user(cls.env, 'lab_bio', groups='lab_core.group_lab_biologist')
        cls.request = cls._new_request(cls, 'panel_eal')

    def test_secretary_cannot_read_results(self):
        self.request.with_user(self.secretary).read(['name', 'state'])   # autorisé
        with self.assertRaises(AccessError):
            self.request.result_ids.with_user(self.secretary).read(['value_text'])

    def test_secretary_creates_request_with_panels(self):
        req = self.env['lab.request'].with_user(self.secretary).create({
            'patient_id': self.alice.id,
            'panel_ids': [(6, 0, self.env.ref('lab_core.panel_bil1').ids)],
        })
        self.assertEqual(len(req.sudo().result_ids), 3)

    def test_technician_cannot_validate(self):
        req = self.request
        req.with_user(self.technician).action_sample()
        req.result_ids.value_text = '1'
        req.with_user(self.technician).action_analyse()
        with self.assertRaises(AccessError):
            req.with_user(self.technician).action_validate()
        req.with_user(self.biologist).action_validate()
        self.assertEqual(req.state, 'validated')

    def test_validation_activity_goes_to_a_biologist(self):
        req = self.request
        req.action_sample()
        req.result_ids.value_text = '1'
        req.with_user(self.technician).action_analyse()
        self.assertTrue(req.activity_ids.user_id.has_group('lab_core.group_lab_biologist'))

    def test_technician_cannot_delete_request(self):
        with self.assertRaises(AccessError):
            self.request.with_user(self.technician).unlink()

    def test_state_validated_write_refused(self):
        with self.assertRaises(UserError):
            self.request.with_user(self.technician).write({'state': 'validated'})

    def test_reset_draft_biologist_only(self):
        req = self.request
        req.action_sample()
        with self.assertRaises(AccessError):
            req.with_user(self.technician).action_reset_draft()

    def test_confidential_patient_hidden_from_secretary(self):
        vip = self.Patient.create({'name': 'Patient confidentiel', 'is_confidential': True})
        req = self.env['lab.request'].create({'patient_id': vip.id})
        self.assertNotIn(vip, self.Patient.with_user(self.secretary).search([]))
        self.assertNotIn(req, self.env['lab.request'].with_user(self.secretary).search([]))
        self.assertIn(vip, self.Patient.with_user(self.biologist).search([]))

    def test_technician_inherits_secretary_restriction(self):
        vip = self.Patient.create({'name': 'Patient confidentiel', 'is_confidential': True})
        self.assertNotIn(vip, self.Patient.with_user(self.technician).search([]))

    def test_internal_user_without_lab_group_has_no_access(self):
        user = new_test_user(self.env, 'lab_other', groups='base.group_user')
        with self.assertRaises(AccessError):
            self.Patient.with_user(user).search([])

    def test_secretary_cannot_move_request_forward(self):
        with self.assertRaises(AccessError):
            self.request.with_user(self.secretary).write({'state': 'sampled'})

    def test_only_biologist_moves_request_back_to_draft(self):
        req = self.request
        req.action_sample()
        with self.assertRaises(AccessError):
            req.with_user(self.technician).write({'state': 'draft'})
