from odoo import _, api, fields, models

class StockPicking(models.Model):
    _inherit = 'stock.picking'
    _description = 'Stock Picking'
    
    shutdown_id = fields.Many2one('shutdown.system', string='Shutdown')
    job_order_id = fields.Many2one('job.order.request', string='Job Order') 
    maintenance_id = fields.Many2one('maintenance.request', string='Maintenance') 
