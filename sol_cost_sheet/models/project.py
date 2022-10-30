from random import random
from odoo import _, api, fields, models
from odoo.exceptions import ValidationError, UserError

class ProjectProjectStage(models.Model):
    _inherit = 'project.project.stage'

    is_closed = fields.Boolean('End of stage')    

class ProjectTask(models.Model):
    _inherit = 'project.task'
    _description = 'Project Task'
    
    @api.onchange('stage_id')
    def _onchange_stage_id(self):
        for i in self:
            # if i.stage_id.is_closed and i.env.user.id != i.manager_id.id:
            if i.env.user.id != i.manager_id.id:
                raise ValidationError("Only project manager can change stage into done!")

class ProjectProject(models.Model):
    _inherit = 'project.project'

    rab_id = fields.Many2one('cost.sheet',related='sale_order_id.rab_id', string='RAB',store=True)
    code = fields.Char('Project Code')
    # code = fields.Char('Project Code',related="sale_order_id.rab_id.project_code")
    rap_id = fields.Many2one('rap.rap', string='RAP')
    project_cost_account_id = fields.Many2one('account.account', string='Project Cost')
    project_onprogress_account_id = fields.Many2one('account.account', string='Project On Progress')

    # purchase_id = fields.Many2one('purchase.requisition', string='RAP')

    def write(self, vals):
        for i in self:
            if vals.get("stage_id"):
                # if i.stage_id.is_closed and i.env.user.id != i.user_id.id:
                if i.env.user.id != i.user_id.id:
                    raise ValidationError("Only project manager can change stage into done!")
                if i.rap_id and i.stage_id.is_closed:
                    i.rap_id.state = 'close'
        return super(ProjectProject, self).write(vals)


    @api.onchange('stage_id')
    def _onchange_stage_project_id(self):
        for i in self:
            # if i.stage_id.is_closed and i.env.user.id != i.user_id.id:
            if i.env.user.id != i.user_id.id:
                raise ValidationError("Only project manager can change stage into done!")
            if i.rap_id and i.stage_id.is_closed:
                i.rap_id.state = 'close'

    def create_rap(self):
        rap = self.env['rap.rap'].create({
                'date_document': fields.Date.today(),
                'partner_id': self.rab_id.partner_id.id,
                # 'crm_id': self.rab_id.crm_id.id,
                'project_id': self.id,
                'category_line_ids': [(0,0,{
                    'cost_sheet_id': self.rab_id.id,
                    'rab_category_id': rab.id,
                    'product_id': rab.product_id.id,
                    'rab_price': rab.price,
                    # 'product_qty':
                    'price_unit': rab.price
                
                }) for rab in self.rab_id.category_line_ids]
        })
        
        for category in self.rab_id.category_line_ids:
            for component in category.parent_component_line_ids:
                category_rap = [i for i in rap.category_line_ids if i.rab_category_id.id == category.id]
                component.write({
                    'rap_category_id': category_rap[0] if category_rap else False,
                    'rap_id': rap.id
                })
                for item in component.item_ids:
                    item.write({
                    'rap_category_id': category_rap[0] if category_rap else False,
                    'rap_id': rap.id
                    })
        
        self.write({'rap_id':rap.id})
        self.rab_id.ga_project_line_ids.write({'rap_id':rap.id})
        self.rab_id.waranty_line_ids.write({'rap_id':rap.id})
        # self.rap_id = rap.id
        
        return {
            "type": "ir.actions.act_window",
            "view_mode": "form",
            "res_model": "rap.rap",
            "res_id": rap.id
        }

    
