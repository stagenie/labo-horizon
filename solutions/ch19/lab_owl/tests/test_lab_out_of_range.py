from odoo.tests import TransactionCase
from odoo.tools.safe_eval import safe_eval


class TestLabOutOfRange(TransactionCase):

    def test_out_of_range_action_domain(self):
        action = self.env.ref('lab_owl.lab_result_out_of_range_action')
        shown = self.env['lab.result'].search(safe_eval(action.domain))
        self.assertTrue(shown, "la démo compte au moins un résultat hors norme")
        self.assertLessEqual(set(shown.mapped('flag')), {'low', 'high'})

    def test_out_of_range_list_uses_gauge(self):
        view = self.env.ref('lab_owl.lab_result_view_list_out_of_range')
        arch = self.env['lab.result'].get_views([(view.id, 'list')])['views']['list']['arch']
        self.assertIn('widget="lab_gauge"', arch)
