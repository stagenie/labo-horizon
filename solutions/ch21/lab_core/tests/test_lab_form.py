from datetime import date

from odoo.tests import Form, TransactionCase


class TestLabForm(TransactionCase):

    def test_form_panel_creates_result_lines(self):
        patient = self.env['lab.patient'].create({'name': 'Hugo Lambert', 'birthdate': date(1980, 5, 5), 'gender': 'male'})
        eal = self.env.ref('lab_core.panel_eal')
        form = Form(self.env['lab.request'])
        form.patient_id = patient
        form.panel_ids.add(eal)
        # l'onchange a déjà créé les lignes, avant tout enregistrement
        self.assertEqual(len(form.result_ids), 4)
        self.assertFalse(self.env['lab.request'].search([('patient_id', '=', patient.id)]))
        request = form.save()
        self.assertEqual(sorted(request.result_ids.mapped('analysis_code')), ['CHOL', 'HDL', 'LDL', 'TG'])
