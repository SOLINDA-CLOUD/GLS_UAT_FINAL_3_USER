# -*- coding: utf-8 -*-

from odoo import models, fields, api


class PurchaseRequisition(models.Model):
    _inherit = 'purchase.requisition'

    name_project = fields.Char(string='Name Project')
    need_category = fields.Selection([
        ('project', 'Project'),
        ('operational', 'Operational'),
        ('maintenance', 'Maintenance'),
        ('trading', 'Trading'),
        ('bidding', 'Bidding')
    ], string='Need Category')
    
    
    @api.model
    def create(self, vals):
        vals['name'] = self.env['ir.sequence'].next_by_code('purchase.requisition.req')
        return super(PurchaseRequisition, self).create(vals)

class DeliveryLocation(models.Model):
    _name = 'delivery.location'
    _description = 'Delivery Location'

    name = fields.Char(string='Delivery Location')

class PurchaseRequisitionLine(models.Model):
    _inherit = 'purchase.requisition.line'

    merk_recommended = fields.Char(string='Merk Recommended')
    price_target = fields.Float('Price Target')
    date_plan_required = fields.Date('Date Plan Required')
    delivery_location_id = fields.Many2one(string='Delivery Location', comodel_name='delivery.location', ondelete='restrict')
    product_description_variants = fields.Text(string='Custom Description', readonly=True)

    @api.onchange('product_id')
    def _onchange_product_id(self):
        if self.product_id:
            product_description_variants = ''
            # if self.product_id.code:
            #     product_description_variants = "[{}] {}".format(self.product_id.default_code, product_description_variants)
            if self.product_id.type_pur:
                product_description_variants += "type : " + self.product_id.type_pur + ";"
            if self.product_id.debit:
                product_description_variants += "\n" + "debit : " + self.product_id.debit + ";"
            if self.product_id.head:
                product_description_variants += "\n" + "head : " + self.product_id.head + ";"
            if self.product_id.voltage:
                product_description_variants += "\n" + "voltage : " + self.product_id.voltage + ";"
            if self.product_id.casing:
                product_description_variants += "\n" + "material casing : " + self.product_id.casing + ";"
            if self.product_id.impeller:
                product_description_variants += "\n" + "material impeller : " + self.product_id.impeller + ";"
            self.product_uom_id = self.product_id.uom_id.id
            self.product_description_variants = product_description_variants

class ProductProduct(models.Model):
    _inherit = 'product.product'

class ProductTemplate(models.Model):
    _inherit = 'product.template'

    type_pur = fields.Char(string='Type')
    debit = fields.Char(string='Debit')
    head = fields.Char(string='Head')
    voltage = fields.Char(string='Voltage')
    casing = fields.Char(string='Casing')
    impeller = fields.Char(string='Impeller')

class PurchaseOrderLine(models.Model):
    _inherit ='purchase.order.line'

    project_code_po = fields.Char(string='Project Code', store=True)

class PurchaseRequest(models.Model):
    _inherit = 'purchase.request'

    def _purchase_request(self, sequence=False):
        res = super(PurchaseRequest, self)._purchase_request()
        res.update({
            'project_code_po': self.project_code
            })
        return res

class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'
    READONLY_STATES = {
        'purchase': [('readonly', True)],
        'done': [('readonly', True)],
        'cancel': [('readonly', True)],
    }

    name = fields.Char(string='Order Reference')
    notes = fields.Html(string='Notes')
    courier = fields.Char('Courier')
    # locatioC_id = fields.Many2one('stock.location', string='Location',related="picking_type_id.default_location_dest_id")
    location_id = fields.Many2one('stock.location', string='Location')
    state = fields.Selection([
        ('draft', 'RFQ'),
        ('submit', 'Submitted'),
        ('confirm', 'Confirmed'),
        ('sent', 'RFQ Sent'),
        ('to approve', 'To Approve'),
        ('purchase', 'Purchase Order'),
        ('done', 'Locked'),
        ('cancel', 'Cancelled')
    ], string='Status', readonly=True, index=True, copy=False, default='draft', tracking=True)
    # currency_id = fields.Many2one('res.currency', 'Currency', required=True, states=READONLY_STATES, related="partner_id.property_purchase_currency_id")

    @api.onchange('partner_id')
    def _onchange_partner_id_change_currency(self):
        for i in self:
            if i.partner_id:
                i.currency_id = i.partner_id.property_purchase_currency_id
            else:
                i.currency_id = False


    @api.depends('date_order', 'currency_id', 'company_id', 'company_id.currency_id')
    def _compute_currency_rate(self):
        for order in self:
            if order.currency_id == order.company_id.currency_id:
                order.currency_rate = 0
            else:
                order.currency_rate = self.env['res.currency']._get_conversion_rate(order.company_id.currency_id, order.currency_id, order.company_id, order.date_order)


    def button_confirm(self):
        for order in self:
            if order.state not in ['draft', 'sent','confirm']:
                continue
            order._add_supplier_to_product()
            # Deal with double validation process
            if order._approval_allowed():
                order.button_approve()
            else:
                order.write({'state': 'to approve'})
            if order.partner_id not in order.message_partner_ids:
                order.message_subscribe([order.partner_id.id])
        return True

    def submit_purchase(self):
        # Purchasing Staff
        self.write({'state': 'submit'})

    def confirm_purchase(self):
        # Procurement Manager
        self.write({'state': 'confirm'})


    @api.model
    def create(self, vals):
        vals['name'] = self.env['ir.sequence'].next_by_code('purchase.order.req')
        return super(PurchaseOrder, self).create(vals)

    @api.model
    def _prepare_picking(self):
        vals = super(PurchaseOrder, self)._prepare_picking()
        vals.update({
            'location_dest_id': self.location_id.id
            })
        return vals