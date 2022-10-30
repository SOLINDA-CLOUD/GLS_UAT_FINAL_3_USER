from odoo import api, models, fields

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    # Report OMS
    subject = fields.Char(string="Subject")
    attn_id = fields.Many2one('res.partner', string='Attn')
    email = fields.Char(related='attn_id.email', store=True)
    supervisor = fields.Many2one('res.partner', string='Supervisor')
    office = fields.Char(related='supervisor.street', store=True)
    items_oms = fields.Many2one('product.product', string="Item", help='Untuk report Quotation OMS')

    # Terms and Conditions
    quotation_validity = fields.Char(string='Quotation Validity')
    delivery_time = fields.Char(string='Delivery Time')
    delivery_point = fields.Char(string='Delivery Point')
    price_tnc = fields.Html(string='Price')
    payment_terms = fields.Html(string='Payment Terms and Requirements')
    revitalization_period = fields.Char(string='Revitalization Period')

    # Additional Shipment
    courier = fields.Char(string="Ship Via")
    fob = fields.Char(string="FOB")
    estimated_freight = fields.Float(string="Estimated Freight")
    ship_to = fields.Many2one('res.partner', string='Ship To')
    ship_address = fields.Char(related='ship_to.street', store=True)
    # BOO 
    periode = fields.Char(string='Period')
    # Supports #
    supervisor_boo = fields.Char(string='Supervisor')
    engineer = fields.Char(string='Engineer')
    office_boo = fields.Char(string='Office')
    operator = fields.Char(string='Operator')
    # Responsibilty Centre #
    president_director = fields.Char('President Director')
    director = fields.Char('Director')
