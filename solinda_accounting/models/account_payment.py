from odoo import models, fields, api

class AccountPayment(models.TransientModel):
    _inherit = 'account.payment.register'

