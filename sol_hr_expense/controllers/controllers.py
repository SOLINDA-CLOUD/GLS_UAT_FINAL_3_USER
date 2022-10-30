# -*- coding: utf-8 -*-
# from odoo import http


# class HrExpense(http.Controller):
#     @http.route('/hr_expense/hr_expense', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/hr_expense/hr_expense/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('hr_expense.listing', {
#             'root': '/hr_expense/hr_expense',
#             'objects': http.request.env['hr_expense.hr_expense'].search([]),
#         })

#     @http.route('/hr_expense/hr_expense/objects/<model("hr_expense.hr_expense"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('hr_expense.object', {
#             'object': obj
#         })
