from datetime import date

from odoo.fields import Command
from odoo.tests import tagged

from odoo.addons.account.tests.common import AccountTestInvoicingCommon


@tagged('post_install', '-at_install')
class TestLabInvoiceLabel(AccountTestInvoicingCommon):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env.user.group_ids |= cls.env.ref('lab_core.group_lab_biologist')
        for xmlid in ('lab_core.seq_lab_patient', 'lab_core.seq_lab_request'):
            cls.env.ref(xmlid).company_id = False
        cls.env.ref('lab_core.panel_eal').analysis_ids.write({'price': 10.0})

    def _insurer_line_label(self, rate):
        insurer = self.env['lab.insurer'].create({'name': f'Mutuelle {rate}', 'coverage_rate': rate})
        patient = self.env['lab.patient'].create({
            'name': 'Léa Martin', 'birthdate': date(1990, 1, 1), 'gender': 'female', 'insurer_id': insurer.id,
        })
        request = self.env['lab.request'].create({
            'patient_id': patient.id,
            'panel_ids': [Command.set(self.env.ref('lab_core.panel_eal').ids)],
        })
        request._sync_results_from_panels()
        request.action_sample()
        request.result_ids.value_text = '1'
        request.action_analyse()
        request.action_validate()
        moves = request.with_context(lang='fr_FR')._create_invoices()
        return moves.filtered(lambda m: m.partner_id == insurer.partner_id).invoice_line_ids[:1].name

    def test_insurer_line_label_integer_rate(self):
        self.assertIn('(part mutuelle, 70 %)', self._insurer_line_label(70.0))

    def test_insurer_line_label_decimal_rate(self):
        self.assertIn('(part mutuelle, 65,5 %)', self._insurer_line_label(65.5))
