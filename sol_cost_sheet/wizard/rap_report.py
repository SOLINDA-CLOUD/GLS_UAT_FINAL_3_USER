from odoo import _, api, fields, models

class RapReportWizard(models.TransientModel):
    _name = 'rap.report.wizard'
    _description = 'Rap Report Wizard'
    

    api.depends('project_ids')
    def _compute_project_name(self):
        n = ''
        for i in self.project_ids:
            n += i.name
        self.name = n

    def download_xlsx_report(self):
        template_report = 'sol_cost_sheet.action_rap_report'
        return self.env.ref(template_report).report_action(self)

    project_ids = fields.Many2many('project.project', string='Project')
    name = fields.Char(string='Name', compute= _compute_project_name)