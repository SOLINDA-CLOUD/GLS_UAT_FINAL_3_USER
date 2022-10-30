# -*- coding:utf-8 -*-
from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    bank_charge_account = fields.Many2one('account.account', string='Default Bank Charge Account', domain="[('company_id', '=', company_id)]")

    def get_values(self):
        res = super().get_values()
        res.update({
                        'bank_charge_account':
                            int(self.env['ir.config_parameter'].sudo().get_param('bank_charge_account'))or False,})
        return res

    def set_values(self):
        res = super().set_values()
        if self.bank_charge_account:
            self.env['ir.config_parameter'].sudo().set_param('bank_charge_account',
                                                                self.bank_charge_account.id or False)
        return res
