from odoo.tests import tagged

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
