# -*- coding: utf-8 -*-
{
    'name': "sol_cost_sheet",

    'summary': """
        Short (1 phrase/line) summary of the module's purpose, used as
        subtitle on modules listing or apps.openerp.com""",

    'description': """
        Long description of module's purpose
    """,

    'author': "My Company",
    'website': "http://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/14.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','mail','account','project','sale_project','sale_crm','purchase_requisition','purchase','purchase_request','report_xlsx'],

    # always loaded
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'data/data.xml',
        'views/master_item.xml',
        'views/crm_views.xml',
        'views/sale_order_views.xml',
        'views/cost_sheet_views.xml',
        'views/item_views.xml',
        'wizard/cost_sheet_component.xml',
        'views/project_views.xml',
        'views/rap_views.xml',
        'views/approval_views.xml',
        'views/purchase_request_views.xml',
        'views/purchase_order.xml',
        'views/account_move.xml',
        'wizard/rap_report.xml',
        'report/report_quotation_turnkey.xml',
        'report/report_quotation_trading.xml',
        'report/action_report.xml',
        'views/menuitem.xml',
        'views/sequence_data.xml',
        'views/templates.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
    'license': 'LGPL-3'
}
