import ast

from lxml import etree

from odoo.tests import new_test_user

from odoo.addons.lab_core.tests.common import LabCoreCommon


class TestLabBillingViews(LabCoreCommon):

    def _arch(self, model, view_type='form', user=None):
        env = self.env(user=user) if user else self.env
        return etree.fromstring(env[model].get_views([(False, view_type)])['views'][view_type]['arch'])

    def _field_names(self, arch):
        return [f.get('name') for f in arch.iter('field')]

    def test_patient_form_shows_insurer_after_email(self):
        names = self._field_names(self._arch('lab.patient'))
        self.assertEqual(names[names.index('email') + 1:names.index('email') + 3], ['insurer_id', 'partner_id'])

    def test_analysis_list_shows_price_after_unit(self):
        names = self._field_names(self._arch('lab.analysis', 'list'))
        self.assertEqual(names[names.index('unit') + 1], 'price')

    def test_contact_lab_page_for_lab_staff(self):
        secretary = new_test_user(self.env, login='sec_view', groups='lab_core.group_lab_secretary')
        self.assertTrue(self._arch('res.partner', user=secretary).xpath("//page[@name='lab']"))

    def test_contact_lab_page_is_read_only(self):
        page = self._arch('res.partner').xpath("//page[@name='lab']")[0]
        self.assertEqual([f.get('readonly') for f in page.xpath("./field")], ['1', '1'])

    def test_contact_lab_page_hidden_from_others(self):
        clerk = new_test_user(self.env, login='clerk_view', groups='base.group_user')
        self.assertFalse(self._arch('res.partner', user=clerk).xpath("//page[@name='lab']"))

    def test_partner_lists_its_patient_files(self):
        partner = self.alice._get_or_create_partner()
        self.assertEqual(partner.lab_patient_ids, self.alice)

    def test_insurer_contact_lists_its_insurer(self):
        insurer = self.env['lab.insurer'].create({'name': 'Mutuelle Vue', 'coverage_rate': 55.0})
        self.assertEqual(insurer.partner_id.lab_insurer_ids, insurer)

    def test_prescriber_choices_exclude_insurers(self):
        self.env['lab.insurer'].create({'name': 'Mutuelle Prescription'})
        field = self._arch('lab.request').xpath("//field[@name='prescriber_id']")[0]
        domain = ast.literal_eval(field.get('domain') or '[]')
        self.assertFalse(self.env['res.partner'].name_search('Mutuelle Prescription', domain=domain))

    def test_patient_list_has_insurer_column(self):
        names = self._field_names(self._arch('lab.patient', 'list'))
        self.assertEqual(names[names.index('email') + 1], 'insurer_id')

    def test_search_has_no_insurer_filter(self):
        self.assertTrue(self._arch('lab.patient', 'search').xpath("//filter[@name='no_insurer']"))

    def test_partner_request_count(self):
        partner = self.alice._get_or_create_partner()
        self.env['lab.request'].create({'patient_id': self.alice.id})
        self.assertEqual(partner.lab_request_count, 1)
        self.assertEqual(self.env['lab.request'].search(partner.action_view_lab_requests()['domain']).patient_id, self.alice)
