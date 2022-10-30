from odoo import _, api, fields, models
from odoo.exceptions import ValidationError

class StockPicking(models.Model):
    _inherit = 'stock.picking'
    _description = 'Stock Picking'
    
    ship_via = fields.Char(string='Ship Via')
    
    def button_validate(self):
        for i in self:
            if i.picking_type_id:
                for t in i.picking_type_id:
                    if t.code == 'internal' and not self.user_has_groups("solinda_stock.validate_internal_groupsol"):
                        raise ValidationError("You are not allowed to validate this document!")
                    elif t.code == 'outgoing' and not self.user_has_groups("solinda_stock.sales_marketing_groupsol"):
                        raise ValidationError("You are not allowed to validate this document!")
        return super(StockPicking,self).button_validate()  

    