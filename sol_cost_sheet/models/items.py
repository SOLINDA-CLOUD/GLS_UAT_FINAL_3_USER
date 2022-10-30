from odoo import _, api, fields, models
from odoo.tools.misc import get_lang

from odoo.exceptions import ValidationError

class Item(models.Model):
    _name = 'item.item'
    _description = 'Item'
    _rec_name = "product_id"
    
    
    cost_sheet_id = fields.Many2one('cost.sheet', string='Cost Sheet',ondelete="cascade",copy=False)
    rap_id = fields.Many2one('rap.rap', string='RAP')
    product_id = fields.Many2one('product.product')
    product_uom_category_id = fields.Many2one(related='product_id.uom_id.category_id', readonly=True)
    category_id = fields.Many2one('rab.category', string='Category',ondelete="cascade",copy=False)
    rap_category_id = fields.Many2one('rap.category', string='Category',ondelete="cascade")
    component_id = fields.Many2one('component.component',ondelete="cascade")
    sequence = fields.Integer('Sequence')
    name = fields.Char('Description',copy=True)
    project_id = fields.Many2one('project.project', related='rap_id.project_id',store=True)
    display_type = fields.Selection([
        ('line_section', "Section"),
        ('line_note', "Note")], default=False, help="Technical field for UX purpose.")
    product_type = fields.Selection(related='product_id.detailed_type',store=True)
    # qty_on_hand = fields.Float('Qty On Hand',related='product_id.qty_available')
    uom_id = fields.Many2one('uom.uom')
    product_qty = fields.Integer('Quantity',default=1,copy=True)
    existing_price = fields.Float('Existing Price',compute="_compute_existing_price",store=True)
    rfq_price = fields.Float('RFQ Price',copy=True)
    total_price = fields.Float(compute='_compute_total_price', string='Total Price',store=True)
    remarks = fields.Text('Remarks',copy=True)
    created_after_approve = fields.Boolean('Created After Approve')
    # can_be_purchased = fields.Boolean(compute='_compute_can_be_purchased', string='Can BE Purchased',store=True)
    purchase_line_ids = fields.One2many('purchase.request.line', 'item_id', string='Purchase Line')
    revisied = fields.Boolean('Revisied')
    
    purchase_request_line_ids = fields.One2many('purchase.request.line', 'item_id', string='Purchase REquest Line')
    purchase_order_line_ids = fields.One2many('purchase.order.line', 'item_id', string='Purchase Order Line')
    qty_pr = fields.Integer(compute='_compute_qty_pr', string='Qty on PR')
    qty_po = fields.Integer(compute='_compute_qty_po', string='Qty on PO')
    qty_received = fields.Integer(compute='_compute_qty_received', string='Qty Received')
    # price_po = fields.Float(compute='_compute_qty_po', string='PO Price')
    price_po = fields.Float(compute='_compute_price_po', string='PO Price')
    project_code = fields.Char('Project Code', related="rap_id.project_id.code")
    data_type = fields.Selection([
        ('normal', 'Normal'),
        ('edit', 'Edited'),
        ('add', 'Additional'),
    ], string='Data Type',default="normal")
    """Alur ke atas => component.component(component_id) =>  rap.category(rap_category_id) => rap.rap(rap_id)"""
    edited_field = fields.Text('Edited Field')
    status_button = fields.Char(compute='_compute_status_button', string='Status Button')
    
    @api.depends('total_price','price_po')
    def _compute_status_button(self):
        for i in self:
            if i.price_po < i.total_price:
                i.status_button = 'up'
            elif i.price_po > i.total_price:
                i.status_button = 'down'
            else:
                i.status_button = 'equal'

             

    def write(self,vals):
        res = super(Item, self).write(vals)
        if self.data_type != 'add' and self.rap_id.revision_on:
            self.data_type = 'edit'
        return res
    
    def status(self):
        return

    @api.model
    def create(self, vals):
        res = super(Item, self).create(vals)
        rap = res.component_id.rap_category_id.rap_id.revision_on
        if rap:
            res.data_type = 'add'
        return res 

    # @api.depends('purchase_request_line_ids')
    def _compute_qty_pr(self):
        for this in self:
            this.qty_pr = sum(this.purchase_request_line_ids.mapped('product_qty'))
    
    @api.depends('purchase_order_line_ids.price_subtotal','qty_po')
    def _compute_price_po(self):
        for this in self:
            this.price_po = sum(this.purchase_order_line_ids.mapped('price_subtotal'))
            
            
    # @api.depends('purchase_order_line_ids.product_qty','purchase_order_line_ids.price_subtotal')
    def _compute_qty_po(self):
        for this in self:
            this.qty_po = sum(this.purchase_order_line_ids.mapped('product_qty'))
            # this.price_po = sum(this.purchase_order_line_ids.mapped('price_subtotal'))

    def _compute_qty_received(self):
        for this in self:
            this.qty_received = sum(
                this.purchase_order_line_ids.mapped('qty_received'))
    
    @api.onchange('product_id')
    def _onchange_product_rfqprice(self):
        for i in self:
            if i.product_id.detailed_type != 'service':
                stock_valuation = i.product_id.stock_valuation_layer_ids.sorted(reverse=True)
            else:
                stock_valuation = i.env['purchase.order.line'].search([('product_id', '=', i.product_id.id),('po_confirm_date', '<=', fields.Date.context_today(i))],order="po_confirm_date desc",limit=1)
            if stock_valuation:
                cost = stock_valuation[0].unit_cost if stock_valuation else 0.0
            else:
                cost = 0
            if not i.rfq_price:
                i.rfq_price = cost
            else:
                i.rfq_price = 0

    @api.depends('product_id')
    def _compute_existing_price(self):
        for this in self:
            if this.product_id.detailed_type != 'service':
                stock_valuation = this.product_id.stock_valuation_layer_ids.sorted(reverse=True)
            else:
                stock_valuation = this.env['purchase.order.line'].search([('product_id', '=', this.product_id.id),('po_confirm_date', '<=', fields.Date.context_today(this))],order="po_confirm_date desc",limit=1)
            if stock_valuation:
                cost = stock_valuation[0].unit_cost if stock_valuation else 0.0
                this.existing_price = cost
            else:
                cost = 0
                this.existing_price = cost
            # if not this.rfq_price:
            #     this.rfq_price = cost
            # else:
            #     this.rfq_price = 0
                

    @api.onchange('product_id')
    def onchange_product_id(self):
        if not self.product_id:
            return

        self.uom_id = self.product_id.uom_po_id or self.product_id.uom_id
        product_lang = self.product_id.with_context(
            lang=get_lang(self.env, self.env.user.partner_id.lang).code,
            partner_id=self.env.user.partner_id.id,
            company_id=self.env.company.id,
        )
        name = product_lang.display_name
        if product_lang.description_purchase:
            name += '\n' + product_lang.description_purchase
        self.name = name
    
    # @api.depends('qty_on_hand','product_qty')
    # def _compute_can_be_purchased(self):
    #     for this in self:
    #         this.can_be_purchased = this.qty_on_hand < this.product_qty
        
    @api.depends('product_qty','rfq_price')
    def _compute_total_price(self):
        for this in self:
            this.total_price = this.product_qty * this.rfq_price
    
    @api.constrains('product_id')
    def _constrains_product_id(self):
        for this in self:
            data = this.env['item.item'].search([('cost_sheet_id', '=', this.cost_sheet_id.id),('category_id', '=', this.category_id.id),('product_id', '=', this.product_id.id)])
            if len(data) > 2:
                raise ValidationError('Cannot create same product in one item')

    
    def view_item_in_purchase(self):
        return {
                'name': 'Item In Purchase',
                'type': 'ir.actions.act_window',
                'view_mode': 'tree,form',
                'res_model': 'purchase.request',
                'domain': [('id','in',self.purchase_line_ids.mapped('request_id.id'))],
                # 'res_id': purchase.id,
        }
    def view_item_in_pr_line(self):
        return {
                'name': 'Item In Purchase',
                'type': 'ir.actions.act_window',
                'view_mode': 'tree,form',
                'res_model': 'purchase.request.line',
                'domain': [('id','in',self.purchase_request_line_ids.ids)],
                # 'res_id': purchase.id,
        }
    def view_item_in_po_line(self):
        return {
                'name': 'Item In PO',
                'type': 'ir.actions.act_window',
                'view_mode': 'tree,form',
                'res_model': 'purchase.order.line',
                'domain': [('id','in',self.purchase_order_line_ids.ids)],
                # 'res_id': purchase.id,
        }
    
    def create_analytic_account_id(self,code,seq):
        analytic_name = code + " 1."+ str(seq)
        analytic_account_existing = self.env['account.analytic.account'].search([('name', '=', analytic_name)],limit=1)
        if analytic_account_existing:
            return analytic_account_existing.id
        else:
            analytic_account_id = self.env['account.analytic.account'].create({'name':analytic_name})
            return analytic_account_id.id


    def create_purchase_request(self):
        # items = [item.product_id.name for item in self if not item.can_be_purchased] # Pengecekan product/item yang tidak dapat create purchase karna qty_on_hand lebih atau sama dengan quantity  
        # if items:
        #     raise ValidationError("""There are Product can't created purchase order because Qty on Hand is bigger or equal than Quantity:
        #     %s"""%items)
        for i in self:
            if i[0].rap_id.state == 'waiting':
                raise ValidationError("Cannot create Purchase Request because RAP with number %s is waiting for approval"%(i.rap_id.name))
            purchase = i.env['purchase.request'].create({
                'project_code':i.project_code,           
                'line_ids':[(0,0,{
                    'product_id': item.product_id.id,
                    'product_qty': item.product_qty,
                    'analytic_account_id': item.create_analytic_account_id(item.project_code,item.rap_category_id.sequence+1),
                    'estimated_cost': item.rfq_price,
                    'item_id': item.id,
                    'project_code':item.project_code               
                    }) for item in self],
            })
        
        return {
                'name': 'Purchase Request',
                'type': 'ir.actions.act_window',
                'view_mode': 'tree,form',
                'res_model': 'purchase.request',
                'domain': [('id','=',purchase.id)],
                'res_id': purchase.id,
        }
