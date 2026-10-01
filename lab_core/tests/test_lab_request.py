from psycopg2 import IntegrityError

from odoo.tests import tagged
from odoo.tools import mute_logger

from .common import LabCoreCommon


@tagged('post_install', '-at_install')
class TestLabRequest(LabCoreCommon):

    def test_request_links_patient_and_prescriber(self):
        doctor = self.env['res.partner'].create({'name': 'Dr Test'})
        req = self.env['lab.request'].create({'patient_id': self.alice.id, 'prescriber_id': doctor.id})
        self.assertEqual(req.patient_id.name, 'Alice Martin')
        self.assertEqual(req.name, 'Nouvelle')
        self.assertTrue(req.date_request)

    def test_patient_with_request_cannot_be_deleted(self):
        self.env['lab.request'].create({'patient_id': self.alice.id})
        with mute_logger('odoo.sql_db'), self.assertRaises(IntegrityError):
            self.alice.unlink()
            self.env.flush_all()
