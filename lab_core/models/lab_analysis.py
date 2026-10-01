from odoo import _, api, fields, models
from odoo.exceptions import ValidationError

SAMPLE_TYPES = [('blood', 'Sang'), ('urine', 'Urine'), ('swab', 'Écouvillon')]


class LabAnalysis(models.Model):
    _name = 'lab.analysis'
    _description = 'Analyse'
    _order = 'code'
    _rec_names_search = ('code', 'name')

    code = fields.Char('Code', required=True)
    name = fields.Char('Libellé', required=True, translate=True)
    sample_type = fields.Selection(SAMPLE_TYPES, 'Prélèvement', required=True, default='blood')
    unit = fields.Char('Unité')
    ref_min = fields.Float('Borne basse', digits=(10, 2))
    ref_max = fields.Float('Borne haute', digits=(10, 2))
    ref_min_female = fields.Float('Borne basse (femme)', digits=(10, 2))
    ref_max_female = fields.Float('Borne haute (femme)', digits=(10, 2))
    protocol = fields.Binary('Fiche technique', attachment=True)
    protocol_filename = fields.Char('Nom du fichier')
    active = fields.Boolean(default=True)

    _code_uniq = models.Constraint('UNIQUE (code)', "Ce code d'analyse existe déjà.")

    @api.constrains('ref_min', 'ref_max', 'ref_min_female', 'ref_max_female')
    def _check_ranges(self):
        for analysis in self:
            for low, high in ((analysis.ref_min, analysis.ref_max),
                              (analysis.ref_min_female, analysis.ref_max_female)):
                if high and low > high:
                    raise ValidationError(_("%s : la borne basse dépasse la borne haute.", analysis.code))

    def _get_range(self, gender):
        self.ensure_one()
        if gender == 'female' and (self.ref_min_female or self.ref_max_female):
            return (self.ref_min_female, self.ref_max_female)
        return (self.ref_min, self.ref_max)
