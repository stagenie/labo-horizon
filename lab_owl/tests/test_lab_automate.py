import json
import os
import subprocess
import sys
from datetime import date, timedelta
from pathlib import Path

from odoo import fields
from odoo.tests import HttpCase, new_test_user

SCRIPT = Path(__file__).resolve().parents[2] / 'scripts' / 'automate.py'


class TestLabAutomateScript(HttpCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        automate = new_test_user(cls.env, 'automate', groups='lab_core.group_lab_technician')
        cls.key = cls.env['res.users.apikeys'].with_user(automate)._generate(
            'rpc', 'Automate', fields.Datetime.now() + timedelta(days=1))
        patient = cls.env['lab.patient'].create({'name': 'Lina Morel', 'birthdate': date(1985, 6, 1), 'gender': 'female'})
        cls.req = cls.env['lab.request'].create({
            'patient_id': patient.id,
            'panel_ids': [(6, 0, cls.env.ref('lab_core.panel_eal').ids)],
        })
        cls.req.action_sample()

    def setUp(self):
        super().setUp()
        if not SCRIPT.is_file():
            self.skipTest(f"{SCRIPT} absent : le module est installé hors du dépôt Labo Horizon")

    def _run(self, *results, key=True):
        env = dict(os.environ, LAB_API_KEY=self.key) if key else {k: v for k, v in os.environ.items() if k != 'LAB_API_KEY'}
        cmd = [sys.executable, str(SCRIPT), '--url', self.base_url(), '--db', self.env.cr.dbname,
               '--request', self.req.name, *[arg for r in results for arg in ('--result', r)]]
        # le serveur de test refuse les requêtes sans son cookie ; le script ne l'a pas : on les laisse passer
        with self.allow_requests(all_requests=True):
            return subprocess.run(cmd, capture_output=True, text=True, env=env, timeout=60)

    def test_script_pushes_results(self):
        proc = self._run('chol=1,5', 'TG=1')
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertEqual(json.loads(proc.stdout)['state'], 'sampled')
        self.assertEqual(self.req.result_ids.filtered(lambda r: r.analysis_code == 'CHOL').value_text, '1,5')

    def test_script_reports_refusal(self):
        proc = self._run('XXX=1')
        self.assertEqual(proc.returncode, 1)
        self.assertIn('XXX', proc.stderr)

    def test_script_requires_key(self):
        proc = self._run('CHOL=1', key=False)
        self.assertEqual(proc.returncode, 2)
        self.assertIn('LAB_API_KEY', proc.stderr)
