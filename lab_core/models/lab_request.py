from odoo import _, api, fields, models
from odoo.exceptions import UserError
from odoo.fields import Command

STATES = [
    ('draft', 'Brouillon'),
    ('sampled', 'Prélevée'),
    ('analysed', 'Analysée'),
    ('validated', 'Validée'),
]

# Pour chaque état d'arrivée, les états d'où une demande peut y venir.
STATE_FROM = {
    'draft': ('sampled', 'analysed'),
    'sampled': ('draft',),
    'analysed': ('sampled',),
    'validated': ('analysed',),
}


class LabRequest(models.Model):
    _name = 'lab.request'
    _description = "Demande d'analyses"
    _order = 'date_request desc, id desc'

    name = fields.Char('Numéro', required=True, readonly=True, copy=False, default='Nouvelle')
    patient_id = fields.Many2one('lab.patient', 'Patient', required=True, index=True, ondelete='restrict')
    prescriber_id = fields.Many2one('res.partner', 'Prescripteur', domain=[('is_company', '=', False)])
    date_request = fields.Datetime('Date', required=True, default=fields.Datetime.now)
    note = fields.Text('Renseignements cliniques')
    state = fields.Selection(STATES, 'État', default='draft', required=True, copy=False)
    validated_by_id = fields.Many2one('res.users', 'Validée par', readonly=True, copy=False)
    validated_date = fields.Datetime('Validée le', readonly=True, copy=False)
    result_ids = fields.One2many('lab.result', 'request_id', 'Résultats', copy=True)
    sample_ids = fields.One2many('lab.sample', 'request_id', 'Tubes', copy=False)
    panel_ids = fields.Many2many('lab.panel', string='Bilans')
    patient_gender = fields.Selection(related='patient_id.gender')
    abnormal_count = fields.Integer('Hors normes', compute='_compute_abnormal_count', store=True)

    @api.depends('result_ids.flag')
    def _compute_abnormal_count(self):
        for request in self:
            request.abnormal_count = len(request.result_ids.filtered(lambda r: r.flag in ('low', 'high')))

    def _get_sample_types(self):
        """ Types de prélèvement nécessaires aux demandes, sans doublon, triés. """
        return sorted(set(self.result_ids.analysis_id.mapped('sample_type')))

    def _get_pending_results(self):
        """ Résultats encore sans valeur. """
        return self.result_ids.filtered(lambda r: not (r.value_text or '').strip())

    def _get_results_by_code(self):
        return self.result_ids.sorted('analysis_code')

    def _sync_results_from_panels(self):
        """ Ajoute une ligne de résultat pour chaque analyse des bilans qui n'en a pas encore. """
        for request in self:
            missing = request.panel_ids.analysis_ids - request.result_ids.analysis_id
            if missing:
                request.result_ids = [Command.create({'analysis_id': a.id}) for a in missing]

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', 'Nouvelle') == 'Nouvelle':
                vals['name'] = self.env['ir.sequence'].next_by_code('lab.request')
        requests = super().create(vals_list)
        requests.filtered(lambda r: not r.result_ids)._sync_results_from_panels()
        return requests

    def write(self, vals):
        if 'state' in vals:
            moved = self.filtered(lambda r: r.state != vals['state'])
            if any(r.state not in STATE_FROM[vals['state']] for r in moved):
                raise UserError(_("Ce changement d'état ne suit pas le cycle de la demande."))
        if vals.get('state') == 'validated' and not self.env.context.get('lab_validation'):
            raise UserError(_("Une demande ne se valide que par le bouton Valider."))
        result = super().write(vals)
        if 'panel_ids' in vals:
            self._sync_results_from_panels()
        return result

    @api.onchange('panel_ids')
    def _onchange_panel_ids(self):
        self._sync_results_from_panels()

    @api.model
    def _assign_missing_names(self):
        for request in self.search([('name', '=', 'Nouvelle')]):
            request.name = self.env['ir.sequence'].next_by_code('lab.request')

    def action_sample(self):
        for request in self.filtered(lambda r: r.state == 'draft'):
            if not request.result_ids:
                raise UserError(_("%s : aucune analyse à prélever.", request.name))
            request.sample_ids = [Command.create({'sample_type': t}) for t in request._get_sample_types()]
            request.state = 'sampled'

    def action_analyse(self):
        for request in self.filtered(lambda r: r.state == 'sampled'):
            missing = request._get_pending_results()
            if missing:
                raise UserError(_("%(req)s : résultats manquants (%(codes)s).",
                                  req=request.name, codes=', '.join(missing.mapped('analysis_code'))))
            request.state = 'analysed'

    def action_validate(self):
        to_validate = self.filtered(lambda r: r.state == 'analysed')
        to_validate.with_context(lab_validation=True).write({
            'state': 'validated',
            'validated_by_id': self.env.uid,
            'validated_date': fields.Datetime.now(),
        })
        return True

    def action_reset_draft(self):
        todo = self.filtered(lambda r: r.state != 'validated')
        todo.write({'state': 'draft'})
        todo.sample_ids.unlink()
