# -*- coding: utf-8 -*-
# from odoo import http


# class SolVendorManagement(http.Controller):
#     @http.route('/sol_vendor_management/sol_vendor_management', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/sol_vendor_management/sol_vendor_management/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('sol_vendor_management.listing', {
#             'root': '/sol_vendor_management/sol_vendor_management',
#             'objects': http.request.env['sol_vendor_management.sol_vendor_management'].search([]),
#         })

#     @http.route('/sol_vendor_management/sol_vendor_management/objects/<model("sol_vendor_management.sol_vendor_management"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('sol_vendor_management.object', {
#             'object': obj
#         })
