from odoo.exceptions import UserError
from odoo.fields import Command
from odoo.tests import Form, tagged

from .common import LabCoreCommon


@tagged('post_install', '-at_install')
class TestLabWorkflow(LabCoreCommon):

    def test_sequences(self):
        self.assertTrue(self.alice.ref.startswith('PAT-'))
        self.assertTrue(self._new_request('panel_bil1').name.startswith('DEM/'))

    def test_assign_missing_sequences(self):
        patient = self.Patient.create({'name': 'Ancien patient'})
        patient.ref = False
        req = self._new_request('panel_bil1')
        req.name = 'Nouvelle'
        self.Patient._assign_missing_refs()
        self.env['lab.request']._assign_missing_names()
        self.assertTrue(patient.ref.startswith('PAT-'))
        self.assertTrue(req.name.startswith('DEM/'))

    def test_create_loads_panels(self):
        req = self._new_request('panel_eal')
        self.assertEqual(len(req.result_ids), 4)

    def test_onchange_panels_fill_results(self):
        with Form(self.env['lab.request']) as form:
            form.patient_id = self.alice
            form.panel_ids.add(self.env.ref('lab_core.panel_eal'))
            self.assertEqual(len(form.result_ids), 4)

    def test_workflow(self):
        req = self._new_request('panel_bil1')
        req.action_sample()
        self.assertEqual(req.state, 'sampled')
        self.assertEqual(len(req.sample_ids), 1)            # 3 analyses sanguines -> 1 tube
        self.assertTrue(req.sample_ids.barcode.startswith('TUB'))
        with self.assertRaises(UserError):
            req.action_analyse()                            # valeurs manquantes
        req.result_ids.value_text = '1'
        req.action_analyse()
        req.action_validate()
        self.assertEqual((req.state, req.validated_by_id), ('validated', self.env.user))

    def test_two_sample_types_two_tubes(self):
        req = self._new_request('panel_eal')
        req.result_ids = [Command.create({'analysis_id': self.env.ref('lab_core.analysis_uprot').id})]
        req.action_sample()
        self.assertEqual(sorted(req.sample_ids.mapped('sample_type')), ['blood', 'urine'])

    def test_state_validated_write_refused(self):
        with self.assertRaises(UserError):
            self._new_request('panel_bil1').write({'state': 'validated'})

    def _validated(self):
        req = self._new_request('panel_bil1')
        req.action_sample()
        req.result_ids.value_text = '1'
        req.action_analyse()
        req.action_validate()
        return req

    def test_validated_results_locked(self):
        with self.assertRaises(UserError):
            self._validated().result_ids[:1].value_text = '9'

    def test_reset_draft_keeps_validated(self):
        req = self._validated()
        req.action_reset_draft()
        self.assertEqual(req.state, 'validated')

    def test_cancel(self):
        req = self._new_request('panel_bil1')
        req.action_sample()
        req.action_cancel()
        self.assertEqual(req.state, 'cancelled')
        self._validated().action_cancel()
        self.assertEqual(self._validated().state, 'validated')

    def test_prescriber_removed_warning(self):
        doctor = self.env['res.partner'].create({'name': 'Dr Test'})
        req = self.env['lab.request'].create({'patient_id': self.alice.id, 'prescriber_id': doctor.id})
        draft = req.new({'patient_id': self.alice.id, 'prescriber_id': False}, origin=req)
        self.assertEqual(draft._onchange_prescriber_id()['warning']['title'], 'Prescripteur retiré')
        self.assertFalse(req._onchange_prescriber_id())
