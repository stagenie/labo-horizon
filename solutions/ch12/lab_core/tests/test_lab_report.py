from odoo.tests import new_test_user, tagged
from odoo.tools.safe_eval import safe_eval, time   # comme le contrôleur de téléchargement

from .common import LabCoreCommon


@tagged('post_install', '-at_install')
class TestLabReport(LabCoreCommon):

    def test_report_shows_flags(self):
        req = self._new_request('panel_bil1')
        for result in req.result_ids:
            result.value_text = {'GLY': '1,40', 'HB': '13', 'CRP': '2'}[result.analysis_code]
        html, _fmt = self.env['ir.actions.report']._render_qweb_html(
            'lab_core.action_report_lab_request', req.ids)
        html = html.decode()
        self.assertIn('Alice Martin', html)
        self.assertIn('Glycémie à jeun', html)
        self.assertIn('lab-flag-high', html)          # la ligne hors norme porte la classe
        self.assertEqual(html.count('lab-flag-high'), 1)

    def test_label_has_barcode(self):
        req = self._new_request('panel_eal')
        req.action_sample()
        html, _fmt = self.env['ir.actions.report']._render_qweb_html(
            'lab_core.action_report_lab_sample_label', req.sample_ids.ids)
        self.assertIn('/report/barcode/Code128/' + req.sample_ids.barcode, html.decode())

    def test_ranges_follow_language(self):
        if not self.env['res.lang']._lang_get('fr_FR'):
            self.skipTest("fr_FR non installée (check_tag.py charge fr_FR)")
        req = self._new_request('panel_bil1')
        html, _fmt = self.env['ir.actions.report'].with_context(lang='fr_FR')._render_qweb_html(
            'lab_core.action_report_lab_request', req.ids)
        self.assertIn('0,70', html.decode())

    def test_unvalidated_report_warns(self):
        req = self._new_request('panel_bil1')
        html, _fmt = self.env['ir.actions.report']._render_qweb_html('lab_core.action_report_lab_request', req.ids)
        self.assertIn('Document non validé', html.decode())

    def test_report_reserved_to_technical_staff(self):
        # la secrétaire ne lit pas les résultats (chapitre 10) : son compte rendu aurait un tableau vide
        report = self.env.ref('lab_core.action_report_lab_request')
        secretary = new_test_user(self.env, 'lab_sec_report', groups='lab_core.group_lab_secretary')
        technician = new_test_user(self.env, 'lab_tech_report', groups='lab_core.group_lab_technician')
        for user, expected in ((secretary, False), (technician, True)):
            bindings = self.env['ir.actions.actions'].with_user(user).get_bindings('lab.request')
            self.assertEqual(report.id in [a['id'] for a in bindings.get('report', [])], expected)
            arch = self.env['lab.request'].with_user(user).get_views([(False, 'form')])['views']['form']['arch']
            self.assertEqual('Imprimer le compte rendu' in arch, expected)

    def test_label_shows_age_and_gender(self):
        req = self._new_request('panel_eal')
        req.action_sample()
        html, _fmt = self.env['ir.actions.report'].with_context(lang='fr_FR')._render_qweb_html(
            'lab_core.action_report_lab_sample_label', req.sample_ids.ids)
        html = html.decode()
        self.assertIn('%s ans' % self.alice.age, html)
        self.assertIn('Femme', html)

    def test_report_file_name(self):
        req = self._new_request('panel_bil1')
        report = self.env.ref('lab_core.action_report_lab_request')
        name = safe_eval(report.print_report_name, {'object': req, 'time': time})
        self.assertTrue(req.patient_id.ref)
        self.assertEqual(name, 'CR-%s-%s' % (req.patient_id.ref, req.name))
