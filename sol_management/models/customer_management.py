from audioop import reverse
from odoo import models, fields, api
from odoo.exceptions import ValidationError

class CustomerManagement(models.Model):
    _name = 'customer.management'
    _description = 'Customer Management'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'name desc'
    _rec_name = 'name'

    name = fields.Char('Document number', default='/', readonly='True', copy=False)
    point = [
        ('0', 'New Customer'),
        ('1', 'Bad'),
        ('2', 'Satisfied'),
        ('3', 'Excellent')

    ]

    state = fields.Selection([
        ('draft', 'Draft'), 
        ('request', 'Request Approval'), 
        ('approved', 'Approved'),
        ('rejected', 'Rejected'), 
        ('cancelled', 'Cancelled')], 
        string='State', default="draft", track_visibility='onchange')

    def draft_request(self):
        for rec in self:
            rec.state = 'request'
        self.calculate()

    def request_draft(self):
        for rec in self:
            rec.state = 'draft'

    def request_approved(self):
        for rec in self:
            rec.state = 'approved'

    def request_rejected(self):
        for rec in self:
            rec.state = 'rejected'

    def approved_cancelled(self):
        for rec in self:
            rec.state = 'cancelled'

    customer = fields.Many2one('res.partner', string="Customer Name", required=True, ondelete='cascade', readonly=True, states={'draft': [('readonly', False)]})
    email = fields.Char('Email', readonly=True, states={'draft': [('readonly', False)], 'request': [('readonly', False)]})
    business_name = fields.Char('Business Name', readonly=True, states={'draft': [('readonly', False)], 'request': [('readonly', False)]})
    date = fields.Date('Start Date', default=lambda self: fields.Date.today(), readonly=True, states={'draft': [('readonly', False)], 'request': [('readonly', False)]})
    period_start = fields.Date('Review Period', required=True, readonly=True, states={'draft': [('readonly', False)]})
    period_end = fields.Date(required=True, readonly=True, states={'draft': [('readonly', False)]})
    manager = fields.Many2one('res.users', string="Manager", required=True, readonly=True, states={'draft': [('readonly', False)]})
    is_manager = fields.Boolean(compute='check_manager')
    user_id = fields.Many2one('res.users', 'Current User', compute='_get_current_user')

    def _get_current_user(self):
        self.user_id = self.env.uid

    @api.depends('manager')
    def check_manager(self):
        for rec in self:
            if rec.manager.id == rec.user_id.id:
                rec.is_manager = True
            else:
                rec.is_manager = False

    @api.onchange('customer')
    def _onchange_email_customer(self):
        self.email = self.customer.email
    
    _sql_constraints = [
        ('period_constraint', 'CHECK(period_start <= period_end)', 'End Period can not be lower than Start Period!'),
        ('name_unique', 'unique(name)', "Document number must be unique!")
    ]

    ## Customer Eval 1
    price_eval = fields.Boolean(string='1. Omset', readonly=True, states={'draft': [('readonly', False)]},
                help='> Rp. 1.000.000.000(4), Rp. 500.000.000 - Rp. 1.000.000.000(3), < Rp. 500.000.000(2)')
    price_score = fields.Integer(string='Score', readonly=True, states={'draft': [('readonly', False)]})
    price = fields.Selection(point, string='Rate', default=point[0][0], readonly=True, states={'draft': [('readonly', False)]})
    price_comment = fields.Char(string='Comment', readonly=True, states={'draft': [('readonly', False)]})

    @api.constrains('price_score', 'price')
    def criteria_price(self):
        for rec in self:
            if rec.price_eval and rec.price_score > 4:
                raise ValidationError('Score of Customer eval no 1 must be 2 until 4!')
            if rec.price_eval and rec.price_score < 2:
                raise ValidationError('Score of Customer eval no 1 must be 2 until 4!')
            if rec.price_eval and not rec.price:
                raise ValidationError('Customer eval no 1 has not evaluated yet!')
    
    ## Customer Eval 2
    terms_eval = fields.Boolean(string='2. History of Payment', readonly=True, states={'draft': [('readonly', False)]},
                help='Ontime(4), Overdue < 2 month(3), Overdue < 4 month(2)')
    terms_score = fields.Integer(string='Score', readonly=True, states={'draft': [('readonly', False)]})
    terms = fields.Selection(point, string='Rate', default=point[0][0], readonly=True, states={'draft': [('readonly', False)]})
    terms_comment = fields.Char(string='Comment', readonly=True, states={'draft': [('readonly', False)]})

    @api.constrains('terms_score', 'terms')
    def criteria_terms(self):
        for rec in self:
            if rec.terms_eval and rec.terms_score > 4:
                raise ValidationError('Score of Customer eval no 2 must be 2 until 4!')
            if rec.terms_eval and rec.terms_score < 2:
                raise ValidationError('Score of Customer eval no 2 must be 2 until 4!')
            if rec.terms_eval and not rec.terms:
                raise ValidationError('Customer eval no 2 has not evaluated yet!')

    ## Customer Eval 3
    items_eval = fields.Boolean(string='3. Communication', readonly=True, states={'draft': [('readonly', False)]},
                help='Fast(3), Slow(2), Too Slow(1)')
    items_score = fields.Integer(string='Score', readonly=True, states={'draft': [('readonly', False)]})
    items = fields.Selection(point, string='Rate', default=point[0][0], readonly=True, states={'draft': [('readonly', False)]})
    items_comment = fields.Char(string='Comment', readonly=True, states={'draft': [('readonly', False)]})

    @api.constrains('items_score', 'items')
    def criteria_items(self):
        for rec in self:
            if rec.items_eval and rec.items_score > 3:
                raise ValidationError('Score of Customer eval no 3 must be 1 until 3!')
            if rec.items_eval and rec.items_score < 1:
                raise ValidationError('Score of Customer eval no 3 must be 1 until 3!')
            if rec.items_eval and not rec.items:
                raise ValidationError('Customer eval no 3 has not evaluated yet!')

    ## Customer Eval 4
    accuracy_eval = fields.Boolean(string='4. Company Image', readonly=True, states={'draft': [('readonly', False)]},
                    help='Big(3), Moderate(2), Small(1)')
    accuracy_score = fields.Integer(string='Score', readonly=True, states={'draft': [('readonly', False)]})
    accuracy = fields.Selection(point, string='Rate', default=point[0][0], readonly=True, states={'draft': [('readonly', False)]})
    accuracy_comment = fields.Char(string='Comment', readonly=True, states={'draft': [('readonly', False)]})

    @api.constrains('accuracy_score', 'accuracy')
    def criteria_accuracy(self):
        for rec in self:
            if rec.accuracy_eval and rec.accuracy_score > 3:
                raise ValidationError('Score of Customer eval no 4 must be 1 until 3!')
            if rec.accuracy_eval and rec.accuracy_score < 1:
                raise ValidationError('Score of Customer eval no 4 must be 1 until 3!')
            if rec.accuracy_eval and not rec.accuracy:
                raise ValidationError('Customer eval no 4 has not evaluated yet!')

    ##Management Report
    final_score = fields.Float(readonly=True, store=True, string='Final Score')
    final_rate_cust = fields.Selection(point, readonly=True, string='Final Rate')
    final_comment = fields.Char(string='Final Comment', states={'cancelled': [('readonly', True)]})

    def calculate(self):
        for rec in self:
            count = 0
            sum_total = 0
            if rec.price_eval:
                count += rec.price_score
                sum_total += (int(rec.price) * rec.price_score)
            if rec.terms_eval:
                count += rec.terms_score
                sum_total += (int(rec.terms) * rec.terms_score)
            if rec.items_eval:
                count += rec.items_score
                sum_total += (int(rec.items) * rec.items_score)
            if rec.accuracy_eval:
                count += rec.accuracy_score
                sum_total += (int(rec.accuracy) * rec.accuracy_score)
            if count == 0:
                rec.final_rate_cust = rec.point[0][0]
            if count >= 6 and count <= 9:
                rec.final_rate_cust = rec.point[1][0]
            if count >= 10 and count <= 12:
                rec.final_rate_cust = rec.point[2][0]
            if count >= 13 and count <=20:
                rec.final_rate_cust = rec.point[3][0]
            if count == 0:
                rec.final_rate_cust = rec.point[0][0]
            else:
                rec.final_score = count

    
    def unlink(self):
        for rec in self:
            if rec.state != 'draft':
                raise ValidationError('You can not delete record when status is not draft')
        return super(CustomerManagement, self).unlink()

    @api.model
    def create(self, vals):
        rec = super(CustomerManagement, self).create(vals)
        number = self.env['ir.sequence'].next_by_code('customer_managemnet_seq')
        rec.name = number
        rec.calculate()
        return rec

    # def write(self, vals):
    #     rec = super(CustomerManagement, self).write(vals)
    #     if 'final_score' not in vals and 'final_rate_cust' not in vals:
    #         self.calculate()
    #     return rec

# class CustomerAdd(models.Model):
#     _inherit = 'res.partner'

#     visible_management_cust = fields.Selection(CustomerManagement.point, string='Last Management', compute='_calculate_eval', readonly=True)

#     @api.depends()
#     def _calculate_eval(self):
#         for rec in self:
#             record = self.env['customer.management'].search([
#                 ('customer', '=', rec.id),
#                 ('state', '=', 'approved')
#             ])
#             if record:
#                 rec.visible_management_cust = record.sorted('period_end', reverse=True)[0].final_rate_cust 
#             else:
#                 rec.visible_management_cust = False

