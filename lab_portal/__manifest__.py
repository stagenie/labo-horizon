{
    'name': 'Labo Horizon — Portail',
    'version': '20.0.1.16.0',
    'summary': 'Résultats validés en ligne pour les patients, compte rendu en PDF',
    'category': 'Services',
    'author': 'OdooSkills',
    'website': 'https://odooskills.com',
    'license': 'LGPL-3',
    'depends': ['lab_billing', 'portal', 'website'],
    'data': [
        'security/ir.access.csv',
        'data/portal_entry_data.xml',
        'views/lab_patient_views.xml',
        'views/lab_portal_templates.xml',
    ],
}
