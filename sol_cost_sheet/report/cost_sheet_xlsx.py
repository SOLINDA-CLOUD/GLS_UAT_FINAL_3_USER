from odoo import fields, models, api, _
from xlsxwriter.utility import xl_range
from xlsxwriter.utility import xl_rowcol_to_cell
from xlsxwriter.utility import xl_cell_to_rowcol


class CostSheetXlsx(models.AbstractModel):
    _name = 'report.sol_cost_sheet.report_cost_sheet_xlsx'
    _inherit = 'report.report_xlsx.abstract'

    def generate_xlsx_report(self, workbook, data, obj):
        money_format = workbook.add_format({'font_size': 10, 'left': 1, 'bottom': 1, 'right': 1, 'top': 1, 'align': 'right', 'valign': 'vcenter', 'text_wrap': True, 'num_format': '#,##0.00' })
        border_basic = workbook.add_format({'font_size': 10, 'left': 1, 'bottom': 1, 'right': 1, 'top': 1, 'align': 'center', 'valign': 'vcenter', 'text_wrap': True, })
        
        style_basic = workbook.add_format({'font_size': 10, 'align': 'left', 'valign': 'vcenter' })
        style_basic_section = workbook.add_format({'font_size': 10, 'align': 'left', 'valign': 'vcenter' })
        style_basic_note = workbook.add_format({'font_size': 10, 'align': 'left', 'valign': 'vcenter', 'text_wrap': True })
        style_basic_center = workbook.add_format({'font_size': 10, 'align': 'center', 'valign': 'vcenter' })
        style_basic_bold = workbook.add_format({'font_size': 10, 'align': 'left', 'valign': 'vcenter', 'bold': True })
        style_basic_bold_center = workbook.add_format({'font_size': 10, 'align': 'center', 'valign': 'vcenter', 'bold': True })
        
        style_basic_section.set_bg_color('#FDEA88')
        style_basic_note.set_bg_color('#F8D316')


        format_header = workbook.add_format({'align': 'center', 'valign': 'vcenter', 'bold': True, 'size': 12, 'top': 1, 'left': 1, 'right': 1, 'bottom': 1, 'text_wrap': True})
        # format_header = workbook.add_format({'align': 'center', 'valign': 'vcenter', 'bold': True, 'size': 12, 'text_wrap': True})

        worksheet = workbook.add_worksheet('Cost Sheet')
        worksheet.set_column('A:B', 5)
        worksheet.set_column('C:D', 30)
        worksheet.set_column('E:F', 10)
        worksheet.set_column('G:J', 15)

        worksheet.merge_range('A1:C1', 'CRM: %s' % (obj.crm_id.name), style_basic_bold)
        worksheet.merge_range('A2:C2', 'Request Date: %s' % (obj.date_document.strftime('%d/%m/%Y') if obj.date_document else ""), style_basic_bold)
        worksheet.merge_range('A3:C3', 'Responsible: %s' % (obj.user_id.name), style_basic_bold)
        worksheet.merge_range('A4:C4', 'Customer: %s' % (obj.partner_id.name or ""), style_basic_bold)
        worksheet.merge_range('A5:C5', 'Tax: %s' % (obj.tax_id.name), style_basic_bold)

        worksheet.merge_range('A7:A9', "No", format_header)
        worksheet.merge_range('B7:D9', "Items", format_header)
        worksheet.merge_range('E7:F9', "Quantity", format_header)
        worksheet.merge_range('G7:G9', "Existing Price (Rp)", format_header)
        worksheet.merge_range('H7:H9', "RFQ Price (Rp)", format_header)
        worksheet.merge_range('I7:I9', "Total Price (Rp)", format_header)
        worksheet.merge_range('J7:J9', "Remarks", format_header)

        row = 9
        first_row = row
        no = 1
        sub_no = 1

        def get_style_name(type):
            if type == 'line_section':
                return style_basic_section
            elif type == 'line_note':
                return style_basic_note
            else:
                return style_basic

        data = obj.category_line_ids
        for rec in data:
            worksheet.write(row, 0, no, style_basic_bold_center)
            worksheet.write(row, 1, rec.product_id.name, style_basic_bold)
            for comp in rec.parent_component_line_ids:
                worksheet.write(row + 1, 1, "%s.%s" % (no,sub_no), style_basic_bold_center)
                worksheet.write(row + 1, 2, comp.product_id.name, style_basic_bold)
                sub_no += 1
                row += 1
                for item in comp.item_ids:
                    style_for_name = get_style_name(item.display_type)
                    worksheet.write(row + 1, 2, item.name, style_for_name)
                    worksheet.write(row + 1, 4, item.product_qty if item.display_type == False else "", style_basic_center)
                    worksheet.write(row + 1, 5, item.uom_id.name if item.display_type == False else "", style_basic_center)
                    worksheet.write(row + 1, 6, item.existing_price if item.display_type == False else "", style_basic_center)
                    worksheet.write(row + 1, 7, item.rfq_price if item.display_type == False else "", style_basic_center)
                    worksheet.write(row + 1, 8, item.total_price if item.display_type == False else "", style_basic_center)
                    worksheet.write(row + 1, 9, item.remarks or "" if item.display_type == False else "", style_basic_center)
                    row += 1

            row += 1
            no += 1
            sub_no = 1
        
        sub_no = 1
        data_ga = obj.ga_project_line_ids
        worksheet.write(row, 0, no, style_basic_bold_center)
        worksheet.write(row, 1, "GA Project", style_basic_bold)
        for rec in data_ga:
            worksheet.write(row + 1, 1, "%s.%s" % (no,sub_no), style_basic_bold_center)
            worksheet.write(row + 1, 2, rec.product_id.name, style_basic_bold)
            worksheet.write(row + 1, 4, rec.product_qty, style_basic_center)
            worksheet.write(row + 1, 6, rec.existing_price, style_basic_center)
            worksheet.write(row + 1, 7, rec.rfq_price, style_basic_center)
            worksheet.write(row + 1, 8, rec.total_price, style_basic_center)
            worksheet.write(row + 1, 9, rec.remarks or "", style_basic_center)
            row += 1
            sub_no += 1
        row += 1
        no += 1
        sub_no = 1

        data_waranty = obj.waranty_line_ids
        worksheet.write(row, 0, no, style_basic_bold_center)
        worksheet.write(row, 1, "Warranty", style_basic_bold)
        for rec in data_waranty:
            worksheet.write(row + 1, 1, "%s.%s" % (no,sub_no), style_basic_bold_center)
            worksheet.write(row + 1, 2, rec.product_id.name, style_basic_bold)
            worksheet.write(row + 1, 4, rec.product_qty, style_basic_center)
            worksheet.write(row + 1, 6, rec.existing_price, style_basic_center)
            worksheet.write(row + 1, 7, rec.rfq_price, style_basic_center)
            worksheet.write(row + 1, 8, rec.total_price, style_basic_center)
            worksheet.write(row + 1, 9, rec.remarks or "", style_basic_center)
            row += 1
            sub_no += 1
        row += 1
        no += 1
        sub_no = 1

        # print(ea)

        # parent_categ = {}
        # query = """
        # SELECT rc.product_id as categ, cc.product_id as compo, item.product_id as items, 
        # item.product_qty, item.uom_id, item.existing_price, item.rfq_price, item.total_price, item.remarks
        # from cost_sheet cs
        # left join rab_category rc on rc.cost_sheet_id = cs.id
        # left join component_component cc on cc.category_id = rc.id
        # left join item_item item on item.component_id = cc.id
        # WHERE cs.id = %s
        # order by rc.product_id, cc.product_id

        # """ % (obj.id)
        # self._cr.execute(query)
        # data = self._cr.dictfetchall()
        # prods = self.env['product.product']
        # uom = self.env['uom.uom']        
        # no = 1
        # categ_list = {}
        # for res in data:
        #     if res['categ'] not in categ_list:
        #         categ_list[res['categ']] = [res['compo']]
        #         worksheet.write(row, 0, no, style_basic_bold_center)
        #         worksheet.write(row, 1, prods.browse(res['categ']).name, style_basic_bold)
        #         row += 1
        #         no += 1
        #     else:
        #         categ_list[res['categ']].append(res['compo'])

        #     worksheet.write(row, 3, prods.browse(res['items']).name, style_basic)
        #     worksheet.write(row, 4, res['product_qty'], style_basic_center)
        #     worksheet.write(row, 5, uom.browse(res['uom_id']).name, style_basic_center)
        #     worksheet.write(row, 6, res['existing_price'], style_basic_center)
        #     worksheet.write(row, 7, res['rfq_price'], style_basic_center)
        #     worksheet.write(row, 8, res['total_price'], style_basic_center)
        #     worksheet.write(row, 9, res['remarks'], style_basic_center)
            
        #     row += 1

        # row = first_row
        # no = 1
        # sub_no = 1
        # for categ,compo in categ_list.items():
        #     if no == 1:
        #         row += 1
        #     else:
        #         row += 2
        #     compo_list = []
        #     for c in compo:
        #         if c not in compo_list:
        #             compo_list.append(c)
        #             worksheet.write(row, 1, "%s.%s" % (no,sub_no), style_basic_bold_center)
        #             worksheet.write(row, 2, prods.browse(c).name, style_basic_bold)
        #             sub_no += 1
        #             row += 1
        #     no += 1
        


        