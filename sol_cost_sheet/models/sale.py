from odoo import _, api, fields, models

class SaleOrder(models.Model):
    _inherit = 'sale.order'
    
    rab_id = fields.Many2one('cost.sheet',related='opportunity_id.rab_id', string='RAB', store=True)
    final_profit = fields.Float(related='rab_id.final_profit_percent',store=True)
    project_code = fields.Char('Project Code',related="opportunity_id.project_code")
    
    def action_confirm(self):
        res = super().action_confirm()
        if self.rab_id:
            self.rab_id.project_id = self.project_id.id
        return res
    
