from odoo import api, fields, models, _
from odoo.exceptions import UserError

class AccountAsset(models.Model):
    _inherit = 'account.asset'

    def action_asset_pause(self):
        raise UserError("You're about to pause the Depreciation")
        """ Returns an action opening the asset pause wizard."""
        self.ensure_one()
        new_wizard = self.env['account.asset.pause'].create({
            'asset_id': self.id,
        })
        return {
            'name': _('Pause Asset'),
            'view_mode': 'form',
            'res_model': 'account.asset.pause',
            'type': 'ir.actions.act_window',
            'target': 'new',
            'res_id': new_wizard.id,
        }
