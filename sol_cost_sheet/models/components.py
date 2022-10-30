from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class ComponentComponent(models.Model):
    _name = 'component.component'
    _description = 'Component Component'
    _rec_name = "product_id"
    _order = "sequence"
    
    
    cost_sheet_id = fields.Many2one('cost.sheet', string='Cost Sheet',ondelete="cascade",copy=False)
    rap_id = fields.Many2one('rap.rap', string='RAP')
    category_id = fields.Many2one('rab.category', string='Category',ondelete="cascade")
    rap_category_id = fields.Many2one('rap.category', string='Category',ondelete="cascade")
    product_id = fields.Many2one('product.product',required=True)
    
    product_uom_category_id = fields.Many2one(related='product_id.uom_id.category_id', readonly=True)
    uom_id = fields.Many2one('uom.uom')
    product_qty = fields.Integer('Quantity',default=1)
    item_ids = fields.One2many('item.item', 'component_id',copy=True)
    sequence = fields.Integer('Sequence')
    total_price = fields.Float(compute='_compute_total_price', string='Total Amount')
    created_after_approve = fields.Boolean('Created After Approve')
    rap_state = fields.Selection(related='rap_id.state',store=True)
    
    @api.onchange('product_id')
    def onchange_product_id(self):
        if not self.product_id:
            return

        self.uom_id = self.product_id.uom_po_id or self.product_id.uom_id

    
    @api.depends('item_ids.total_price')
    def _compute_total_price(self):
        for this in self:
            this.total_price = sum(this.item_ids.filtered(lambda x:x.cost_sheet_id).mapped('total_price'))
    
    # @api.constrains('product_id')
    # def _constrains_product_id(self):
    #     for this in self:
    #         data = this.env['component.component'].search([('cost_sheet_id', '=', this.cost_sheet_id.id),('category_id', '=', this.category_id.id),('product_id', '=', this.product_id.id)])
    #         if len(data) > 1:
    #             raise ValidationError('Cannot create same product in one component')
    
    def get_items_rab(self):
        master = self.env['master.item'].search([('product_id', '=', self.product_id.id)])
        data = []
        if master:
            for item in master[0].item_line_ids:
                if item.product_id.detailed_type != 'service':
                    stock_valuation = item.product_id.stock_valuation_layer_ids.sorted(reverse=True)
                else:
                    stock_valuation = item.env['purchase.order.line'].search([('product_id', '=', item.product_id.id),('po_confirm_date', '<=', fields.Date.context_today(i))],order="po_confirm_date desc",limit=1)
                if stock_valuation:
                    cost = stock_valuation[0].unit_cost if stock_valuation else 0.0
                else:
                    cost = 0
                data.append((0,0,{
                    'cost_sheet_id': self.cost_sheet_id.id,
                    'product_id': item.product_id.id,
                    'name': item.product_id.display_name,
                    'uom_id': item.product_id.uom_id.id,
                    'category_id': self.category_id.id,
                    'rfq_price': cost,
                }))
            self.write({'item_ids':data})

            # self.write({
            #     'item_ids':[(0,0,{
            #         'cost_sheet_id': self.cost_sheet_id.id,
            #         'product_id': item.product_id.id,
            #         'name': item.product_id.display_name,
            #         'uom_id': item.product_id.uom_id.id,
            #         'category_id': self.category_id.id,
            #         'rfq_price': cost,
            #     }) for item in master[0].item_line_ids]
            # })
        else:
            raise ValidationError('Master data items for Component %s does not exist'%(self.product_id.display_name))
    
    def get_items_rap(self):
        master = self.env['master.item'].search([('product_id', '=', self.product_id.id)])
        
        if master:
            self.write({
                'item_ids':[(0,0,{
                    'rap_id':self.rap_id.id,
                    'product_id': item.product_id.id,
                    'uom_id': item.product_id.uom_id.id,
                    'category_id': self.category_id.id                
                }) for item in master[0].item_line_ids]
            })
        else:
            raise ValidationError('Master data items for Component %s does not exist'%(self.product_id.display_name))
    
    # @api.onchange('category_id')
    # def _onchange_category_id(self):
    #     if self.category_id:
    #         self.cost_sheet_id = self.category_id.cost_sheet_id.id

    def action_view_items(self):
        return {
                'name': 'Item for %s'%self.product_id.display_name,
                'type': 'ir.actions.act_window',
                'view_mode': 'form',
                'res_model': 'component.component',
                'res_id': self.id,
            }
    
    def action_view_items_rap(self):
        return {
                'name': 'Item for %s'%self.product_id.display_name,
                'type': 'ir.actions.act_window',
                'view_mode': 'form',
                'res_model': 'component.component',
                'res_id': self.id,
                'view_id': self.env.ref('sol_cost_sheet.rap_component_component_view_form').id
            }
    def action_view_items_rap_revisied(self):
        return {
                'name': 'Item for %s'%self.product_id.display_name,
                'type': 'ir.actions.act_window',
                'view_mode': 'form',
                'res_model': 'component.component',
                'res_id': self.id,
                'view_id': self.env.ref('sol_cost_sheet.rap_revisied_component_component_view_form').id
            }
    
    

