from odoo.fields import Command
from odoo.tests import TransactionCase


class LabCoreCommon(TransactionCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.Patient = cls.env['lab.patient']
        cls.alice = cls.Patient.create({
            'name': 'Alice Martin',
            'birthdate': '1992-03-14',
            'phone': '+33600000001',
            'gender': 'female',
            'email': 'alice@example.com',
        })

    def _new_request(self, *panels):
        req = self.env['lab.request'].create({
            'patient_id': self.alice.id,
            'panel_ids': [Command.set([self.env.ref(f'lab_core.{p}').id for p in panels])],
        })
        req._sync_results_from_panels()
        return req
