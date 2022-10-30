import string
from odoo import models, fields, api
from dateutil import relativedelta

class ProjectProjectStage(models.Model):
    _inherit = 'project.project.stage'

    is_closed = fields.Boolean('End of stage')    

class ProjectTask(models.Model):
  _inherit = 'project.task'

  change_stage_time = fields.Datetime('Change Stage Time',store=True)
  duration_change_stage = fields.Char(string='Duration')
  attachment_ids = fields.One2many(string='Attachments')
  percentage_done = fields.Float(compute='_compute_percentage_done', string='Percentage')
  percentage_done_char = fields.Char(compute='_compute_percentage_done', string='Done Percentage')
  
  @api.depends('child_ids')
  def _compute_percentage_done(self):
    for i in self:
      n = len(i.child_ids.ids)
      done = len(i.child_ids.filtered(lambda x:x.stage_id.is_closed == True).ids)
      if n and done:
        p = done/n
        i.percentage_done = p
        i.percentage_done_char = str(round(p*100))+"%"
        round(2.676, 2)
      else:
        i.percentage_done_char = "0%"
        i.percentage_done = 0



  @api.onchange('stage_id')
  def _onchange_stagescrm_id(self):
    for i in self:
      i.change_stage_time = fields.datetime.now()
         

  # @api.depends('change_stage_time')
  def _compute_duration_change_stage(self):
    now = fields.datetime.now()
    for i in self:
      if i.change_stage_time:
        diff = relativedelta.relativedelta(i.change_stage_time, now)
        years = diff.years
        months = diff.months
        days = diff.days
        hours = diff.hours
        minutes = diff.minutes
        if years > 0:
          i.duration_change_stage = str(years) + " Tahun " + str(months) + " bulan " + str(days) + " Hari" + str(hours) + " jam " + str(minutes) + " menit"
        elif months > 0:
          i.duration_change_stage = str(months) + " Bulan " + str(days) + " hari " + str(hours) + " jam " + str(minutes) + " menit"
        elif days > 0:
          i.duration_change_stage = str(days) + " Hari " + str(hours) + " jam " + str(minutes) + " menit"
        elif hours > 0:
          i.duration_change_stage = str(hours) + " Jam " + str(minutes) + " menit"
        else:
          i.duration_change_stage =str(minutes) + " Menit " + str(diff.seconds) + " detik"
      else:
          i.duration_change_stage = 'The changes stage time is not defined!'
