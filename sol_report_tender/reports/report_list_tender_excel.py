# -*- coding: utf-8 -*-
# from numpy import False_
# from numpy import product
from odoo import fields, models, api
from xlsxwriter.utility import xl_range
from xlsxwriter.utility import xl_rowcol_to_cell
from datetime import datetime, timedelta
from dateutil.parser import parse
from dateutil.relativedelta import relativedelta

import base64
import pytz
import xlwt
import datetime
from dateutil import relativedelta
import time
# from dateutil.relativedelta import relativedelta
from datetime import datetime
import datetime
import calendar
from datetime import datetime, timedelta
from odoo.exceptions import UserError, ValidationError
import logging


class ReportListTenderExcel(models.AbstractModel):
    _name = 'report.sol_report_tender.report_list_tender_excel'
    _inherit = 'report.report_xlsx.abstract'
    
    def excel_column_name(self,n):
        """Number to Excel-style column name, e.g., 1 = A, 26 = Z, 27 = AA, 703 = AAA."""
        name = ''
        while n > 0:
            n, r = divmod (n - 1, 26)
            name = chr(r + ord('A')) + name
        return name

    def generate_xlsx_report(self, workbook, data, obj):
        sheet = workbook.add_worksheet('Report')

        # Format
        format_header                           = workbook.add_format({'font_name': 'Times', 'align': 'center', 'size': 16, 'valign': 'vcenter', 'bold': True, })
        format_header_2                         = workbook.add_format({'font_name': 'Times', 'align': 'center', 'size': 11, 'valign': 'vcenter', 'bold': True, })
        format_header_table                     = workbook.add_format({'font_name': 'Times', 'align': 'center', 'size': 11, 'valign': 'vcenter', 'bold': True,  'left': 1, 'bottom': 1, 'right': 1, 'top': 1})
        format_number_table                     = workbook.add_format({'font_name': 'Times', 'align': 'center', 'size': 11, 'valign': 'vcenter',                'left': 1, 'bottom': 1, 'right': 1, 'top': 1})
        format_number_table_non_border_right    = workbook.add_format({'font_name': 'Times', 'align': 'center', 'size': 11, 'valign': 'vcenter',                'left': 1, 'bottom': 1,             'top': 1, 'bg_color': 'white'})
        format_number_table_non_border_left     = workbook.add_format({'font_name': 'Times', 'align': 'right',  'size': 11, 'valign': 'vcenter',                           'bottom': 1, 'right': 1, 'top': 1, 'bg_color': 'white'})
        format_table                            = workbook.add_format({'font_name': 'Times', 'align': 'left',   'size': 11, 'valign': 'vcenter',                'left': 1, 'bottom': 1, 'right': 1, 'top': 1})
        format_item_table                       = workbook.add_format({'font_name': 'Times', 'align': 'right',  'size': 11, 'valign': 'vcenter',                'left': 1, 'bottom': 1, 'right': 1, 'top': 1, 'num_format': '"Rp." #,###0.00', })

        # Set Column Size >>> set_column(ROW, COL, SIZE)
        sheet.set_column(0, 0, 5)
        sheet.set_column(1, 1, 5)
        sheet.set_column(2, 2, 25)
        sheet.set_column(3, 3, 5)
        sheet.set_column(4, 4, 7)

        po_length = len(obj.purchase_order_ids)
        col_name = []
        
        for x in range(0 ,(po_length * 2) + 2):
            col_name.append(self.excel_column_name(x + 6))

        # Judul
        sheet.merge_range('A2:' + col_name[(po_length * 2)] + '2', 'MATRIKS PERBANDINGAN HARGA ', format_header)
        sheet.merge_range('A3:' + col_name[(po_length * 2)] + '3', 'Membrane : ', format_header_2)

        # Header table
        sheet.write('B4', 'Project :')
        sheet.write('B5', str(parse(str(obj.create_date)).strftime("%d %B %Y")))

        sheet.merge_range('B6:B8', 'No.', format_header_table)
        sheet.merge_range('C6:C8', 'Spesifikasi', format_header_table)
        sheet.merge_range('D6:D8', 'Qty', format_header_table)
        sheet.merge_range('E6:E8', 'Sat', format_header_table)
        sheet.merge_range('F6:' + col_name[(po_length * 2) - 1] + '6', 'Penawaran', format_header_table)

        sheet.write('B9', '', format_header_table)
        sheet.write('C9', '', format_header_table)
        sheet.write('D9', '', format_header_table)
        sheet.write('E9', '', format_header_table)

        for x in range((po_length * 2)):
            sheet.write(col_name[x] + '9', '', format_header_table)

        subtotal1 = []
        product_list = {}
        product_row_id = 0
        col_num = 0
        data_row_num = 10
        
        # Create Product List
        for po in obj.purchase_order_ids:
            for ol in po.order_line:
                if ol.product_id.id not in product_list:
                    product_list[ol.product_id.id] = {
                        "row" : product_row_id
                    }
                    sheet.write('B' + str(data_row_num + product_row_id), product_row_id + 1, format_number_table)
                    sheet.write('C' + str(data_row_num + product_row_id), ol.product_id.name, format_table)
                    sheet.write('D' + str(data_row_num + product_row_id), ol.product_qty, format_number_table)
                    sheet.write('E' + str(data_row_num + product_row_id), ol.product_uom.name, format_number_table)
                    product_row_id += 1
                    
        # Add Style For Empty Column
        for p_row in range(len(product_list)):
            for p_len in range(len(obj.purchase_order_ids)*2):
                sheet.write(col_name[col_num + p_len] + str(data_row_num + p_row), '', format_number_table)
        
        for po in obj.purchase_order_ids:
            # Header Vendor
            sheet.merge_range(col_name[col_num] + '7:' + col_name[col_num + 1] + '7', po.partner_id.name, format_header_table)
            sheet.write(col_name[col_num] + '8', 'Harga', format_header_table)
            sheet.write(col_name[col_num + 1] + '8', 'Total', format_header_table)
            
            # Set Column Size
            sheet.set_column(col_num + 6, col_num + 6, 20)
            sheet.set_column(col_num + 7, col_num + 7, 20)
            
            subtotal1.append({
                'total_price_unit': sum([datas.price_unit for datas in po.order_line]),
                'total_price_subtotal': sum([datas.price_subtotal for datas in po.order_line]),
                'total_price_subtotal_tax': sum([datas.price_tax for datas in po.order_line]),
            })
            
            # Item
            for ol in po.order_line:
                sheet.write(col_name[col_num + 0] + str(data_row_num + product_list[ol.product_id.id]['row']), ol.price_unit, format_number_table)
                sheet.write(col_name[col_num + 1] + str(data_row_num + product_list[ol.product_id.id]['row']), ol.price_subtotal, format_number_table)
                
            col_num += 2
            
        row_num = data_row_num + len(product_list)

        sheet.write('B' + str(row_num), '', format_header_table)
        sheet.write('C' + str(row_num), '', format_header_table)
        sheet.write('D' + str(row_num), '', format_header_table)
        sheet.write('E' + str(row_num), '', format_header_table)

        for x in range((po_length * 2)):
            sheet.write(col_name[x] + str(row_num), '', format_header_table)

        row_num += 1
        sheet.write('B' + str(row_num), '', format_header_table)
        sheet.write('C' + str(row_num), 'Sub Total 1', format_item_table)
        sheet.merge_range('D' + str(row_num) + ':' + 'E' + str(row_num), '', format_number_table)
        col_num = 0
        for rec in subtotal1:
            sheet.write(col_name[col_num] + str(row_num), str(rec['total_price_unit']), format_item_table)
            sheet.write(col_name[col_num + 1] + str(row_num), str(rec['total_price_subtotal']), format_item_table)
            col_num += 2
        row_num += 1
        sheet.write('B' + str(row_num), '', format_header_table)
        sheet.write('C' + str(row_num), 'VAT', format_item_table)
        if obj.tax_id:
            sheet.merge_range('D' + str(row_num) + ':' + 'E' + str(row_num), str(obj.tax_id.amount) + '%', format_number_table)
        else:
            sheet.merge_range('D' + str(row_num) + ':' + 'E' + str(row_num), '0%', format_number_table)
        col_num = 0
        for rec in subtotal1:
            sheet.merge_range(col_name[col_num] + str(row_num) + ':' + col_name[col_num + 1] + str(row_num), str((rec['total_price_subtotal'] * obj.tax_id.amount) / 100), format_item_table)
            col_num += 2
        row_num += 1
        sheet.write('B' + str(row_num), '', format_header_table)
        sheet.write('C' + str(row_num), 'customs', format_item_table)
        sheet.merge_range('D' + str(row_num) + ':' + 'E' + str(row_num), str(obj.customs) + '%', format_number_table)
        col_num = 0
        for rec in subtotal1:
            sheet.merge_range(col_name[col_num] + str(row_num) + ':' + col_name[col_num + 1] + str(row_num), str((rec['total_price_subtotal'] * obj.customs) / 100), format_item_table)
            col_num += 2
        row_num += 1
        sheet.write('B' + str(row_num), '', format_header_table)
        sheet.write('C' + str(row_num), 'Sub Total 2', format_item_table)
        sheet.merge_range('D' + str(row_num) + ':' + 'E' + str(row_num), '', format_number_table)
        col_num = 0
        for rec in subtotal1:
            sheet.merge_range(col_name[col_num] + str(row_num) + ':' + col_name[col_num + 1] + str(row_num), str((rec['total_price_subtotal']) + ((rec['total_price_subtotal'] * obj.tax_id.amount) / 100)), format_item_table)
            col_num += 2
        row_num += 1
        sheet.write('B' + str(row_num), '', format_header_table)
        sheet.write('C' + str(row_num), 'Sewa CDD', format_item_table)
        sheet.merge_range('D' + str(row_num) + ':' + 'E' + str(row_num), '', format_number_table)
        col_num = 0
        nom = 0
        for rec in obj.purchase_order_ids:
            if rec.sewa_cdd_ket:
                sheet.write(col_name[col_num] + str(row_num), str(rec.sewa_cdd_ket), format_number_table_non_border_right)
            else:
                sheet.write(col_name[col_num] + str(row_num), '', format_number_table_non_border_right)
            sheet.write(col_name[col_num + 1] + str(row_num), str(rec.sewa_cdd_harga), format_number_table_non_border_left)
            subtotal1[nom]['sewa_cdd_ket'] = rec.sewa_cdd_harga
            nom += 1
            col_num += 2
        row_num += 1
        sheet.write('B' + str(row_num), '', format_header_table)
        sheet.write('C' + str(row_num), 'Grand total', format_header_table)
        sheet.merge_range('D' + str(row_num) + ':' + 'E' + str(row_num), '', format_number_table)
        col_num = 0
        for rec in subtotal1:
            sheet.merge_range(col_name[col_num] + str(row_num) + ':' + col_name[col_num + 1] + str(row_num), str((rec['total_price_subtotal']) + ((rec['total_price_subtotal'] * obj.tax_id.amount) / 100) + (
                (rec['total_price_subtotal'] * obj.customs) / 100) + ((rec['total_price_subtotal']) + ((rec['total_price_subtotal'] * obj.tax_id.amount) / 100)) + (rec['sewa_cdd_ket'])), format_item_table)
            col_num += 2

        row_num += 1
        sheet.write('B' + str(row_num), '', format_header_table)
        sheet.write('C' + str(row_num), '', format_item_table)
        sheet.merge_range('D' + str(row_num) + ':' + 'E' + str(row_num), '', format_number_table)
        col_num = 0
        for rec in obj.purchase_order_ids:
            sheet.merge_range(col_name[col_num] + str(row_num) + ':' + col_name[col_num + 1] + str(row_num), '', format_item_table)
            col_num += 2
        row_num += 1
        sheet.write('B' + str(row_num), '', format_header_table)
        sheet.write('C' + str(row_num), 'Terms of Payment', format_item_table)
        sheet.merge_range('D' + str(row_num) + ':' + 'E' + str(row_num), 'a', format_number_table)
        col_num = 0
        for rec in obj.purchase_order_ids:
            if rec.payment_term_id:
                sheet.merge_range(col_name[col_num] + str(row_num) + ':' + col_name[col_num + 1] + str(row_num), str(rec.payment_term_id.name), format_number_table)
            else:
                sheet.merge_range(col_name[col_num] + str(row_num) + ':' + col_name[col_num + 1] + str(row_num), '', format_number_table)
            col_num += 2
        row_num += 1
        sheet.write('B' + str(row_num), '', format_header_table)
        sheet.write('C' + str(row_num), 'Delivery Time', format_item_table)
        sheet.merge_range('D' + str(row_num) + ':' + 'E' + str(row_num), 'b', format_number_table)
        col_num = 0
        for rec in obj.purchase_order_ids:
            if rec.delivery_time:
                sheet.merge_range(col_name[col_num] + str(row_num) + ':' + col_name[col_num + 1] + str(
                    row_num), str(rec.delivery_time), format_number_table)
            else:
                sheet.merge_range(col_name[col_num] + str(row_num) + ':' + col_name[col_num + 1] + str(row_num), '', format_number_table)
            col_num += 2
        row_num += 1
        sheet.write('B' + str(row_num), '', format_header_table)
        sheet.write('C' + str(row_num), 'Price', format_item_table)
        sheet.merge_range('D' + str(row_num) + ':' + 'E' + str(row_num), 'c', format_number_table)
        col_num = 0
        for rec in obj.purchase_order_ids:
            if rec.price:
                sheet.merge_range(col_name[col_num] + str(row_num) + ':' + col_name[col_num + 1] + str(row_num), str(rec.price), format_number_table)
            else:
                sheet.merge_range(col_name[col_num] + str(row_num) + ':' + col_name[col_num + 1] + str(row_num), '', format_number_table)
            col_num += 2
        row_num += 1
        sheet.write('B' + str(row_num), '', format_header_table)
        sheet.write('C' + str(row_num), 'Notes', format_item_table)
        sheet.merge_range('D' + str(row_num) + ':' + 'E' + str(row_num+1), '', format_number_table)
        col_num = 0
        for rec in obj.purchase_order_ids:
            if rec.price:
                sheet.merge_range(col_name[col_num] + str(row_num) + ':' + col_name[col_num + 1] + str(row_num), str(rec.notes), format_number_table)
            else:
                sheet.merge_range(col_name[col_num] + str(row_num) + ':' + col_name[col_num + 1] + str(row_num), '', format_number_table)
            col_num += 2

        row_num += 1
        sheet.write('B' + str(row_num), '', format_header_table)
        sheet.write('C' + str(row_num), '', format_item_table)
        col_num = 0

        for rec in obj.purchase_order_ids:
            sheet.merge_range(col_name[col_num] + str(row_num) + ':' + col_name[col_num + 1] + str(row_num), '', format_number_table)
            col_num += 2

        row_num += 1
        sheet.merge_range('B' + str(row_num) + ':' + col_name[(po_length * 2) - 3] + str(row_num), 'Vendor Terpilih', format_header_table)
        sheet.merge_range(col_name[(po_length * 2) - 2] + str(row_num) + ':' + col_name[(po_length * 2) - 1] + str(row_num), '', format_header_table)
        row_num += 1
        sheet.merge_range('B' + str(row_num) + ':' + col_name[(po_length * 2) - 3] + str(row_num), 'TTD Persetujuan', format_header_table)
        sheet.merge_range(col_name[(po_length * 2) - 2] + str(row_num) + ':' + col_name[(po_length * 2) - 1] + str(row_num), '', format_header_table)


# ------------------------------------------------------------------------------------------------------------------
