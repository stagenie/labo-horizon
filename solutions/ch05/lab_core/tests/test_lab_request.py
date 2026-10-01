from psycopg2 import IntegrityError

from odoo.fields import Command
from odoo.tests import tagged
from odoo.tools import mute_logger

from .common import LabCoreCommon


@tagged('post_install', '-at_install')
class TestLabRequest(LabCoreCommon):

    def test_request_links_patient_and_prescriber(self):
        doctor = self.env['res.partner'].create({'name': 'Dr Test'})
        req = self.env['lab.request'].create({'patient_id': self.alice.id, 'prescriber_id': doctor.id})
        self.assertEqual(req.patient_id.name, 'Alice Martin')
        self.assertEqual(req.name, 'Nouvelle')
        self.assertTrue(req.date_request)

    def test_patient_with_request_cannot_be_deleted(self):
        self.env['lab.request'].create({'patient_id': self.alice.id})
        with mute_logger('odoo.sql_db'), self.assertRaises(IntegrityError):
            self.alice.unlink()
            self.env.flush_all()

    def _request_with(self, codes):
        return self.env['lab.request'].create({
            'patient_id': self.alice.id,
            'result_ids': [Command.create({'analysis_id': self.env.ref(f'lab_core.analysis_{c}').id}) for c in codes],
        })

    def test_sample_types_unique_sorted(self):
        self.assertEqual(self._request_with(['gly', 'uprot', 'hb'])._get_sample_types(), ['blood', 'urine'])

    def test_sample_types_across_requests(self):
        both = self._request_with(['gly']) | self._request_with(['ecbu'])
        self.assertEqual(both._get_sample_types(), ['blood', 'urine'])

    def test_pending_results(self):
        req = self._request_with(['gly', 'hb'])
        req.result_ids.filtered(lambda r: r.analysis_code == 'GLY').value_text = '0,95'
        self.assertEqual(req._get_pending_results().analysis_code, 'HB')

    def test_results_sorted_by_code(self):
        req = self._request_with(['tsh', 'crp', 'gly'])
        self.assertEqual(req._get_results_by_code().mapped('analysis_code'), ['CRP', 'GLY', 'TSH'])

    def test_delete_request_deletes_results(self):
        req = self._request_with(['gly'])
        results = req.result_ids
        req.unlink()
        self.assertFalse(results.exists())

    def test_patient_sees_its_requests(self):
        req = self._request_with(['gly'])
        self.assertIn(req, self.alice.request_ids)

    def test_sync_adds_each_analysis_once(self):
        req = self._new_request('panel_bil1', 'panel_nfs')
        self.assertEqual(sorted(req.result_ids.mapped('analysis_code')), ['CRP', 'GB', 'GLY', 'HB', 'PLQ', 'VGM'])

    def test_sync_is_idempotent(self):
        req = self._new_request('panel_eal')
        req._sync_results_from_panels()
        self.assertEqual(len(req.result_ids), 4)

    def test_sync_keeps_existing_values(self):
        req = self._new_request('panel_bil1')
        req.result_ids.filtered(lambda r: r.analysis_code == 'GLY').value_text = '1,02'
        req.panel_ids = [Command.link(self.env.ref('lab_core.panel_eal').id)]
        req._sync_results_from_panels()
        self.assertEqual(len(req.result_ids), 7)
        self.assertEqual(req.result_ids.filtered(lambda r: r.analysis_code == 'GLY').value_text, '1,02')

    def test_clear_empty_results(self):
        req = self._new_request('panel_bil1')
        req.result_ids.filtered(lambda r: r.analysis_code == 'GLY').value_text = '1,02'
        req.action_clear_empty_results()
        self.assertEqual(req.result_ids.mapped('analysis_code'), ['GLY'])

    def test_thyroid_panel(self):
        self.assertEqual(self.env.ref('lab_core.panel_thy').analysis_ids.mapped('code'), ['TSH'])
