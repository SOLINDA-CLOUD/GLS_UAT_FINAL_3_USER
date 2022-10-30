# -*- coding: utf-8 -*-
# from odoo import http


# class Projectbaru(http.Controller):
#     @http.route('/projectbaru/projectbaru', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/projectbaru/projectbaru/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('projectbaru.listing', {
#             'root': '/projectbaru/projectbaru',
#             'objects': http.request.env['projectbaru.projectbaru'].search([]),
#         })

#     @http.route('/projectbaru/projectbaru/objects/<model("projectbaru.projectbaru"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('projectbaru.object', {
#             'object': obj
#         })
