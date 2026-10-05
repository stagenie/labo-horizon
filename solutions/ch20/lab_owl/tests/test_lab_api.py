import json
from datetime import date, timedelta

from odoo import fields
from odoo.tests import HttpCase, new_test_user

STATUS_NO_KEY = 401          # pas de clé, ou clé inconnue
STATUS_USER_ERROR = 422      # UserError levée par la méthode
STATUS_ACCESS_ERROR = 403    # droits insuffisants


class TestLabApi(HttpCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env.user.group_ids |= cls.env.ref('lab_core.group_lab_biologist')
        cls.automate = new_test_user(cls.env, 'automate', groups='lab_core.group_lab_technician', name='Automate CHIM-1')
        cls.key = cls._key_for(cls.automate)
        patient = cls.env['lab.patient'].create({'name': 'Yanis Roux', 'birthdate': date(1970, 3, 3), 'gender': 'male'})
        cls.req = cls.env['lab.request'].create({
            'patient_id': patient.id,
            'panel_ids': [(6, 0, cls.env.ref('lab_core.panel_eal').ids)],
        })
        cls.req.action_sample()

    @classmethod
    def _key_for(cls, user):
        return cls.env['res.users.apikeys'].with_user(user)._generate(
            'rpc', 'Automate', fields.Datetime.now() + timedelta(days=1))

    def _call(self, payload, key=None):
        headers = {'Content-Type': 'application/json'}
        if key is not False:
            headers['Authorization'] = f'Bearer {key or self.key}'
        return self.url_open('/json/2/lab.request/api_push_results', data=json.dumps(payload), headers=headers)

    def _values(self, high_code=None):
        """Une valeur au milieu de l'intervalle pour chaque analyse, le double du maximum pour `high_code`."""
        values = {}
        for result in self.req.result_ids:
            low, high = result.range_min, result.range_max
            mid = (low + high) / 2 if high > low else (low * 1.5 or 1.0)   # borne unique : au-dessus du minimum
            values[result.analysis_code] = f"{result.range_max * 2 if result.analysis_code == high_code else mid:.2f}"
        return values

    def test_api_push_results(self):
        res = self._call({'request_ref': self.req.name, 'results': self._values(high_code='CHOL')})
        self.assertEqual(res.status_code, 200, res.text)
        self.assertEqual(res.json(), {'request': self.req.name, 'state': 'analysed', 'abnormal': 1})
        self.assertEqual(self.req.state, 'analysed')

    def test_api_partial_keeps_sampled(self):
        res = self._call({'request_ref': self.req.name, 'results': {'CHOL': '1.5'}})
        self.assertEqual(res.status_code, 200, res.text)
        self.assertEqual(res.json()['state'], 'sampled')

    def test_api_logs_note_on_request(self):
        self._call({'request_ref': self.req.name, 'results': {'CHOL': '1.5', 'TG': '1'}})
        note = self.req.message_ids.filtered(lambda m: "automate" in (m.body or ''))[:1]
        self.assertIn('CHOL, TG', note.body)
        self.assertEqual(note.author_id, self.automate.partner_id)

    def test_api_unknown_request(self):
        res = self._call({'request_ref': 'DEM/0000/99999', 'results': {'CHOL': '2'}})
        self.assertEqual(res.status_code, STATUS_USER_ERROR)
        self.assertIn('introuvable', res.json()['message'])

    def test_api_unknown_analysis_writes_nothing(self):
        res = self._call({'request_ref': self.req.name, 'results': {'CHOL': '2', 'XXX': '1'}})
        self.assertEqual(res.status_code, STATUS_USER_ERROR)
        self.assertIn('XXX', res.json()['message'])
        self.assertFalse(self.req.result_ids.filtered('value_text'))

    def test_api_refuses_null_value(self):
        res = self._call({'request_ref': self.req.name, 'results': {'CHOL': None}})
        self.assertEqual(res.status_code, STATUS_USER_ERROR)
        self.assertIn('CHOL', res.json()['message'])
        self.assertFalse(self.req.result_ids.filtered('value_text'))

    def test_api_blank_value_keeps_result(self):
        self.req.result_ids.value_text = '1'
        self.req.action_analyse()
        res = self._call({'request_ref': self.req.name, 'results': {'CHOL': '  '}})
        self.assertEqual(res.status_code, STATUS_USER_ERROR)
        self.assertEqual(set(self.req.result_ids.mapped('value_text')), {'1'})

    def test_api_empty_results(self):
        res = self._call({'request_ref': self.req.name, 'results': {}})
        self.assertEqual(res.status_code, STATUS_USER_ERROR)

    def test_api_refuses_draft_request(self):
        draft = self.req.copy()
        res = self._call({'request_ref': draft.name, 'results': {'CHOL': '2'}})
        self.assertEqual(res.status_code, STATUS_USER_ERROR)
        self.assertIn('prélevée', res.json()['message'])

    def test_api_refuses_validated_request(self):
        self.req.result_ids.value_text = '1'
        self.req.action_analyse()
        self.req.action_validate()
        res = self._call({'request_ref': self.req.name, 'results': {'CHOL': '3,1'}})
        self.assertEqual(res.status_code, STATUS_USER_ERROR)
        self.assertEqual(set(self.req.result_ids.mapped('value_text')), {'1'})

    def test_api_without_key(self):
        res = self._call({'request_ref': self.req.name, 'results': {'CHOL': '2'}}, key=False)
        self.assertEqual(res.status_code, STATUS_NO_KEY)
        self.assertFalse(self.req.result_ids.filtered('value_text'))

    def test_api_bad_key(self):
        res = self._call({'request_ref': self.req.name, 'results': {'CHOL': '2'}}, key='pas-une-cle')
        self.assertEqual(res.status_code, STATUS_NO_KEY)

    def test_api_requires_lab_rights(self):
        outsider = new_test_user(self.env, 'outsider', groups='base.group_user')
        res = self._call({'request_ref': self.req.name, 'results': {'CHOL': '2'}}, key=self._key_for(outsider))
        self.assertEqual(res.status_code, STATUS_ACCESS_ERROR)
        self.assertFalse(self.req.result_ids.filtered('value_text'))

    def test_api_error_hides_traceback(self):
        res = self._call({'request_ref': 'DEM/0000/99999', 'results': {'CHOL': '2'}})
        debug = res.json()['debug']
        self.assertNotIn('Traceback', debug)
        self.assertNotIn('File "', debug)

    # --- Exercice 20.2 -------------------------------------------------------------------------------------------

    def _pending(self, request_ref):
        return self.url_open('/json/2/lab.request/api_pending_analyses', data=json.dumps({'request_ref': request_ref}),
                             headers={'Content-Type': 'application/json', 'Authorization': f'Bearer {self.key}'})

    def test_api_pending_analyses(self):
        self._call({'request_ref': self.req.name, 'results': {'CHOL': '1.5'}})
        res = self._pending(self.req.name)
        self.assertEqual(res.status_code, 200, res.text)
        self.assertEqual(res.json(), ['HDL', 'LDL', 'TG'])

    def test_api_pending_unknown_request(self):
        res = self._pending('DEM/0000/99999')
        self.assertEqual(res.status_code, STATUS_USER_ERROR)
        self.assertIn('introuvable', res.json()['message'])
