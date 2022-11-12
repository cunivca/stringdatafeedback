{
    'name': 'Svátky',
    'version': '0',
    'author': 'StringData s.r.o',
    'category': 'Svátky',
    'complexity': 'easy',
    'Summary': 'A Module For a name day notifications',
    'depends': ['base'],
    'data': [
        'security/ir.model.access.csv',
        'views/partner_views.xml',
        'views/nameday_views.xml',
        'views/svatky_menus.xml',
        'data/partner.nameday.csv',
        'data/partner.xml',
    ],
    'installable': True,
    'application': True
}
