# -*- coding: utf-8 -*-
{
    'name': "Birthday	reminder",

    'summary': """Employees	birthday reminder module""",

    'description': """""",

    'author': "YI",
    'website': "",

    'category': 'Human Resources/Employees',
    'version': '14.0.0.1',

    'depends': ['base', 'hr'],

    'data': [
        'data/remind_birthday_data.xml',
        'data/remind_birthday_cron.xml',

        'views/res_config_settings.xml',
        'views/hr_employee_views.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}
