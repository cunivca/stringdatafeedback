{
    'name': 'Birthday',
    'version': '0',
    'author': 'StringData s.r.o',
    'category': 'Birthday',
    'complexity': 'easy',
    'Summary': 'A Module For a birthday wishes',
    'depends': ['base','svatky'],
    'data': [
        'views/partner_views.xml',
        'data/mail_template_data.xml',
        'data/cron_birthday_wish.xml',
    ],
    'installable': True,
    'application': True
}
