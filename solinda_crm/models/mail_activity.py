# action_feedback
from odoo import _, api, fields, models
from odoo.tools.misc import clean_context


class MailActivity(models.Model):
    _inherit = 'mail.activity'
    
    
    def action_feedback(self, feedback=False, attachment_ids=None):
        if self.res_model == 'crm.lead':
            crm_id = self.env[self.res_model].browse(self.res_id)
            progress = self.activity_type_id.progress * 100
            crm_id.probability += progress
            
        res = super().action_feedback(feedback=False, attachment_ids=None)
        
        return res
        