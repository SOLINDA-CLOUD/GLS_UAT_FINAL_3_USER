# -*- coding: utf-8 -*-
# from odoo import http


# class YmReportTender(http.Controller):
#     @http.route('/sol_report_tender/sol_report_tender/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/sol_report_tender/sol_report_tender/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('sol_report_tender.listing', {
#             'root': '/sol_report_tender/sol_report_tender',
#             'objects': http.request.env['sol_report_tender.sol_report_tender'].search([]),
#         })

#     @http.route('/sol_report_tender/sol_report_tender/objects/<model("sol_report_tender.sol_report_tender"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('sol_report_tender.object', {
#             'object': obj
#         })
