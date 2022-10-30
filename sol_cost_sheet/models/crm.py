from odoo import _, api, fields, models
import collections
from odoo.exceptions import ValidationError

class CrmLead(models.Model):
    _inherit = 'crm.lead'
    # _sql_constraints = [('project_code_must_uniq', 'unique(project_code)', 'Project Code Must Be Unique!')]
    
    rab_id = fields.Many2one('cost.sheet', string='RAB')
    project_code = fields.Char('Project Code',tracking=True)
    
    @api.constrains('project_code')
    def _constrains_project_code(self):
        for this in self:
            data = self.env['crm.lead'].search([]).mapped('project_code')
            dup = len([item for item, count in collections.Counter(data).items() if count > 1 and item])
            if dup > 0:
                raise ValidationError("Project Code Already Exist!")

    def action_new_quotation(self):
        action = self.env["ir.actions.actions"]._for_xml_id("sale_crm.sale_action_quotations_new")
        action['context'] = {
            'search_default_opportunity_id': self.id,
            'default_opportunity_id': self.id,
            'search_default_partner_id': self.partner_id.id,
            'default_partner_id': self.partner_id.id,
            'default_campaign_id': self.campaign_id.id,
            'default_medium_id': self.medium_id.id,
            'default_origin': self.name,
            'default_project_code': self.project_code,
            'default_source_id': self.source_id.id,
            'default_company_id': self.company_id.id or self.env.company.id,
            'default_tag_ids': [(6, 0, self.tag_ids.ids)]
        }
        if self.team_id:
            action['context']['default_team_id'] = self.team_id.id,
        if self.user_id:
            action['context']['default_user_id'] = self.user_id.id
        return action