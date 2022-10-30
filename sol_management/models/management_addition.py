from odoo import models, fields, api
from . import vendor_management as vm
from . import customer_management as cm

class VendorAdd(models.Model):
    _inherit = 'res.partner'

    visible_management = fields.Selection(vm.VendorManagement.point, string='Last Management Vendor', compute='_calculate_eval', readonly=True)
    visible_management_cust = fields.Selection(cm.CustomerManagement.point, string='Last Management Customer', compute='_calculate_eval_cust', readonly=True)
    # test = fields.Boolean(string="Test", default=False)
    
    @api.depends()
    def _calculate_eval(self):
        for rec in self:
            record = self.env['vendor.management'].search([
                ('vendor', '=', rec.id),
                ('state', '=', 'approved')
            ])
            if record:
                rec.visible_management = record.sorted('period_end', reverse=True)[0].final_rate 
                # rec.test = True
            else:
                rec.visible_management = False

    @api.depends()
    def _calculate_eval_cust(self):
        for rec in self:
            record = self.env['customer.management'].search([
                ('customer', '=', rec.id),
                ('state', '=', 'approved')
            ])
            if record:
                rec.visible_management_cust = record.sorted('period_end', reverse=True)[0].final_rate_cust
                # rec.test = True
            else:
                rec.visible_management_cust = False
