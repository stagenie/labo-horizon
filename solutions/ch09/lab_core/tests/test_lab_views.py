from odoo.tests import tagged

from .common import LabCoreCommon


@tagged('post_install', '-at_install')
class TestLabViews(LabCoreCommon):

    def test_views_load(self):
        for model, types in (('lab.request', ['kanban', 'list', 'form', 'search', 'calendar']),
                             ('lab.result', ['pivot', 'graph']),
                             ('lab.patient', ['list', 'form', 'search'])):
            views = self.env[model].get_views([(False, t) for t in types])
            self.assertEqual(set(views['views']), set(types))

    def test_abnormal_stats(self):
        req = self._new_request('panel_bil1')
        for result in req.result_ids:
            result.value_text = {'GLY': '1,40', 'HB': '9', 'CRP': '2'}[result.analysis_code]
        groups = self.env['lab.result']._read_group(
            [('request_id', '=', req.id), ('flag', 'in', ('low', 'high'))], ['analysis_id'], ['__count'])
        self.assertEqual(sorted(a.code for a, _count in groups), ['GLY', 'HB'])

    def test_kanban_cards_not_draggable(self):
        # glisser une carte écrirait l'état sans passer par les boutons (section 7.7)
        arch = self.env['lab.request'].get_views([(False, 'kanban')])['views']['kanban']['arch']
        self.assertIn('records_draggable="0"', arch)

    def test_quick_create_in_column_starts_draft(self):
        # la création rapide du kanban passe l'état de la colonne en valeur par défaut
        req = self.env['lab.request'].with_context(default_state='sampled').create({'patient_id': self.alice.id})
        self.assertEqual(req.state, 'draft')

    def test_my_validations_filter(self):
        req = self._new_request('panel_bil1')
        req.action_sample()
        req.result_ids.value_text = '1'
        req.action_analyse()
        mine = self.env['lab.request'].search([('activity_user_id', '=', self.env.uid)])
        self.assertIn(req, mine)

    def test_weekly_graph(self):
        views = self.env['lab.request'].get_views([(False, 'graph')])
        self.assertIn('interval="week"', views['views']['graph']['arch'])
