from odoo import _, api, fields, models
from datetime import datetime,date

class StockLocation(models.Model):
    _inherit = 'stock.location'

    chemical_catridge_usage = fields.Float('Chemical Catridge Usage')
    cut_off = fields.Date('Cut Off')
    equipment_ids = fields.One2many('maintenance.equipment', 'location_id', string='Equipment')

class ChemicalCatridge(models.Model):
    _name = 'chemical.catridge'
    _description = 'Chemical Catridge'
    _order = 'date desc'

    product_id = fields.Many2one('product.product', string='Product/Chemical')
    warehouse_id = fields.Many2one('stock.location', string='Lokasi',domain=[("usage", "=", "internal")])
    date = fields.Date('Date',default=fields.Date.today)
    stock_awal = fields.Float('Stock Awal')
    penerimaan = fields.Float('Penerimaan')
    penuangan = fields.Float(string='Penuangan')
    pemakaian = fields.Float(string='Pemakaian',compute='_get_pemakaian')
    cleaning_basa = fields.Float('Pemakaian Cleaning Basa')
    adj_over_loss = fields.Float('Adjustment Over/(Loss)')
    dosing_stroke = fields.Float('Dosing Stoke')
    dosing_stroke_percent = fields.Float('Dosing Stoke (%)')
    sisa_stock = fields.Float(compute='_compute_sisa_stock', string='Sisa Stock',store=True)
    type = fields.Selection([('boo', 'BOO'),('oms', 'OMS')], string='type')
    sisa_tangki = fields.Integer('Sisa Tangki')
    sisa_tangki_kg = fields.Float(compute='_compute_sisa_tangki_kg', string='Sisa Tangki (kg)',store=True)
    
    @api.onchange('product_id','warehouse_id','date')
    def _onchange_product_id(self):
        for i in self:
            if i.product_id and i.warehouse_id and i.date:
                first_day = i.date.replace(day=1)
                # first_day = datetime.strptime(i.date, '%d %b %Y').replace(day=1)
                sisa_stock = self.env["chemical.catridge"].search([("product_id", "=", i.product_id.id),("warehouse_id", "=", i.warehouse_id.id),('date','<',i.date )],limit = 1, order = 'date desc')
                if sisa_stock:
                    i.stock_awal = sisa_stock.sisa_stock
            
    @api.depends('sisa_tangki_kg','date','warehouse_id','product_id')
    def _get_pemakaian(self):
        for i in self:
            if i.sisa_tangki_kg and i.date and i.warehouse_id and i.product_id:
                getyes = self.env["chemical.catridge"].search([("product_id", "=", i.product_id.id),("warehouse_id", "=", i.warehouse_id.id),('date','<',i.date ),('sisa_tangki_kg','>',0.0 )],limit = 1, order = 'date desc')
                if i.penuangan not in [0,False]:
                    i.pemakaian = getyes.sisa_tangki_kg
                else:
                    if getyes:
                        i.pemakaian = getyes.sisa_tangki_kg - i.sisa_tangki_kg
                    else:
                        i.pemakaian = 0
            else:
                i.pemakaian = 0
           

    @api.depends('sisa_tangki','product_id')
    def _compute_sisa_tangki_kg(self):
        for i in self:
            if i.sisa_tangki and i.warehouse_id:
                i.sisa_tangki_kg = i.sisa_tangki / 100 * i.warehouse_id.chemical_catridge_usage
            else:
                i.sisa_tangki_kg = 0


    @api.depends('stock_awal','penerimaan','penuangan','pemakaian','cleaning_basa','adj_over_loss','dosing_stroke')
    def _compute_sisa_stock(self):
        for i in self:
            i.sisa_stock = i.stock_awal + i.penerimaan - i.penuangan - i.cleaning_basa - i.adj_over_loss - i.dosing_stroke or 0

    