from odoo.tests import TransactionCase

GAUGE_FILES = ('lab_gauge_field.js', 'lab_gauge_field.xml', 'lab_gauge_field.scss')


class TestLabGauge(TransactionCase):

    def test_request_form_shows_gauge(self):
        arch = self.env['lab.request'].get_views([(False, 'form')])['views']['form']['arch']
        self.assertIn('widget="lab_gauge"', arch)

    def test_gauge_column_is_readonly(self):
        arch = self.env['lab.request'].get_views([(False, 'form')])['views']['form']['arch']
        self.assertRegex(arch, r'<field name="value"[^>]*widget="lab_gauge"[^>]*readonly="1"'
                               r'|<field name="value"[^>]*readonly="1"[^>]*widget="lab_gauge"')

    def test_gauge_assets_in_backend(self):
        paths = [p[0] for p in self.env['ir.asset']._get_asset_paths('web.assets_backend', {})]
        for name in GAUGE_FILES:
            self.assertTrue(any(p.endswith('lab_owl/static/src/gauge/' + name) for p in paths), name)
