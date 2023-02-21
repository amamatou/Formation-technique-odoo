# -*- coding: utf-8 -*-
{
    'name': "INSTANCE REQUEST",

    'summary': """
        Demande d'instance""",

    'description': """
        Demande d'instance
    """,

    'author': "Mhao",
    'website': "https://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/16.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Tools',
    'version': '16.0',

    # any module necessary for this one to work correctly
    'depends': ['instance_request'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'security/security.xml',
        #'views/views.xml',
        #'views/templates.xml',
        'views/instance_request.xml',
        'views/odoo_version.xml',
        #'reports/rapport.xml',
        'data/version_odoo.xml',
        'data/instance_request_to_process.xml',
        'data/create_instance_mail_template.xml',
        'data/instance_created_mail_template.xml'
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
