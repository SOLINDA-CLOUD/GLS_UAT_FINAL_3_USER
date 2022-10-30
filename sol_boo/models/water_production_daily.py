from odoo import _, api, fields, models
from datetime import datetime,date
from dateutil import relativedelta
from odoo.exceptions import ValidationError

class CleaningConsumption(models.Model):
    _name = 'cleaning.consumption'
    _description = 'Cleaning Consumption'
    
    product_id = fields.Many2one('product.product', string='Material')
    consumption = fields.Float('Consumption')
    remarks = fields.Text('Remarks')
    shutdown_id = fields.Many2one('shutdown.system', string='Shutdown System')

class ShutdownSystem(models.Model):
    _name = 'shutdown.system'
    _description = 'Shutdown System'
    _inherit = 'mail.thread'
    _rec_name = 'trouble_id'

    trouble_id = fields.Many2one('trouble.master', string='Keterangan',tracking=True)
    time = fields.Datetime('Waktu', default=datetime.now(),tracking=True)
    end_time = fields.Datetime('Waktu Akhir', default=datetime.now(),tracking=True)
    # notes = fields.Text('Keterangan')
    jadwal_pelaksana = fields.Date('Jadwal Pelaksanaan',tracking=True)
    type = fields.Selection([
        ('trouble', 'Input Trouble'),
        ('cleaning', 'Cleaning'),
        ('backwash', 'Backwash'),
        ('grease', 'Grease')
    ], string='type',related="trouble_id.type",tracking=True,store=True)
    state = fields.Selection([
        ('draft', 'Draft'),
        ('approve', 'Approved'),
        ('done', 'Done')
    ], string='Status',default="draft",tracking=True)
    attachment = fields.Binary('Upload')
    filename = fields.Char('File Name',tracking=True)
    request_id = fields.Many2one('res.users', string='Requested By',tracking=True)
    approve_id = fields.Many2one('res.users', string='Approved By',tracking=True)
    job_order_id = fields.Many2one('job.order.request', string='Job Order',tracking=True)
    water_prod_id = fields.Many2one('water.prod.daily', string='Water Production',tracking=True)
    warehouse_id = fields.Many2one('stock.location', string='Lokasi',related="water_prod_id.warehouse_id",tracking=True,store=True)
    is_trouble = fields.Boolean('Trouble',related="trouble_id.is_trouble",tracking=True,store=True)
    trouble_minute = fields.Float(compute='_compute_trouble_minute', string='Trouble Minute',tracking=True)
    maintenance_id = fields.Many2one('maintenance.request', string='Maintenance')
    state_maintenance = fields.Char('State Maintenance',related="maintenance_id.stage_id.name")
    frek_cleaning = fields.Float('Frekuensi Cleaning')
    cleaning_consumption_ids = fields.One2many('cleaning.consumption', 'shutdown_id', string='Cleaning Consumption')
    grease_usage = fields.Float('Grease Usage(gr)',tracking=True)
    mr_ids = fields.One2many('stock.picking', 'shutdown_id', string='MR')
    mr_count = fields.Integer(compute='_compute_mr_count', string='Mr')
    
    @api.depends('mr_ids')
    def _compute_mr_count(self):
        for i in self:
            i.mr_count = len(i.mr_ids)

    def create_open_mr(self):
         return {
                'name': 'Material Request',
                'type': 'ir.actions.act_window',
                'view_mode': 'tree,kanban,form,calendar,map',
                'res_model': 'stock.picking',
                'context': {'default_company_id': self.env.company.id,'default_shutdown_id':self.id},
                'domain': [('shutdown_id','=',self.id)],
            }

    def create_open_maintenance(self):
        for i in self:
            i.ensure_one()
            if i.maintenance_id:
                return {
                        'name': 'Maintenance Request',
                        'type': 'ir.actions.act_window',
                        'view_mode': 'form',
                        'res_model': 'maintenance.request',
                        'res_id': i.maintenance_id.id,
                        'context': {'create': False}
                    }
            else:
                maintenance = self.env["maintenance.request"].create({
                            'name': i.type + '...',
                            'description': i.trouble_id.name,
                            'shutdown_id':i.id,
                            'location_id':i.warehouse_id.id
                            })
                if maintenance:
                    i.maintenance_id = maintenance.id
                    return {
                    'name': 'Maintenance Request',
                    'type': 'ir.actions.act_window',
                    'view_mode': 'form',
                    'res_model': 'maintenance.request',
                    'res_id': maintenance.id,
                    }

    def state_done(self):
        self.state = 'done'

    def confirm_backwash(self):
        for i in self:
            if i.type and i.filename:
                i.state_done()
            else:
                raise ValidationError('Attachment not upload yet.\nPlease upload first!')

    @api.onchange('type')
    def _onchange_type(self):
        if self.type == 'trouble':
            self.is_trouble = True

    def approve_button(self):
        for i in self:
            i.state = 'approve'

    @api.depends('time','end_time')
    def _compute_trouble_minute(self):
        for i in self:
            if i.time and i.end_time:
                c = i.end_time - i.time
                minutes = divmod(c.total_seconds(), 60) 
                i.trouble_minute = minutes[0]
            else:
                i.trouble_minute = 0

    def open_self_record(self):
        return {
                    'name': 'Request',
                    'type': 'ir.actions.act_window',
                    'view_mode': 'form',
                    'res_model': 'shutdown.system',
                    'res_id': self.id,
                    'context': {'create': False}
                }

    def create_open_job_order(self):
        for i in self:
            i.ensure_one()
            if i.job_order_id:
                return {
                        'name': 'Job Order Request',
                        'type': 'ir.actions.act_window',
                        'view_mode': 'form',
                        'res_model': 'job.order.request',
                        'res_id': i.job_order_id.id,
                        'context': {'create': False}
                    }
            else:
                job_order = self.env["job.order.request"].create({
                            'state': 'draft',
                            'warehouse_id': i.warehouse_id.id,
                            'problem': i.trouble_id.name,
                            })
                if job_order:
                    i.job_order_id = job_order.id
                    return {
                    'name': 'Job Order Request',
                    'type': 'ir.actions.act_window',
                    'view_mode': 'form',
                    'res_model': 'job.order.request',
                    'res_id': job_order.id,
                    }


