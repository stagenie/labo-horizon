from psycopg2 import IntegrityError

from odoo.exceptions import ValidationError
from odoo.tests import new_test_user
from odoo.tools import mute_logger

from odoo.addons.lab_core.tests.common import LabCoreCommon


class TestLabExtension(LabCoreCommon):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.insurer = cls.env['lab.insurer'].create({'name': 'Mutuelle Test', 'coverage_rate': 70.0})

    def test_insurer_is_a_contact(self):
        partner = self.insurer.partner_id
        self.assertEqual(partner.name, 'Mutuelle Test')
        self.insurer.name = 'Mutuelle Test Santé'          # champ du contact, écrit à travers la mutuelle
        self.assertEqual(partner.name, 'Mutuelle Test Santé')

    def test_coverage_rate_bounds(self):
        with self.assertRaises(ValidationError):
            self.insurer.coverage_rate = 120.0

    def test_unlink_insurer_keeps_contact(self):
        partner = self.insurer.partner_id
        self.insurer.unlink()
        self.assertTrue(partner.exists())

    def test_patient_partner_created_once(self):
        self.assertFalse(self.alice.partner_id)
        partner = self.alice._get_or_create_partner()
        self.assertEqual((partner.name, partner.email, partner.phone),
                         ('Alice Martin', 'alice@example.com', '+33600000001'))
        self.assertEqual(self.alice._get_or_create_partner(), partner)

    def test_product_follows_analysis(self):
        chol = self.env.ref('lab_core.analysis_chol')
        product = chol.product_id
        self.assertEqual((product.type, product.default_code, product.lst_price), ('service', 'CHOL', 2.70))
        self.assertFalse(product.taxes_id)
        chol.price = 3.10
        self.assertEqual(chol.product_id, product)
        self.assertEqual(product.lst_price, 3.10)

    def test_existing_analyses_have_products(self):
        ids = self.env['ir.model.data'].search([('module', '=', 'lab_core'), ('model', '=', 'lab.analysis')]).mapped('res_id')
        analyses = self.env['lab.analysis'].browse(ids)
        self.assertEqual(len(analyses), 30)
        self.assertFalse(analyses.filtered(lambda a: not a.price or not a.product_id).mapped('code'))

    def test_biologist_creates_insurer(self):
        biologist = new_test_user(self.env, login='bio_insurer', groups='lab_core.group_lab_biologist')
        insurer = self.env['lab.insurer'].with_user(biologist).create({'name': 'Mutuelle du Biologiste'})
        self.assertEqual(insurer.partner_id.name, 'Mutuelle du Biologiste')

    def test_biologist_creates_analysis(self):
        biologist = new_test_user(self.env, login='bio_analysis', groups='lab_core.group_lab_biologist')
        analysis = self.env['lab.analysis'].with_user(biologist).create({'code': 'TEST', 'name': 'Analyse test', 'price': 4.0})
        self.assertEqual(analysis.product_id.lst_price, 4.0)

    def test_partner_reused_by_email(self):
        existing = self.env['res.partner'].create({'name': 'A. Martin', 'email': 'ALICE@example.com'})
        self.assertEqual(self.alice._get_or_create_partner(), existing)

    def test_insurer_code_unique(self):
        self.insurer.code = '75000001'
        with mute_logger('odoo.sql_db'), self.assertRaises(IntegrityError):
            self.env['lab.insurer'].create({'name': 'Doublon', 'code': '75000001'})
            self.env.flush_all()
