# -*- coding: utf-8 -*-
# from odoo import http


# class SolindaProject(http.Controller):
#     @http.route('/solinda_project/solinda_project', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/solinda_project/solinda_project/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('solinda_project.listing', {
#             'root': '/solinda_project/solinda_project',
#             'objects': http.request.env['solinda_project.solinda_project'].search([]),
#         })

#     @http.route('/solinda_project/solinda_project/objects/<model("solinda_project.solinda_project"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('solinda_project.object', {
#             'object': obj
#         })
