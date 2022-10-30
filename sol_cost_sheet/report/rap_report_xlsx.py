from odoo import fields, models, api, _
from xlsxwriter.utility import xl_range
from xlsxwriter.utility import xl_rowcol_to_cell
from xlsxwriter.utility import xl_cell_to_rowcol


class CostSheetXlsx(models.AbstractModel):
    _name = 'report.sol_cost_sheet.rap_report_xlsx'
    _inherit = 'report.report_xlsx.abstract'

    def generate_xlsx_report(self, workbook, data, obj):
        money_format_table = workbook.add_format({'font_size': 10, 'left': 1, 'bottom': 1, 'right': 1, 'top': 1, 'align': 'right', 'valign': 'vcenter', 'text_wrap': True, 'num_format': '#,##0.00' })
        money_format = workbook.add_format({'font_size': 10, 'align': 'right', 'valign': 'vcenter', 'text_wrap': True, 'num_format': '#,##0.00' })
        border_basic = workbook.add_format({'font_size': 10, 'left': 1, 'bottom': 1, 'right': 1, 'top': 1, 'align': 'center', 'valign': 'vcenter', 'text_wrap': True, })

        header_format = workbook.add_format({'font_size': 12, 'bold': True, 'align': 'center', 'valign': 'vcenter', 'left': 1, 'bottom': 1, 'right': 1, 'top': 1,'text_wrap': True, })
        
        style_basic = workbook.add_format({'font_size': 10, 'align': 'left', 'valign': 'vcenter' })
        style_basic_center = workbook.add_format({'font_size': 10, 'align': 'center', 'valign': 'vcenter' })
        style_basic_bold = workbook.add_format({'font_size': 10, 'align': 'left', 'valign': 'vcenter', 'bold': True })
        style_basic_bold_center = workbook.add_format({'font_size': 10, 'align': 'center', 'valign': 'vcenter', 'bold': True })
        
        style_basic_section = workbook.add_format({'font_size': 10, 'align': 'left', 'valign': 'vcenter' })
        style_basic_note = workbook.add_format({'font_size': 10, 'align': 'left', 'valign': 'vcenter', 'text_wrap': True })
        style_basic_section.set_bg_color('#FDEA88')
        style_basic_note.set_bg_color('#F8D316')

        header_format.set_bg_color('#B2B1AE')

        worksheet = workbook.add_worksheet('RAP Report')
        worksheet.set_column('A:A', 15)
        worksheet.set_column('B:B', 7)
        worksheet.set_column('C:D', 5)
        worksheet.set_column('E:E', 45)
        worksheet.set_column('F:I', 15)
        worksheet.set_column('J:J', 45)
        worksheet.set_column('K:P', 15)
        worksheet.set_column('Q:Q', 20)
        worksheet.set_column('R:R', 15)

        def create_header(row, col, project):
            worksheet.write(row - 1, col, project, style_basic_bold_center)
            worksheet.merge_range(row, col, row + 1, col, "Project Code", header_format)
            worksheet.merge_range(row, col + 1, row + 1, col + 1, "No", header_format)
            worksheet.merge_range(row, col + 2, row + 1, col + 4, "Item", header_format)
            worksheet.merge_range(row, col + 5, row + 1, col + 5, "Quantity", header_format)
            worksheet.merge_range(row, col + 6, row + 1, col + 6, "Total Price", header_format)

            col = col + 7
            worksheet.merge_range(row, col + 1, row + 1, col + 1, "PO No.", header_format)
            worksheet.merge_range(row, col + 2, row + 1, col + 2, "Detail Description", header_format)
            worksheet.merge_range(row, col + 3, row + 1, col + 3, "Qty", header_format)
            worksheet.merge_range(row, col + 4, row + 1, col + 4, "Unit", header_format)
            worksheet.merge_range(row, col + 5, row + 1, col + 5, "Curr", header_format)
            worksheet.merge_range(row, col + 6, row + 1, col + 6, "Unit Price", header_format)
            worksheet.merge_range(row, col + 7, row + 1, col + 7, "Disc", header_format)
            worksheet.merge_range(row, col + 8, row + 1, col + 8, "Total Price", header_format)
            worksheet.merge_range(row, col + 9, row + 1, col + 9, "Vendor Name", header_format)
            worksheet.merge_range(row, col + 10, row + 1, col + 10, "Budget Code", header_format)

        def get_style_name(type):
            if type == 'line_section':
                return style_basic_section
            elif type == 'line_note':
                return style_basic_note
            else:
                return style_basic

        row = 4
        no = 1
        sub_no = 1

        domain = [('rap_id','!=',False)]
        if obj.project_ids:
            domain += [('rap_id.project_id','in',obj.project_ids.ids)]
        data = self.env['rap.category'].search(domain, order='project_id asc')
        projects = []
        count = 1

        for rec in data:
            if rec.project_id not in projects:
                projects.append(rec.project_id)
                if count != 1:
                    no = 1
                    row += 5
                count += 1
                create_header(row - 2, 0, rec.project_id.name)
            worksheet.write(row, 0, rec.project_id.code or "-", style_basic_bold_center)
            worksheet.write(row, 1, no, style_basic_bold_center)
            worksheet.write(row, 2, rec.product_id.name, style_basic_bold)
            for comp in rec.parent_component_line_ids:
                worksheet.write(row + 1, 2, "%s.%s" % (no,sub_no), style_basic_bold_center)
                worksheet.write(row + 1, 3, comp.product_id.name, style_basic_bold)
                sub_no += 1
                row += 1
                for item in comp.item_ids:
                    style_for_name = get_style_name(item.display_type)
                    worksheet.write(row + 1, 3, item.name, style_for_name)
                    worksheet.write(row + 1, 5, "%s %s" % (item.product_qty,item.uom_id.name) if item.display_type == False else "", style_basic_center)
                    worksheet.write(row + 1, 6, item.total_price if item.display_type == False else "", money_format)

                    for purchase in item.purchase_order_line_ids:
                        worksheet.write(row + 1, 8, purchase.order_id.name, style_basic_center)
                        worksheet.write(row + 1, 9, purchase.name, style_basic)
                        worksheet.write(row + 1, 10, purchase.product_qty, style_basic_center)
                        worksheet.write(row + 1, 11, purchase.product_uom.name, style_basic_center)
                        worksheet.write(row + 1, 12, purchase.order_id.currency_id.name, style_basic_center)
                        worksheet.write(row + 1, 13, purchase.price_unit, money_format)
                        worksheet.write(row + 1, 14, 0, style_basic_center)
                        worksheet.write(row + 1, 15, purchase.price_subtotal, money_format)
                        worksheet.write(row + 1, 16, purchase.order_id.partner_id.name, style_basic_center)
                        worksheet.write(row + 1, 17, purchase.account_analytic_id.name, style_basic_center)
                        # worksheet.write(row + 1, 17, rec.project_id.code or "-", style_basic_center)
                        row += 1

                    row += 1

            row += 1
            no += 1

        data_ga = obj.project_ids.rap_id.ga_project_line_ids
        worksheet.write(row, 1, no, style_basic_bold_center)
        worksheet.write(row, 2, "GA Project", style_basic_bold)
        for rec in data_ga:
            worksheet.write(row + 1, 2, "%s.%s" % (no,sub_no), style_basic_bold_center)
            worksheet.write(row + 1, 3, rec.product_id.name, style_basic_bold)
            worksheet.write(row + 1, 5, rec.product_qty, style_basic_center)
            worksheet.write(row + 1, 6, rec.total_price, style_basic_center)
            sub_no += 1
            row += 1
        row += 1
        no += 1

        data_ga = obj.project_ids.rap_id.waranty_line_ids
        worksheet.write(row, 1, no, style_basic_bold_center)
        worksheet.write(row, 2, "Waranty", style_basic_bold)
        for rec in data_ga:
            worksheet.write(row + 1, 2, "%s.%s" % (no,sub_no), style_basic_bold_center)
            worksheet.write(row + 1, 3, rec.product_id.name, style_basic_bold)
            worksheet.write(row + 1, 5, rec.product_qty, style_basic_center)
            worksheet.write(row + 1, 6, rec.total_price, style_basic_center)
            sub_no += 1
            row += 1
        row += 1
        no += 1


