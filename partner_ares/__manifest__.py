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
            # tento import v originalnim v modulu partner_autocomplete neni, nicmene taky nepomohl
            'partner_ares/static/src/lib/jsvat.js',
        ],
        # Pridano dle https://stackoverflow.com/questions/73103280/odoo15-how-can-i-load-js-in-qweb-template
        'web.assets_frontend': [
            'partner_ares/static/src/lib/jsvat.js',
        ],
        'web.tests_assets': [
            'partner_ares/static/lib/**/*',
        ],
        # 'web.qunit_suite_tests': [
        #     'partner_ares/static/tests/**/*',
        # ],
    },
}
