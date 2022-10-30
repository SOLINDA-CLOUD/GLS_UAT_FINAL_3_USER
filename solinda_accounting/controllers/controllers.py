# -*- coding: utf-8 -*-
# from odoo import http


# class SolindaAccounting(http.Controller):
#     @http.route('/solinda_accounting/solinda_accounting', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/solinda_accounting/solinda_accounting/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('solinda_accounting.listing', {
#             'root': '/solinda_accounting/solinda_accounting',
#             'objects': http.request.env['solinda_accounting.solinda_accounting'].search([]),
#         })

#     @http.route('/solinda_accounting/solinda_accounting/objects/<model("solinda_accounting.solinda_accounting"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('solinda_accounting.object', {
#             'object': obj
#         })
