{
    'name': "Vendor Bill - Approval Process",
    'version': '16.0.0.1',
    'category': "Internal Customization",
    'website': "https://www.stringdata.cz/produkty/odoo-erp/",
    'summary': """
       Add the extension for approving Vendor Bills.
    """,
    'author': 'Stringdata s.r.o',
    'depends': ['base', 'account', 'analytic'],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'views/account_move_view.xml',
        'views/analytic_account_view.xml',
        'views/res_users_views.xml',
    ],
    'installable': True,
    'application': True,
}

