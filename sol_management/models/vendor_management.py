from audioop import reverse
from odoo import models, fields, api
from odoo.exceptions import ValidationError

class VendorManagement(models.Model):
    _name = 'vendor.management'
    _description = 'Vendor Management'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'name desc'
    _rec_name = 'name'

    name = fields.Char('Document number', default='/', readonly='True', copy=False)
    point = [
        ('0', 'Not Good'),
        ('1', 'Bad'),
        ('2', 'Not Bad'),
        ('3', 'Satisfied'),
        ('4', 'Great'),
        ('5', 'Excellent')
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

    vendor = fields.Many2one('res.partner', string="Vendor Name", required=True, ondelete='cascade', readonly=True, states={'draft': [('readonly', False)]})
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

    @api.onchange('vendor')
    def _onchange_email_vendor(self):
        self.email = self.vendor.email
    
    _sql_constraints = [
        ('period_constraint', 'CHECK(period_start <= period_end)', 'End Period can not be lower than Start Period!'),
        ('name_unique', 'unique(name)', "Document number must be unique!")
    ]

    ## Customer Eval 1
    price_eval = fields.Boolean(string='1. Pricing', readonly=True, states={'draft': [('readonly', False)]},
                help='Most Competitive(4), 5%(3), 10%(2), More than 10%(1)')
    price_score = fields.Integer(string='Score', readonly=True, states={'draft': [('readonly', False)]})
    price = fields.Selection(point, string='Rate', default=point[0][0], readonly=True, states={'draft': [('readonly', False)]})
    price_comment = fields.Char(string='Comment', readonly=True, states={'draft': [('readonly', False)]})

    @api.constrains('price_score', 'price')
    def criteria_price(self):
        for rec in self:
            if rec.price_eval and rec.price_score > 4:
                raise ValidationError('Score of Vendor eval no 1 must be 1 until 4!')
            if rec.price_eval and rec.price_score < 1:
                raise ValidationError('Score of Vendor eval no 1 must be 1 until 4!')
            if rec.price_eval and not rec.price:
                raise ValidationError('Vendor eval no 1 has not evaluated yet!')
    
    ## Customer Eval 2
    terms_eval = fields.Boolean(string='2. Terms of Payment', readonly=True, states={'draft': [('readonly', False)]},
                help='30 to 45 Days(4), 14 Days(3), 7 Days(2), CBD/COD(1)')
    terms_score = fields.Integer(string='Score', readonly=True, states={'draft': [('readonly', False)]})
    terms = fields.Selection(point, string='Rate', default=point[0][0], readonly=True, states={'draft': [('readonly', False)]})
    terms_comment = fields.Char(string='Comment', readonly=True, states={'draft': [('readonly', False)]})

    @api.constrains('terms_score', 'terms')
    def criteria_terms(self):
        for rec in self:
            if rec.terms_eval and rec.terms_score > 4:
                raise ValidationError('Score of Vendor eval no 2 must be 1 until 4!')
            if rec.terms_eval and rec.terms_score < 1:
                raise ValidationError('Score of Vendor eval no 2 must be 1 until 4!')
            if rec.terms_eval and not rec.terms:
                raise ValidationError('Vendor eval no 2 has not evaluated yet!')

    ## Customer Eval 3
    items_eval = fields.Boolean(string='3. Item Avaibility', readonly=True, states={'draft': [('readonly', False)]},
                help='Ready Stock(4), Indent(2)')
    items_score = fields.Integer(string='Score', readonly=True, states={'draft': [('readonly', False)]})
    items = fields.Selection(point, string='Rate', default=point[0][0], readonly=True, states={'draft': [('readonly', False)]})
    items_comment = fields.Char(string='Comment', readonly=True, states={'draft': [('readonly', False)]})

    @api.constrains('items_score', 'items')
    def criteria_items(self):
        for rec in self:
            if rec.items_eval and rec.items_score != 4 and rec.items_score != 2:
                raise ValidationError('Score of Vendor eval no 3 must be 2 or 4!')
            if rec.items_eval and not rec.items:
                raise ValidationError('Vendor eval no 3 has not evaluated yet!')

    ## Customer Eval 4
    accuracy_eval = fields.Boolean(string='4. Accuracy in Delivery', readonly=True, states={'draft': [('readonly', False)]},
                    help='Match with Quotation(4), Quotation +3 days(3), Quotation +7 days(2), Quotation + 14 days(1)')
    accuracy_score = fields.Integer(string='Score', readonly=True, states={'draft': [('readonly', False)]})
    accuracy = fields.Selection(point, string='Rate', default=point[0][0], readonly=True, states={'draft': [('readonly', False)]})
    accuracy_comment = fields.Char(string='Comment', readonly=True, states={'draft': [('readonly', False)]})

    @api.constrains('accuracy_score', 'accuracy')
    def criteria_accuracy(self):
        for rec in self:
            if rec.accuracy_eval and rec.accuracy_score > 4:
                raise ValidationError('Score of Vendor eval no 4 must be 1 until 4!')
            if rec.accuracy_eval and rec.accuracy_score < 1:
                raise ValidationError('Score of Vendor eval no 4 must be 1 until 4!')
            if rec.accuracy_eval and not rec.accuracy:
                raise ValidationError('Vendor eval no 4 has not evaluated yet!')

    ## Customer Eval 5
    respon_eval = fields.Boolean(string='5. Respon For RFQ', readonly=True, states={'draft': [('readonly', False)]},
                help='Fast(4), Slow(2)')
    respon_score = fields.Integer(string='Score', readonly=True, states={'draft': [('readonly', False)]})
    respon = fields.Selection(point, string='Rate', default=point[0][0], readonly=True, states={'draft': [('readonly', False)]})
    respon_comment = fields.Char(string='Comment', readonly=True, states={'draft': [('readonly', False)]})

    @api.constrains('respom_score', 'respon')
    def criteria_respon(self):
        for rec in self:
            if rec.respon_eval and rec.respon_score != 2 and rec.respon_score != 4:
                raise ValidationError('Score of Vendor eval no 5 must be 2 or 4!')
            if rec.terms_eval and not rec.terms:
                raise ValidationError('Vendor eval no 5 has not evaluated yet!')

    ## Customer Eval 6
    complain_eval = fields.Boolean(string='6. Respon For Complain', readonly=True, states={'draft': [('readonly', False)]},
                    help='Good(4), Bad(-4)')
    complain_score = fields.Integer(string='Score', readonly=True, states={'draft': [('readonly', False)]})
    complain = fields.Selection(point, string='Rate', default=point[0][0], readonly=True, states={'draft': [('readonly', False)]})
    complain_comment = fields.Char(string='Comment', readonly=True, states={'draft': [('readonly', False)]})

    @api.constrains('complain_score', 'complain')
    def criteria_complain(self):
        for rec in self:
            if rec.complain_eval and rec.complain_score != 4 and rec.complain_score != -4:
                raise ValidationError('Score of Vendor eval no 6 must be -4 or 4!')
            if rec.terms_eval and not rec.terms:
                raise ValidationError('Vendor eval no 6 has not evaluated yet!')

    ## Customer Eval 7
    warranty_eval = fields.Boolean(string='7. Claim For Warranty', readonly=True, states={'draft': [('readonly', False)]},
                    help='Convenient(4), Complicated(-4)')
    warranty_score = fields.Integer(string='Score', readonly=True, states={'draft': [('readonly', False)]})
    warranty = fields.Selection(point, string='Rate', default=point[0][0], readonly=True, states={'draft': [('readonly', False)]})
    warranty_comment = fields.Char(string='Comment', readonly=True, states={'draft': [('readonly', False)]})

    @api.constrains('warranty_score', 'warranty')
    def criteria_warranty(self):
        for rec in self:
            if rec.warranty_eval and rec.warranty_score != 4 and rec.warranty_score != -4:
                raise ValidationError('Score of Vendor eval no 7 must be -4 or 4!')
            if rec.warranty_eval and not rec.warranty:
                raise ValidationError('Vendor eval no 7 has not evaluated yet!')

    ##Management Report
    final_score = fields.Float(readonly=True, store=True, string='Final Score')
    final_rate = fields.Selection(point, string='Final Rate')
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
            if rec.respon_eval:
                count += rec.respon_score
                sum_total += (int(rec.respon) * rec.respon_score)
            if rec.complain_eval:
                count += rec.complain_score
                sum_total += (int(rec.complain) * rec.complain_score)
            if rec.warranty_eval:
                count += rec.warranty_score
                sum_total += (int(rec.warranty) * rec.warranty_score)
            if count == 0:
                raise ValidationError('Score must be filled!')
            else:
                rec.final_score = count
    
    def unlink(self):
        for rec in self:
            if rec.state != 'draft':
                raise ValidationError('You can not delete record when status is not draft')
        return super(VendorManagement, self).unlink()

    @api.model
    def create(self, vals):
        rec = super(VendorManagement, self).create(vals)
        number = self.env['ir.sequence'].next_by_code('vendor_managemnet_seq')
        rec.name = number
        rec.calculate()
        return rec

    # def write(self, vals):
    #     rec = super(VendorManagement, self).write(vals)
    #     if 'final_score' not in vals and 'final_rate' not in vals:
    #         self.calculate()
    #     return rec

# class VendorAdd(models.Model):
#     _inherit = 'res.partner'

#     visible_management = fields.Selection(VendorManagement.point, string='Last Management', compute='_calculate_eval', readonly=True)

#     @api.depends()
#     def _calculate_eval(self):
#         for rec in self:
#             record = self.env['vendor.management'].search([
#                 ('vendor', '=', rec.id),
#                 ('state', '=', 'approved')
#             ])
#             if record:
#                 rec.visible_management = record.sorted('period_end', reverse=True)[0].final_rate 
#             else:
#                 rec.visible_management = False