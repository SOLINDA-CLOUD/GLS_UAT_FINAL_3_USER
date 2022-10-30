# -*- coding: utf-8 -*-

from email.policy import default
from odoo import api, fields, models, _
from datetime import date, datetime



class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'
    _description = 'Purchase Order'

    list_report_tender_id = fields.Many2one('list.report.tender', string='List Report Tender', ondelete="cascade")
    
    sewa_cdd_ket = fields.Char('Sewa CDD Ket.')
    sewa_cdd_harga = fields.Float('Sewa CCD Harga')
    delivery_time = fields.Char('Delivery Time')
    price = fields.Char('Price')
    

    def action_tolist_report_tender(self):
        active_ids = self.env.context.get('active_ids', [])
        list_report_tender =  False
        for rec in self:
            list_report_tender = self.env['list.report.tender'].create({
                'purchase_order_ids' : [(4, x) for x in active_ids],
            })

            if list_report_tender:
                return {
                    'name': _('List Report Tender'),
                    'view_type': 'form',
                    'view_mode': 'form',
                    'res_model': 'list.report.tender',
                    'res_id': list_report_tender.id,
                    'type': 'ir.actions.act_window',
                    # 'domain': [('id', 'in', move_ids)],
                    # 'context': {
                    #     'create_date': datetime.today(),
                    #     'create_date': fields.Datetime.today(),
                    # },
                }
    

class ListReportTender(models.Model):
    _name = 'list.report.tender'
    _description = 'List Report Tender'


    purchase_order_ids = fields.One2many('purchase.order', 'list_report_tender_id', string='List Tender')
    tax_id = fields.Many2one('account.tax', string='VAT')
    customs = fields.Float('Customs')

    def print_xlsx(self):
        return self.env.ref('sol_report_tender.report_list_tender_excel').report_action(self)


