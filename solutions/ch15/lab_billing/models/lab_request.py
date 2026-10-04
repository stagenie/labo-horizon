from markupsafe import Markup

from odoo import _, api, fields, models
from odoo.exceptions import UserError
from odoo.fields import Command


class LabRequest(models.Model):
    _inherit = 'lab.request'

    invoice_ids = fields.Many2many(
        'account.move', 'lab_request_account_move_rel', 'request_id', 'move_id',
        string='Factures', readonly=True, copy=False)
    invoice_count = fields.Integer('Nombre de factures', compute='_compute_invoice_count')
    billing_state = fields.Selection([
        ('to_invoice', 'À facturer'),
        ('invoiced', 'Facturée'),
        ('paid', 'Payée'),
    ], 'Facturation', compute='_compute_billing_state', store=True)

    @api.depends('invoice_ids')
    def _compute_invoice_count(self):
        for request in self:
            request.invoice_count = len(request.invoice_ids)

    @api.depends('state', 'invoice_ids.state', 'invoice_ids.payment_state')
    def _compute_billing_state(self):
        for request in self:
            moves = request.invoice_ids.filtered(lambda m: m.state != 'cancel')
            if request.state != 'validated':
                request.billing_state = False
            elif not moves:
                request.billing_state = 'to_invoice'
            elif all(m.state == 'posted' and m.payment_state in ('paid', 'in_payment') for m in moves):
                request.billing_state = 'paid'
            else:
                request.billing_state = 'invoiced'

    def _billable_analyses(self):
        """Analyses réalisées. Le secrétariat facture sans lire les résultats (Ch.10) : la lecture
        privilégiée se limite à la liste des analyses, rendue ensuite à l'utilisateur."""
        self.ensure_one()
        return self.sudo().result_ids.analysis_id.sudo(False)

    def _split_amounts(self, analyses, rate):
        """{analyse: (part patient, part mutuelle)} : la part mutuelle est arrondie à la devise,
        la part patient est le reste, si bien que les deux parts font toujours le tarif."""
        currency = self.env.company.currency_id
        split = {}
        for analysis in analyses:
            insurer_part = currency.round(analysis.price * rate)
            split[analysis] = (currency.round(analysis.price - insurer_part), insurer_part)
        return split

    def _prepare_invoice_vals(self, partner, amounts, label):
        self.ensure_one()
        return {
            'move_type': 'out_invoice',
            'partner_id': partner.id,
            'invoice_origin': self.name,
            'invoice_line_ids': [Command.create({
                'product_id': analysis.product_id.id,
                'name': f"{analysis.code} — {analysis.name} ({label})",
                'quantity': 1,
                'price_unit': amount,
                'tax_ids': [Command.clear()],
            }) for analysis, amount in amounts.items()],
        }

    def _create_invoices(self):
        moves = self.env['account.move']
        for request in self:
            if request.state != 'validated':
                raise UserError(_("%s : seule une demande validée peut être facturée.", request.name))
            if request.invoice_ids.filtered(lambda m: m.state != 'cancel'):
                raise UserError(_("%s : cette demande est déjà facturée.", request.name))
            analyses = request._billable_analyses()
            if not analyses:
                raise UserError(_("%s : aucune analyse à facturer.", request.name))
            unpriced = analyses.filtered(lambda a: not a.price)
            if unpriced:
                raise UserError(_("%(request)s : tarif manquant pour %(codes)s.",
                                  request=request.name, codes=", ".join(unpriced.mapped('code'))))
            insurer = request.patient_id.insurer_id
            rate = insurer.coverage_rate / 100 if insurer else 0.0
            split = request._split_amounts(analyses, rate)
            patient_part = {a: parts[0] for a, parts in split.items() if parts[0]}
            insurer_part = {a: parts[1] for a, parts in split.items() if parts[1]}
            vals = []
            if patient_part:
                vals.append(request._prepare_invoice_vals(
                    request.patient_id._get_or_create_partner(), patient_part, _("part patient")))
            if insurer_part:
                vals.append(request._prepare_invoice_vals(
                    insurer.partner_id, insurer_part, _("part mutuelle, %s %%", insurer.coverage_rate)))
            new_moves = moves.create(vals)
            request.invoice_ids = [Command.link(move.id) for move in new_moves]
            partners = Markup(", ").join(Markup("<b>%s</b>") % move.partner_id.name for move in new_moves)
            request.message_post(body=Markup(_("Factures brouillon créées pour %s.")) % partners)
            moves |= new_moves
        return moves

    def action_create_invoices(self):
        self._create_invoices()
        return self.action_view_invoices() if len(self) == 1 else True

    def action_view_invoices(self):
        self.ensure_one()
        action = self.env['ir.actions.actions']._for_xml_id('account.action_move_out_invoice_type')
        action['domain'] = [('id', 'in', self.invoice_ids.ids)]
        return action
