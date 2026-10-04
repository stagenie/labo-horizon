from datetime import date

from lxml import etree

from odoo.exceptions import UserError
from odoo.fields import Command
from odoo.tests import new_test_user, tagged

from odoo.addons.account.tests.common import AccountTestInvoicingCommon


@tagged('post_install', '-at_install')
class TestLabInvoicing(AccountTestInvoicingCommon):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # AccountTestInvoicingCommon travaille sous un utilisateur comptable : lui donner le laboratoire.
        cls.env.user.group_ids |= cls.env.ref('lab_core.group_lab_biologist')
        # Elle crée aussi sa propre société : les séquences de lab_core, rattachées à la société principale,
        # deviennent communes à toutes les sociétés le temps du test.
        for xmlid in ('lab_core.seq_lab_patient', 'lab_core.seq_lab_request'):
            cls.env.ref(xmlid).company_id = False
        cls.insurer = cls.env['lab.insurer'].create({'name': 'Mutuelle Horizon', 'coverage_rate': 70.0})
        cls.patient = cls.env['lab.patient'].create({
            'name': 'Nora Petit', 'birthdate': date(1992, 2, 2), 'gender': 'female',
            'phone': '+33600000021', 'email': 'nora@example.com', 'insurer_id': cls.insurer.id,
        })
        cls.eal = cls.env.ref('lab_core.panel_eal')
        cls.eal.analysis_ids.write({'price': 10.0})

    def _validated_request(self, patient=None):
        request = self.env['lab.request'].create({
            'patient_id': (patient or self.patient).id,
            'panel_ids': [Command.set(self.eal.ids)],
        })
        request._sync_results_from_panels()
        request.action_sample()
        request.result_ids.value_text = '1'
        request.action_analyse()
        request.action_validate()
        return request

    def test_no_invoice_before_validation(self):
        request = self.env['lab.request'].create({'patient_id': self.patient.id})
        with self.assertRaises(UserError):
            request._create_invoices()

    def test_invoice_split_patient_insurer(self):
        request = self._validated_request()
        self.assertEqual(request.billing_state, 'to_invoice')
        moves = request._create_invoices()
        patient_move = moves.filtered(lambda m: m.partner_id == self.patient.partner_id)
        insurer_move = moves.filtered(lambda m: m.partner_id == self.insurer.partner_id)
        self.assertEqual(len(moves), 2)
        self.assertAlmostEqual(patient_move.amount_total, 12.0)   # 4 analyses × 10 € × 30 %
        self.assertAlmostEqual(insurer_move.amount_total, 28.0)   # 4 analyses × 10 € × 70 %
        self.assertEqual(request.invoice_ids, moves)
        self.assertEqual(moves.lab_request_ids, request)
        self.assertEqual(request.billing_state, 'invoiced')

    def test_split_sums_to_tariff(self):
        self.insurer.coverage_rate = 50.0
        self.eal.analysis_ids.write({'price': 1.25})   # 1,25 × 50 % = 0,625 : arrondir chaque part donnerait 0,63 + 0,63
        moves = self._validated_request()._create_invoices()
        self.assertAlmostEqual(sum(moves.mapped('amount_total')), 1.25 * len(self.eal.analysis_ids))

    def test_single_invoice_when_one_side_is_zero(self):
        self.insurer.coverage_rate = 100.0
        moves = self._validated_request()._create_invoices()
        self.assertEqual(moves.partner_id, self.insurer.partner_id)
        alone = self.env['lab.patient'].create({'name': 'Hugo Blanc', 'gender': 'male', 'email': 'hugo@example.com'})
        moves = self._validated_request(patient=alone)._create_invoices()
        self.assertEqual(moves.partner_id, alone.partner_id)

    def test_missing_price_blocks_invoice(self):
        request = self._validated_request()
        request.result_ids.analysis_id[:1].price = 0.0
        with self.assertRaisesRegex(UserError, 'tarif manquant'):
            request._create_invoices()

    def test_invoice_not_duplicated(self):
        request = self._validated_request()
        request._create_invoices()
        with self.assertRaises(UserError):
            request._create_invoices()

    def test_cancelled_invoices_allow_reinvoicing(self):
        request = self._validated_request()
        request._create_invoices().button_cancel()
        self.assertEqual(request.billing_state, 'to_invoice')
        self.assertEqual(len(request._create_invoices()), 2)

    def test_credit_note_allows_reinvoicing(self):
        request = self._validated_request()
        moves = request._create_invoices()
        moves.action_post()
        moves._reverse_moves(cancel=True)   # avoir total, lettré avec la facture
        self.assertEqual(set(moves.mapped('payment_state')), {'reversed'})
        self.assertEqual(request.billing_state, 'to_invoice')
        self.assertEqual(len(request._create_invoices()), 2)

    def test_confidential_patient_not_invoiced(self):
        self.patient.is_confidential = True
        request = self._validated_request()
        with self.assertRaisesRegex(UserError, 'confidentiel'):
            request._create_invoices()
        self.assertFalse(self.patient.partner_id)

    def test_billing_state_follows_payment(self):
        request = self._validated_request()
        moves = request._create_invoices()
        moves.action_post()
        self.assertEqual(request.billing_state, 'invoiced')
        for move in moves:
            self.env['account.payment.register'].with_context(
                active_model='account.move', active_ids=move.ids,
            ).create({})._create_payments()
        self.assertEqual(request.billing_state, 'paid')

    def test_secretary_invoices_all_analyses(self):
        request = self._validated_request()
        secretary = new_test_user(self.env, login='lab_sec_invoice', groups='lab_core.group_lab_secretary')
        moves = request.with_user(secretary)._create_invoices()
        self.assertEqual(len(moves.invoice_line_ids), 2 * len(self.eal.analysis_ids))

    def test_view_invoices_opens_customer_invoices(self):
        request = self._validated_request()
        request._create_invoices()
        action = request.action_view_invoices()
        self.assertEqual(action['id'], self.env.ref('account.action_move_out_invoice_type').id)
        self.assertEqual(action['domain'], [('id', 'in', request.invoice_ids.ids)])

    def test_invoice_form_has_lab_page(self):
        secretary = new_test_user(self.env, login='lab_sec_view', groups='lab_core.group_lab_secretary')
        views = self.env(user=secretary)['account.move'].get_views([(False, 'form')])
        self.assertTrue(etree.fromstring(views['views']['form']['arch']).xpath("//page[@name='lab']"))
