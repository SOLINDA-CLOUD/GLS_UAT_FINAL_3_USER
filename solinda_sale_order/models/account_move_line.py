from odoo import _, api, fields, models

class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'
    
    
    payment_schedule_ids = fields.Many2many('payment.schedule')    