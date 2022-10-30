from odoo import _, api, fields, models
import collections
from odoo.exceptions import ValidationError

class AccountAnalyticAccount(models.Model):
    _inherit = 'account.analytic.account'

    @api.constrains('name')
    def _constrains_project_code(self):
        for this in self:
            data = self.env['account.analytic.account'].search([]).mapped('name')
            dup = len([item for item, count in collections.Counter(data).items() if count > 1])
            if dup > 0:
                raise ValidationError("Name Analytic Accounts Already Exist!")
    