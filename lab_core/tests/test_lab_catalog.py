from psycopg2 import IntegrityError

from odoo.exceptions import ValidationError
from odoo.tests import tagged
from odoo.tools import BinaryBytes, mute_logger

from .common import LabCoreCommon


@tagged('post_install', '-at_install')
class TestLabCatalog(LabCoreCommon):

    def test_catalog_data_loaded(self):
        self.assertEqual(self.env['lab.analysis'].search_count([]), 30)
        hb = self.env.ref('lab_core.analysis_hb')
        self.assertEqual((hb.unit, hb.ref_min_female, hb.ref_max), ('g/dL', 12.0, 17.0))
        self.assertEqual(self.env.ref('lab_core.analysis_uprot').sample_type, 'urine')

    def test_archived_analysis_hidden(self):
        tp = self.env.ref('lab_core.analysis_tp')
        tp.active = False
        Analysis = self.env['lab.analysis']
        self.assertNotIn(tp, Analysis.search([]))
        self.assertIn(tp, Analysis.with_context(active_test=False).search([]))

    def test_search_by_code(self):
        found = self.env['lab.analysis'].search([('display_name', 'ilike', 'GLY')])
        self.assertIn(self.env.ref('lab_core.analysis_gly'), found)

    def test_protocol_binary_is_raw_bytes(self):
        pdf = b'%PDF-1.4 fiche technique'
        gly = self.env.ref('lab_core.analysis_gly')
        gly.write({'protocol': BinaryBytes(pdf), 'protocol_filename': 'gly.pdf'})
        gly.invalidate_recordset(['protocol'])
        self.assertEqual(gly.protocol.content, pdf)

    def test_protocol_refuses_plain_bytes(self):
        gly = self.env.ref('lab_core.analysis_gly')
        with self.assertRaises(TypeError):
            gly.protocol = b'%PDF-1.4'

    def test_panels_data(self):
        self.assertEqual(set(self.env.ref('lab_core.panel_eal').analysis_ids.mapped('code')), {'CHOL', 'HDL', 'LDL', 'TG'})
        self.assertEqual(self.env['lab.panel'].search_count([]), 5)

    def test_range_by_gender(self):
        hb = self.env.ref('lab_core.analysis_hb')
        self.assertEqual(hb._get_range('male'), (13.0, 17.0))
        self.assertEqual(hb._get_range('female'), (12.0, 16.0))
        gly = self.env.ref('lab_core.analysis_gly')
        self.assertEqual(gly._get_range('female'), gly._get_range('male'))

    def test_min_above_max_refused(self):
        with self.assertRaises(ValidationError):
            self.env['lab.analysis'].create({'code': 'ZZZ', 'name': 'Test', 'ref_min': 5.0, 'ref_max': 1.0})

    def test_code_unique(self):
        with mute_logger('odoo.sql_db'), self.assertRaises(IntegrityError):
            self.env['lab.analysis'].create({'code': 'GLY', 'name': 'Doublon'})
            self.env.flush_all()

    def test_panel_count(self):
        self.assertEqual(self.env.ref('lab_core.panel_eal').analysis_count, 4)
