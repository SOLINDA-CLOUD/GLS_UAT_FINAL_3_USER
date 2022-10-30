# -*- coding: utf-8 -*-
{
    'name': "solinda_crm",

    'summary': """
        Short (1 phrase/line) summary of the module's purpose, used as
        subtitle on modules listing or apps.openerp.com""",

    'description': """
        Long description of module's purpose
    """,

    'author': "Siwi Wiyono Raharjo",
    'website': "https://www.linkedin.com/in/siwiyono",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/14.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','crm','sale','mail'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'security/security_access.xml',
        'views/crm_views.xml',
        'views/sale_views.xml',
        'views/mail_activity_type_view.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
    "application": True,
    'license': 'LGPL-3'
}
