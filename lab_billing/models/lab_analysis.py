from odoo import api, fields, models
from odoo.fields import Command


class LabAnalysis(models.Model):
    _inherit = 'lab.analysis'

    price = fields.Float('Tarif', digits='Product Price')
    product_id = fields.Many2one('product.product', 'Article', readonly=True, copy=False)

    @api.model_create_multi
    def create(self, vals_list):
        analyses = super().create(vals_list)
        analyses._sync_product()
        return analyses

    def write(self, vals):
        result = super().write(vals)
        if {'code', 'name', 'price'} & vals.keys():
            self._sync_product()
        return result

    def _sync_product(self):
        """L'article de service suit l'analyse : créé au premier passage, mis à jour ensuite."""
        for analysis in self:
            values = {'name': analysis.name, 'default_code': analysis.code, 'list_price': analysis.price}
            if analysis.product_id:
                analysis.product_id.write(values)
            else:
                analysis.product_id = self.env['product.product'].create({
                    **values,
                    'type': 'service',
                    'taxes_id': [Command.clear()],   # actes de biologie médicale : exonérés de TVA
                })
