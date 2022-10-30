from odoo import _, api, fields, models

class TroubleMaster(models.Model):
    _name = 'trouble.master'
    _description = 'Trouble Master'
    
    name = fields.Text('Name')
    is_trouble = fields.Boolean('trouble')
    type = fields.Selection([('trouble', 'Input Trouble'),('cleaning', 'Request Cleaning'),('backwash', 'Backwash'), ('grease', 'Request Grease')], string='type')

    