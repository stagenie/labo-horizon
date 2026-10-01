from datetime import timedelta

from odoo.tests import new_test_user, tagged

from .common import LabCoreCommon


@tagged('post_install', '-at_install')
class TestLabWizard(LabCoreCommon):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.technician = new_test_user(cls.env, 'lab_tech', groups='lab_core.group_lab_technician')

    def test_entry_wizard_fills_and_analyses(self):
        req = self._new_request('panel_eal')
        req.action_sample()
        action = req.with_user(self.technician).action_open_result_entry()
        wizard = self.env['lab.result.entry'].with_user(self.technician).browse(action['res_id'])
        self.assertEqual(len(wizard.line_ids), 4)
        for line in wizard.line_ids:
            line.value_text = '2,5'
        wizard.action_apply()
        self.assertEqual(req.state, 'analysed')
        self.assertEqual(set(req.result_ids.mapped('flag')), {'high'})

    def test_server_action_validates_selection(self):
        reqs = self._new_request('panel_bil1') | self._new_request('panel_bil1')
        for req in reqs:
            req.action_sample()
            req.result_ids.value_text = '1'
            req.action_analyse()
        action = self.env.ref('lab_core.action_server_lab_request_validate')
        action.with_context(active_model='lab.request', active_ids=reqs.ids).run()
        self.assertEqual(set(reqs.mapped('state')), {'validated'})

    def test_wizard_is_transient(self):
        self.assertTrue(self.env['lab.result.entry']._transient)

    def test_old_wizard_is_vacuumed(self):
        req = self._new_request('panel_bil1')
        req.action_sample()
        Entry = self.env['lab.result.entry']
        entry = Entry.browse(req.action_open_result_entry()['res_id'])
        self.env.flush_all()
        self.env.cr.execute("UPDATE lab_result_entry SET write_date = %s WHERE id = %s",
                            [self.env.cr.now() - timedelta(hours=2), entry.id])
        Entry._transient_max_count   # la tâche planifiée lit les attributs dans cet ordre
        Entry._transient_vacuum()
        self.assertFalse(Entry.search([('id', '=', entry.id)]))
