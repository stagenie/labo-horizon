from odoo import fields, models

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
