{
    'name': 'Labo Horizon — Aller plus loin',
    'version': '20.0.1.19.0',
    'summary': "Jauge OWL 3 des résultats, API pour les automates, tests",
    'category': 'Services',
    'author': 'OdooSkills',
    'website': 'https://odooskills.com',
    'license': 'LGPL-3',
    'depends': ['lab_core', 'web'],
    'data': [
        'views/lab_request_views.xml',
        'views/lab_result_views.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'lab_owl/static/src/gauge/lab_gauge_field.js',
            'lab_owl/static/src/gauge/lab_gauge_field.xml',
            'lab_owl/static/src/gauge/lab_gauge_field.scss',
        ],
        'web.assets_unit_tests': [
            'lab_owl/static/tests/**/*',
        ],
    },
    'installable': True,
}
