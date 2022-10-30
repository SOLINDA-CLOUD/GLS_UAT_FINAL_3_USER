from odoo import _, api, fields, models
from odoo.exceptions import ValidationError
from dateutil.relativedelta import relativedelta

class SaleOrder(models.Model):
    _inherit = 'sale.order'
    _description = 'Sale Order'
    
    payment_schedule_line_ids = fields.One2many('payment.schedule', 'order_id', string='Payment Schedule Line')
    deduct_dp = fields.Boolean('Deduct DP')
    payment_scheme = fields.Selection([
        ('normal', 'Normal'),
        ('deduct', 'Deduct'),
    ], string='Payment Scheme')

    ## Other Info
    attn_id = fields.Many2one('res.partner', string='Attn')
    director_info = fields.Char(string='Director')
    
    
    @api.onchange('payment_schedule_line_ids')
    def _onchange_payment_schedule_line_ids(self):
        # total = sum(self.payment_schedule_line_ids.mapped('total_amount'))
        # if total > self.amount_total:
        total = sum(self.payment_schedule_line_ids.mapped('bill'))
        if total > 1:
            raise ValidationError("Total in Payment Schedule is greater then total amount in sales")

class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'
    
    qty_delivered = fields.Float(readonly=False)


class PaymentSchedule(models.Model):
    _name = 'payment.schedule'
    _description = 'Payment Schedule'
    
    order_id = fields.Many2one('sale.order', string='Sale Order')    
    payment_date = fields.Date('Payment Date')
    payment_type = fields.Selection([
        ('dp', 'Down Payment'),
        ('termin', 'Termin'),
        ('retensi', 'Retensi'),
    ], string='Payment Type')
    currency_id = fields.Many2one('res.currency', default=lambda self: self.env.company.currency_id)
    amount = fields.Monetary(currency_field='currency_id')
    # product_id = fields.Many2one('product.product', string='Service')
    account_id = fields.Many2one('account.account', string='Account')
    name = fields.Char('Description')
    progress = fields.Float('Progress')
    bill = fields.Float('Bill')
    include_project_cost = fields.Boolean('Include Project Cost')
    total_amount = fields.Float(compute='_compute_total_amount', string='Total Amount')
    move_id = fields.Many2one('account.move',string="Invoice")
    move_line_id = fields.Many2many('account.move.line')
    include_dp = fields.Boolean('Include DP')
    include_termin = fields.Boolean('Include Termin')
    percentage_based_on = fields.Selection([
        ('bill', 'Bill'),
        ('progress', 'Progress'),
    ], string='Percentage Based On',default="bill")
    deduct_dp = fields.Boolean('Deduct DP')

    
    
    
    @api.depends('order_id.amount_total','bill','percentage_based_on','order_id.payment_scheme')
    def _compute_total_amount(self):
        for this in self:
            total_amount = 0
            if this.percentage_based_on == 'bill':
                total_amount = this.bill * this.order_id.amount_total
            if this.percentage_based_on == 'progress':
                total_amount = this.progress * this.order_id.amount_total
            if this.payment_type in ('dp','retensi'):
                total_amount = this.bill * this.order_id.amount_total
                
            this.total_amount = total_amount
    
    def _include_project_cost(self,project,cost):
        data_payment = []
        data_payment.append((0,0,{
                        'sequence': 10,
                        'name': "Project Cost",
                        'account_id':project.project_cost_account_id.id,
                        'quantity': 1,
                        # 'price_unit': self.total_amount,
                        'price_unit': cost * -1,
                        'analytic_account_id': self.order_id.analytic_account_id.id,
                        'payment_schedule_ids': [(4, self.id)]
                        }))
        data_payment.append((0,0,{
                        'sequence': 10,
                        'name': "Project On Progress",
                        'account_id':project.project_onprogress_account_id.id,
                        'quantity': 1,
                        # 'price_unit': self.total_amount,
                        'price_unit': cost,
                        'analytic_account_id': self.order_id.analytic_account_id.id,
                        'payment_schedule_ids': [(4, self.id)]
                        }))
        return data_payment
        
                        
    
    def create_invoice(self):
        invoice_vals = self.order_id._prepare_invoice()
        if self.move_id:
            return {
                        'name': '%s - %s'%(self.order_id.name,self.name),
                        'type': 'ir.actions.act_window',
                        'view_mode': 'form',
                        'res_model': 'account.move',
                        'res_id': self.move_id.id,
            }
        else:
            # if self.order_id.deduct_dp:
            list_dp = []
            project = self.order_id.project_ids[0] if self.order_id.project_ids else self.order_id.project_id
            data_payment = []
            amount_total = 0
            cost = 0
            retensi = 0
            if self.order_id.payment_scheme == 'deduct':
                if self.payment_type == 'termin':                
                    seq = 10
                    amount = self.total_amount
                    dp = sum(self.order_id.payment_schedule_line_ids.filtered(lambda x : x.payment_type in ('dp')).mapped('total_amount'))
                    data_retensi = self.order_id.payment_schedule_line_ids.filtered(lambda x : x.payment_type == 'retensi')
                    for payment in self.order_id.payment_schedule_line_ids.filtered(lambda x : x.payment_type == 'termin'):
                        if payment.id != self.id:
                            amount -= payment.move_id.amount_total
                    if data_retensi.percentage_based_on == 'bill' :
                        retensi = self.total_amount * data_retensi.bill
                    elif data_retensi.percentage_based_on == 'progress' :
                        retensi = self.total_amount * data_retensi.progress
                    
                    amount = amount - (dp + retensi)
                    if self.deduct_dp:
                        amount += dp
                        record_dp = self.order_id.payment_schedule_line_ids.filtered(lambda x : x.payment_type == 'dp')
                        data_payment.append((0,0,{
                                'sequence': 10,
                                'name': self.name,
                                'account_id': self.account_id.id,
                                'quantity': 1,
                                'price_unit': amount,
                                'analytic_account_id': self.order_id.analytic_account_id.id,
                                'payment_schedule_ids': [(4, self.id)]
                        }))
                        data_payment.append((0,0,{
                                'sequence': 11,
                                'name': record_dp.name,
                                'account_id': record_dp.account_id.id,
                                'quantity': 1,
                                'price_unit': -record_dp.total_amount,
                                'analytic_account_id': self.order_id.analytic_account_id.id,
                                'payment_schedule_ids': [(4, self.id)]
                        }))
                        data_payment += self._include_project_cost(project,amount * (1 - self.order_id.final_profit))
                        
                    else:
                        data_payment.append((0,0,{
                                'sequence': 10,
                                'name': self.name,
                                'account_id': self.account_id.id,
                                'quantity': 1,
                                'price_unit': amount,
                                'analytic_account_id': self.order_id.analytic_account_id.id,
                                'payment_schedule_ids': [(4, self.id)]
                        }))
                        data_payment += self._include_project_cost(project,amount * (1 - self.order_id.final_profit))
                    invoice_vals['invoice_line_ids'] += data_payment
                    moves = self.env['account.move'].sudo().with_context(default_move_type='out_invoice').create(invoice_vals)    
                elif self.payment_type == 'retensi':
                    data_payment.append((0,0,{
                            'sequence': 10,
                            'name': self.name,
                            'account_id': self.account_id.id,
                            'quantity': 1,
                            'price_unit': self.total_amount,
                            'analytic_account_id': self.order_id.analytic_account_id.id,
                            'payment_schedule_ids': [(4, self.id)]
                    }))
                    data_payment += self._include_project_cost(project,self.total_amount * (1 - self.order_id.final_profit))
                    invoice_vals['invoice_line_ids'] += data_payment
                    
                    moves = self.env['account.move'].sudo().with_context(default_move_type='out_invoice').create(invoice_vals)    
                else:
                    invoice_vals['invoice_line_ids'] = [(0,0,{
                        'sequence': 10,
                        'name': self.name,
                        'account_id': self.account_id.id,
                        'quantity': 1,
                        'price_unit': self.total_amount,
                        'analytic_account_id': self.order_id.analytic_account_id.id,
                        'payment_schedule_ids': [(4, self.id)]
                    })]
                    moves = self.env['account.move'].sudo().with_context(default_move_type='out_invoice').create(invoice_vals)    
            
            elif self.order_id.payment_scheme == 'normal':
                
                if self.include_dp:
                    data_dp = self.order_id.payment_schedule_line_ids.filtered(lambda x : x.payment_type == 'dp')
                    invoice_vals['invoice_line_ids'] = [
                    (0,0,{
                        'sequence': 10,
                        'name': self.name,
                        'account_id': self.account_id.id,
                        'quantity': 1,
                        'price_unit': self.total_amount + data_dp[0].total_amount,
                        'analytic_account_id': self.order_id.analytic_account_id.id,
                        'payment_schedule_ids': [(4, self.id)]
                    }),
                    (0,0,{
                        'sequence': 10,
                        'name': data_dp[0].name,
                        'account_id': data_dp[0].account_id.id,
                        'quantity': 1,
                        'price_unit': data_dp[0].total_amount * -1,
                        'analytic_account_id': data_dp[0].order_id.analytic_account_id.id,
                        'payment_schedule_ids': [(4, data_dp[0].id)]
                    })]
                   
                    if self.deduct_dp:
                        cost = self.total_amount * (1 - self.order_id.final_profit)
                    else:
                        # cost = (self.total_amount + (data_dp[0].total_amount * -1)) * (1 - self.order_id.final_profit)
                        # cost = self.total_amount * (1 - self.order_id.final_profit)
                        cost = (self.total_amount + data_dp[0].total_amount) * (1 - self.order_id.final_profit)
                        
                else:
                    invoice_vals['invoice_line_ids'] = [(0,0,{
                        'sequence': 10,
                        'name': self.name,
                        'account_id': self.account_id.id,
                        'quantity': 1,
                        'price_unit': self.total_amount,
                        'analytic_account_id': self.order_id.analytic_account_id.id,
                        'payment_schedule_ids': [(4, self.id)]
                    })]
                    
                    cost = self.total_amount * (1 - self.order_id.final_profit)
                    
                if self.include_project_cost:
                    invoice_vals['invoice_line_ids'] += self._include_project_cost(project,cost)
                
                moves = self.env['account.move'].sudo().with_context(default_move_type='out_invoice').create(invoice_vals)    

            self.write({'move_id': moves.id})
            return {
                            'name': '%s - %s'%(self.order_id.name,self.name),
                            'type': 'ir.actions.act_window',
                            'view_mode': 'form',
                            'res_model': 'account.move',
                            'res_id': moves.id,
                
            }
             
    @api.constrains('amount')
    def _constrains_amount(self):
        for this in self:
            total = this.order_id.amount_total
            if this.amount > total:
                raise ValidationError('Amount field is greater then sales total amount')
    
    # @api.onchange('payment_term_id')
    # def _onchange_payment_term_id(self):
    #     if self.payment_term_id:
    #         days = self.payment_term_id.line_ids[0].days
    #         self.payment_date = self.order_id.date_order + relativedelta(days=days)
    #     else:
    #         self.payment_date = False
    
    
    
    
    
    # for payment in self.order_id.payment_schedule_line_ids.filtered(lambda x : x.payment_type == 'termin'):
                    #     if payment.id != self.id:
                    #         if payment.move_id:
                    #         #     data_payment.append((0,0,{
                    #         #     'sequence': seq + 10,
                    #         #     'name': payment.name,
                    #         #     'account_id': payment.account_id.id,
                    #         #     'quantity': 1,
                    #         #     'price_unit': -payment.move_id.amount_total,
                    #         #     'analytic_account_id': self.order_id.analytic_account_id.id,
                    #         #     'payment_schedule_ids': [(4, payment.id)]
                    #         # }))
                    #             amount_total += payment.move_id.amount_total
                    #         else:
                    #             raise ValidationError("Cannot Processed because a payment schedule %s hasn't made an invoice yet"%payment.name)
                    #     else:
                    #         amount_total += self.total_amount
                    #         cost = amount_total * (1 - self.order_id.final_profit)
                    #         data_payment.append((0,0,{
                    #         'sequence': 10,
                    #         'name': self.name,
                    #         'account_id': self.account_id.id,
                    #         'quantity': 1,
                    #         'price_unit': self.total_amount,
                    #         # 'price_unit': amount_total,
                    #         'analytic_account_id': self.order_id.analytic_account_id.id,
                    #         'payment_schedule_ids': [(4, self.id)]
                    #         }))
                        
                    #         break    
                    # if self.include_project_cost:
                    #     data = self._include_project_cost(project,cost)
                    #     data_payment += data
                    # for aditional_data in self.order_id.payment_schedule_line_ids.filtered(lambda x : x.payment_type in ('dp','retensi')):
                    #     data_payment.append((0,0,{
                    #             'sequence': 10,
                    #             'name': aditional_data.name,
                    #             'account_id': aditional_data.account_id.id,
                    #             'quantity': 1,
                    #             # 'price_unit': self.total_amount,
                    #             'price_unit': aditional_data.total_amount * -1 if aditional_data.payment_type == 'dp' else (self.total_amount * aditional_data.bill) * -1,
                    #             'analytic_account_id': self.order_id.analytic_account_id.id,
                    #             'payment_schedule_ids': [(4, self.id)]
                    #             }))