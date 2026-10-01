from odoo.tests import tagged

from .common import LabCoreCommon


@tagged('post_install', '-at_install')
class TestLabChatter(LabCoreCommon):

    def _flush_tracking(self):
        self.env.flush_all()
        self.env.cr.precommit.run()

    def test_state_change_is_tracked(self):
        req = self._new_request('panel_bil1')
        self._flush_tracking()      # fin de la « transaction » de création
        req.action_sample()
        self._flush_tracking()
        tracking = req.message_ids.filtered(lambda m: m.message_type == 'tracking')
        self.assertIn('Prélevée', tracking.body)
        self.assertIn('(État)', tracking.body)

    def test_analyse_schedules_validation(self):
        req = self._new_request('panel_bil1')
        req.action_sample()
        req.result_ids.value_text = '1'
        req.action_analyse()
        self.assertEqual(req.activity_ids.summary, 'Validation biologique')

    def test_validate_closes_activity(self):
        req = self._new_request('panel_bil1')
        req.action_sample()
        req.result_ids.value_text = '1'
        req.action_analyse()
        req.action_validate()
        self.assertFalse(req.activity_ids)
