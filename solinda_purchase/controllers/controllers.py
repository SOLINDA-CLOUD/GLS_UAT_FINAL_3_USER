# -*- coding: utf-8 -*-
# from odoo import http


# class SolindaPurchase(http.Controller):
#     @http.route('/solinda_purchase/solinda_purchase', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/solinda_purchase/solinda_purchase/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('solinda_purchase.listing', {
#             'root': '/solinda_purchase/solinda_purchase',
#             'objects': http.request.env['solinda_purchase.solinda_purchase'].search([]),
#         })

#     @http.route('/solinda_purchase/solinda_purchase/objects/<model("solinda_purchase.solinda_purchase"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('solinda_purchase.object', {
#             'object': obj
#         })
