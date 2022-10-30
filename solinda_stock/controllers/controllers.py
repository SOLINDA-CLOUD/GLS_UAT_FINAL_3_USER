# -*- coding: utf-8 -*-
# from odoo import http


# class SolindaStock(http.Controller):
#     @http.route('/solinda_stock/solinda_stock', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/solinda_stock/solinda_stock/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('solinda_stock.listing', {
#             'root': '/solinda_stock/solinda_stock',
#             'objects': http.request.env['solinda_stock.solinda_stock'].search([]),
#         })

#     @http.route('/solinda_stock/solinda_stock/objects/<model("solinda_stock.solinda_stock"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('solinda_stock.object', {
#             'object': obj
#         })
