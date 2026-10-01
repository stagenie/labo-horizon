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