class WaterProdDaily(models.Model):
    _name = 'water.prod.daily'
    _description = 'Water Prod Daily'
    _inherit = 'mail.thread'
    _order = 'date desc'

    # IRISAN
    name = fields.Char('Name',tracking=True)
    date = fields.Date('Date',default=fields.Date.today,tracking=True)
    warehouse_id = fields.Many2one('stock.location',domain=[("usage", "=", "internal")],string='Lokasi',tracking=True)

    # HARIAN
    # laguna = fields.Char('Laguna',tracking=True)
    # target_prod = fields.Integer('Target Produksi',tracking=True)
    # kontrak_boo = fields.Integer('Berdasarkan Kontrak BOO',default=450,tracking=True)
    # adjustment_prod = fields.Integer('Penyesuaian Produksi',tracking=True)
    # adendum = fields.Integer('Adendum',tracking=True)
    # now_prod = fields.Float('Produksi Sekarang',tracking=True)
    # over_target = fields.Float('Produksi Melebihi Target',compute="_compute_over_target",store=True,tracking=True)
    # freq_hpp = fields.Integer('Frekuensi HPP',tracking=True)
    # flow_prod = fields.Integer('Flow Produksi',tracking=True)
    # catatan = fields.Text('Catatan',tracking=True)

    # PEKANAN DAN BULANAN
    aktual_ro = fields.Float('Konsumsi Aktual Ro(m3)',tracking=True,compute="_get_actual_ro")
    ro_read = fields.Integer('Ro Read')
    lwbp = fields.Integer('LWBP',tracking=True,compute='_get_lwbp')
    lwbp_read = fields.Float('LWBP read',tracking=True)
    wbp = fields.Integer(string='WBP',tracking=True,compute='_get_wbp')
    wbp_read = fields.Float('WBP read',tracking=True)
    sec = fields.Float('SEC',tracking=True,compute="_ge_sec")
    deep_well_read = fields.Float('kWh Deep WEll Read',)
    deep_well = fields.Float('Deep Well (kWh)',compute="_get_well")
    kwh_ro_read = fields.Float('kWh RO Read')
    ro_kwh = fields.Float('RO (kWh)',compute="_get_ro_kwh")
    minimum_prod = fields.Integer('Minimum Produksi',tracking=True)
    hasil_prod = fields.Float('Hasil Produksi',tracking=True)
    remarks = fields.Text('Remarks',tracking=True)
    water_prod_id = fields.Many2one('water.prod.daily', string='water_prod',tracking=True)
    saidi = fields.Float('Saidi (minute)',compute="_compute_saidi_saifi",digit=(0,0))
    saifi = fields.Integer('Saifi',compute="_compute_saidi_saifi")
    
    # LINE
    shutdown_system_line = fields.One2many('shutdown.system', 'water_prod_id', string='Shutdown System')

    @api.depends('wbp','lwbp','aktual_ro','deep_well','ro_kwh')
    def _ge_sec(self):
        for i in self:
            summary = i.lwbp + i.wbp + i.deep_well + i.ro_kwh
            if summary != 0:
                i.sec = (summary) / i.aktual_ro
            else:
                i.sec = 0

    @api.depends('kwh_ro_read','warehouse_id','date')
    def _get_ro_kwh(self):
        for i in self:
            if i.warehouse_id and i.date:
                deep_well = self.env["water.prod.daily"].search([("warehouse_id", "=", i.warehouse_id.id),('date','=',i.date - relativedelta.relativedelta(days=1))]).kwh_ro_read
                if deep_well:
                    i.ro_kwh = (i.kwh_ro_read - deep_well)
                else:
                    i.ro_kwh = 0
            else:
                i.ro_kwh = 0

    @api.depends('deep_well_read','warehouse_id','date')
    def _get_well(self):
        for i in self:
            if i.warehouse_id and i.date:
                deep_well = self.env["water.prod.daily"].search([("warehouse_id", "=", i.warehouse_id.id),('date','=',i.date - relativedelta.relativedelta(days=1))]).deep_well_read
                if deep_well:
                    i.deep_well = (i.deep_well_read - deep_well)
                else:
                    i.deep_well = 0
            else:
                i.deep_well = 0

    @api.depends('wbp_read','warehouse_id','date')
    def _get_wbp(self):
        for i in self:
            if i.warehouse_id and i.date:
                wbp_yes = self.env["water.prod.daily"].search([("warehouse_id", "=", i.warehouse_id.id),('date','=',i.date - relativedelta.relativedelta(days=1))]).wbp_read
                if wbp_yes:
                    i.wbp = (i.wbp_read - wbp_yes)
                    # i.wbp = (i.wbp_read - wbp_yes) * 2000
                else:
                    i.wbp = 0
            else:
                i.wbp = 0
    
    @api.depends('lwbp_read','warehouse_id','date')
    def _get_lwbp(self):
        for i in self:
            if i.warehouse_id and i.date:
                lwbp_yes = self.env["water.prod.daily"].search([("warehouse_id", "=", i.warehouse_id.id),('date','=',i.date - relativedelta.relativedelta(days=1))]).lwbp_read
                if lwbp_yes:
                    i.lwbp = (i.lwbp_read - lwbp_yes)
                    # i.lwbp = (i.lwbp_read - lwbp_yes) * 2000
                else:
                    i.lwbp = 0
            else:
                i.lwbp = 0

    @api.depends('ro_read','warehouse_id','date')
    def _get_actual_ro(self):
        for i in self:
            if i.warehouse_id and i.date:
                ro_yesterday = self.env["water.prod.daily"].search([("warehouse_id", "=", i.warehouse_id.id),('date','=',i.date - relativedelta.relativedelta(days=1))]).ro_read
                if ro_yesterday:
                    i.aktual_ro = i.ro_read - ro_yesterday
                else:
                    i.aktual_ro = 0
            else:
                i.aktual_ro = 0

    

    @api.depends('shutdown_system_line.is_trouble','shutdown_system_line.time','shutdown_system_line.end_time')
    def _compute_saidi_saifi(self):
        for i in self:
            i.saifi = i.shutdown_system_line.mapped('is_trouble').count(True)
            i.saidi = sum(l.trouble_minute for l in i.shutdown_system_line if l.is_trouble)

    def _compute_over_target(self):
        for i in self:
            if i.target_prod and i.now_prod:
                i.over_target = i.now_prod - i.target_prod
            else:
                i.over_targer = 0

    @api.model
    def create(self, vals):
        res = super(WaterProdDaily, self).create(vals)
        res.name = self.env["ir.sequence"].next_by_code("wpd.seqcode")
        return res 