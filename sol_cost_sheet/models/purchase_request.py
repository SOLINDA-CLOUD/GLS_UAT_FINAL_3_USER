from odoo.exceptions import ValidationError
from odoo import _, api, fields, models

_STATES = [
    ("draft", "Draft"),
    ("to_approve", "To be approved"),
    ("approved_gm", "Approved GM/PM"),
    ("approved_dir", "Approved Direksi"),
    ("approved", "Approved"),
    ("rejected", "Rejected"),
    ("done", "Done"),
]
class PurchaseRequest(models.Model):
    _inherit = 'purchase.request'
    
    qty_is_bigger = fields.Boolean(compute='_compute_qty_is_bigger', string='Qty Is Bigger')
    project_code = fields.Char('Project Code',store=True)
    
    # state = fields.Selection(selection_add=[
    # ("to_approve", "Waiting Approval GM/PM"),
    # ("approved_gm", "Approved GM/PM"),
    # ("approved",)],
    # ondelete={'approved_gm': 'cascade', 'approved_dir': 'cascade'})
    
    
    def action_approve_gm(self):
        item_line = self.line_ids.filtered(lambda x : x.product_qty_is_bigger)
        data = []
            
        
        if self.qty_is_bigger:
            
            for item in item_line:
                if not item.reason_qty_different:
                    data.append((item.product_id.display_name))
                    # raise ValidationError('')
            if data and not self.create_directly:
                raise ValidationError(
                        """Qty Product below is bigger than qty demand:
                        %s
please fill the Reason field in table to continue
                        """%(data))
            else:
                self.write({'state':'approved_gm'})
        else:
            self.button_approved()
            
        
    def action_approve_dir(self):
        self.write({'state':'approved_dir'})
    
    def _compute_qty_is_bigger(self):
        for this in self:
            data = []
            for line in self.line_ids:
                if line.product_qty > line.qty_item:
                    data.append(True)
            
            
            this.qty_is_bigger = True if data else False
            

class PurchaseRequestLine(models.Model):
    _inherit = 'purchase.request.line'
    
    
    item_id = fields.Many2one('item.item', string='Item')
    qty_item = fields.Integer('Qty RAP',related='item_id.product_qty')
    reason_qty_different = fields.Text('Reason')
    product_qty_is_bigger = fields.Boolean(compute='_compute_product_qty_is_bigger', string='Product QTy IS Bigger')
    project_code = fields.Char('Project Code',related="request_id.project_code")
    
    # @api.depends('')
    def _compute_product_qty_is_bigger(self):
        for this in self:
            this.product_qty_is_bigger = this.product_qty > this.qty_item