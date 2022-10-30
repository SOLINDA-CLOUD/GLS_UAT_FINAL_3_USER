from odoo import _, api, fields, models

class RequestMaintenance(models.Model):
    _name = 'request.maintenance'
    _description = 'Request Maintenance'
    
    name = fields.Char('Name')
    type = fields.Selection([
        ('trouble', 'Input Trouble'),
        ('cleaning', 'Request Cleaning'),
        ('backwash', 'Backwash'),
        ('grease', 'Request Grease')
    ], string='type')
    create_date = fields.Date('Create Date',default=fields.Date.today)
    state = fields.Selection([
        ('draft', 'Draft'),
        ('req', 'Requested'),
        ('approve', 'Approved'),
    ], string='State')
    attachment = fields.Binary('Attachment')
    filename = fields.Char('File Name')