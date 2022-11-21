{
    'name': "Ares Connector",
    'version': '16.0.0.1',
    'description': """
       Auto-complete partner companies data using Ares API
    """,
    'author': 'StringData s.r.o',
    'depends': [
        'iap_mail',
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/res_partner_views.xml',
        'views/res_company_views.xml',
    ],
    'installable': True,
    'application': True,
    'assets': {
        'web.assets_backend': [
            'partner_ares/static/src/scss/*',
            'partner_ares/static/src/js/*',
            'partner_ares/static/src/xml/*',
        ],
        'web.tests_assets': [
            'partner_ares/static/src/lib/**/*',
        ],
        # 'web.qunit_suite_tests': [
        #     'partner_ares/static/tests/**/*',
        # ],
    },
}
