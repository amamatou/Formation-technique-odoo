# -*- coding: utf-8 -*-
{
    'name': "INSTANCE REQUEST",

    'summary': """
        Instance request""",

    'description': """
        Instance request
    """,

    'author': "Mhao",
    'website': "https://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/16.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Tools',
    'version': '16.0',

    # any module necessary for this one to work correctly
    'depends': ['base', 'mail', 'contacts', 'sale_management', 'hr'],

    # always loaded
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'wizard/instance_wizard.xml',
        'wizard/instance_bon_wizard.xml',
        'views/instance_request.xml',
        'views/odoo_version.xml',
        'views/res_partner.xml',
        'views/hr_employee.xml',
        'views/devis.xml',
        'data/version_odoo.xml',
        'data/instance_request_to_process.xml',
        'data/create_instance_mail_template.xml',
        'data/instance_created_mail_template.xml',
        'data/perimeters.xml',
        'data/instance_sequence.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
