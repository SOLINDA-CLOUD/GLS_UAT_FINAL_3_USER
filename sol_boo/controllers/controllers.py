# -*- coding: utf-8 -*-
# from odoo import http


# class SolBoo(http.Controller):
#     @http.route('/sol_boo/sol_boo', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/sol_boo/sol_boo/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('sol_boo.listing', {
#             'root': '/sol_boo/sol_boo',
#             'objects': http.request.env['sol_boo.sol_boo'].search([]),
#         })

#     @http.route('/sol_boo/sol_boo/objects/<model("sol_boo.sol_boo"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('sol_boo.object', {
#             'object': obj
#         })
