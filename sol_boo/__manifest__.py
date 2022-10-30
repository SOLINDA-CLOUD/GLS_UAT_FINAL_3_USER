# -*- coding: utf-8 -*-
{
    'name': "sol_boo",

    'summary': """
        Short (1 phrase/line) summary of the module's purpose, used as
        subtitle on modules listing or apps.openerp.com""",

    'description': """
        Long description of module's purpose
    """,

    'author': "Luthfi A.Nizar - 08998046065",
    'website': "http://https://www.linkedin.com/in/luthfi-nizar-388a89195/",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/14.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','mail','stock','maintenance','report_xlsx'],

    # always loaded
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'data/sequence.xml',
        'data/data.xml',
        'views/reporting_view.xml',
        'views/pivot_graph.xml',
        'views/stock_location.xml',
        'views/trouble_master.xml',
        'views/job_order_req.xml',
        'views/water_prod.xml',
        'views/chemical_catridge.xml',
        'views/shutdown_system.xml',
        'views/maintenance_request.xml',
        'views/menu_items.xml',
        'views/templates.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
