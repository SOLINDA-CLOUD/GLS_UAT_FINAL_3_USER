from odoo import _, api, fields, models
from datetime import datetime
import io
import base64

# from GLS.sol_boo.models import water_production_daily

class ReporttingBoo(models.TransientModel):
    _name = 'reporting.boo'
    _description = 'Reportting Boo'
    

    type = fields.Selection([('water_prod', 'Water Production'),('chemical_catridge', 'Chemical Catridge')], string='Type')
    warehouse_id = fields.Many2many('stock.location', string='Lokasi',domain=[("usage", "=", "internal")])
    product_ids = fields.Many2many('product.product', string='Product')
    date_from = fields.Date('Date From')
    date_to = fields.Date('Date To')

    def download_report(self):
        context = self._context
        datas = {'ids': context.get('active_ids', [])}
        datas['model'] = 'wizard.aging.report'
        datas['form'] = self.read()[0]
        for field in datas['form'].keys():
            if isinstance(datas['form'][field], tuple):
                datas['form'][field] = datas['form'][field][0]
        if self.type == 'chemical_catridge':
            return self.env.ref('sol_boo.chemical_gls_xlsx').report_action(self, data=datas)
        else:
            return self.env.ref('sol_boo.gls_xlsx').report_action(self, data=datas)

class ReportingTroubleSystem(models.TransientModel):
    _name = 'reporting.trouble.system'
    _description = 'Reporting Trouble System'

    type = fields.Selection([("backwash","Backwash"), ('grease', 'Grease'), ("cleaning","Cleaning")], string='Type')
    location_ids = fields.Many2many('stock.location', string='Lokasi',domain=[("usage", "=", "internal")])
    date_from = fields.Date('Date From')
    date_to = fields.Date('Date To')

    def download_report(self):
        context = self._context
        datas = {'ids': context.get('active_ids', [])}
        datas['model'] = 'reporting.trouble.system'
        datas['form'] = self.read()[0]
        for field in datas['form'].keys():
            if isinstance(datas['form'][field], tuple):
                datas['form'][field] = datas['form'][field][0]
        if self.type == 'backwash':
            return self.env.ref('sol_boo.backwash_xlsx').report_action(self, data=datas)
        elif self.type == 'grease':
            return self.env.ref('sol_boo.grease_xlsx').report_action(self, data=datas)
        else:
            return self.env.ref('sol_boo.cleaning_xlsx').report_action(self, data=datas)

class GlsReport(models.AbstractModel):
    _name = 'report.sol_boo.gls_report_xls.xlsx'
    _inherit = 'report.report_xlsx.abstract'

    def generate_xlsx_report(self, workbook, data, lines):
        
        format0 = workbook.add_format({'font_size': 20, 'align': 'center', 'bold': True})
        format1 = workbook.add_format({'font_size': 14, 'align': 'vcenter', 'bold': True})
        formatHeaderCompany = workbook.add_format({'font_size': 14, 'valign':'vcenter', 'align': 'center', 'bold': True})
        formatHeader = workbook.add_format({'font_size': 10, 'valign':'vcenter', 'align': 'left', 'bold': False, 'text_wrap': True})
        formatHeaderDate = workbook.add_format({'font_size': 10, 'valign':'vcenter', 'align': 'left', 'bold': False, 'text_wrap': True, 'num_format': 'dd-mm-yyyy'})        
        formatHeaderCenter = workbook.add_format({'font_size': 14, 'valign':'vcenter', 'align': 'center', 'bold': True, 'text_wrap': True})
        formatHeaderLeft = workbook.add_format({'font_size': 10, 'valign':'vcenter', 'align': 'left', 'bold': True, 'text_wrap': True})
        formatHeaderRight = workbook.add_format({'font_size': 10, 'valign':'vcenter', 'align': 'left', 'num_format': '#,##0'})
        formatHeaderTable = workbook.add_format({'font_size': 10, 'valign':'vcenter', 'align': 'centre', 'bold': True, 'bg_color':'#4ead2f', 'color':'white', 'text_wrap': True})
        formatHeaderTableRight = workbook.add_format({'font_size': 10, 'valign':'vcenter', 'align': 'right', 'bold': True, 'bg_color':'#3eaec2', 'text_wrap': True, 'num_format': '#,##0'})
        formatHeaderDetailCenter = workbook.add_format({'font_size': 10, 'valign':'vcenter', 'align': 'centre', 'text_wrap': True})
        formatHeaderDetailCenterBold = workbook.add_format({'font_size': 10, 'valign':'vcenter', 'align': 'centre', 'text_wrap': True, 'bold': True})
        formatHeaderDetailCenterNumber = workbook.add_format({'font_size': 10, 'valign':'vcenter', 'align': 'centre', 'text_wrap': True, 'num_format': '_-"Rp"* #,##0.00_-;-"Rp"* #,##0.00_-;_-"Rp"* "-"_-;_-@_-'})
        formatHeaderDetailCenterNumberBold = workbook.add_format({'font_size': 10, 'valign':'vcenter', 'align': 'centre', 'text_wrap': True, 'bold': True, 'num_format': '_-"Rp"* #,##0.00_-;-"Rp"* #,##0.00_-;_-"Rp"* "-"_-;_-@_-'})
        
        formatHeaderDetailCenterNumberDollar = workbook.add_format({'font_size': 10, 'valign':'vcenter', 'align': 'centre', 'text_wrap': True, 'num_format': '_($* #,##0.00_);_($* (#,##0.00);_($* "-"??_);_(@_)'})
        formatHeaderDetailCenterDate = workbook.add_format({'font_size': 10, 'valign':'vcenter', 'align': 'centre', 'text_wrap': True, 'num_format': 'dd-mm-yyyy'})
        formatHeaderDetailCenterNumberFour = workbook.add_format({'font_size': 10, 'valign':'vcenter', 'align': 'centre', 'text_wrap': True, 'num_format': '#,##4'})
        formatHeaderDetailLeft = workbook.add_format({'font_size': 10, 'valign':'vcenter', 'align': 'left'})
        formatHeaderDetailRight = workbook.add_format({'font_size': 10, 'valign':'vcenter', 'align': 'right', 'num_format': '#,##0'})
        format11 = workbook.add_format({'font_size': 12, 'align': 'center', 'bold': True})
        format21 = workbook.add_format({'font_size': 10, 'align': 'center', 'bold': True})
        format3 = workbook.add_format({'bottom': True, 'top': True, 'font_size': 12})
        format4 = workbook.add_format({'font_size': 12, 'align': 'left', 'bold': True})
        font_size_8 = workbook.add_format({'font_size': 8, 'align': 'center'})
        font_size_8_l = workbook.add_format({'font_size': 8, 'align': 'left'})
        font_size_8_r = workbook.add_format({'font_size': 8, 'align': 'right'})
        red_mark = workbook.add_format({'font_size': 8, 'bg_color': 'red'})
        justify = workbook.add_format({'font_size': 12})
        accounting_numformat_dolar = workbook.add_format({'num_format': '_($* #,##0.00_);_($* (#,##0.00);_($* "-"??_);_(@_)'})
        accounting_numformat_idr = workbook.add_format({'num_format': '_([$IDR] * #,##0.00_);_([$IDR] * (#,##0.00);_([$IDR] * "-"??_);_(@_)'})
        
        # Red for Due Invoices
        formatHeaderDetailCenterRed = workbook.add_format({'font_size': 10, 'valign':'vcenter', 'align': 'centre', 'text_wrap': True, 'color':'red'})
        formatHeaderDetailCenterNumberRed = workbook.add_format({'font_size': 10, 'valign':'vcenter', 'align': 'centre', 'text_wrap': True, 'num_format': '#,##0', 'color':'red'})
        formatHeaderDetailCenterDateRed = workbook.add_format({'font_size': 10, 'valign':'vcenter', 'align': 'centre', 'text_wrap': True, 'num_format': 'dd-mm-yyyy', 'color':'red'})
        formatHeaderDetailLeftRed = workbook.add_format({'font_size': 10, 'valign':'vcenter', 'align': 'left', 'color': 'red'})

        formatHeaderLocationWP = workbook.add_format({'font_size': 12, 'valign':'vcenter', 'align': 'left', 'color': 'black', 'bold': True})
        formatHeaderTableWP = workbook.add_format({'font_size': 12, 'valign':'vcenter', 'align': 'centre', 'bold': True, 'color':'black', 'text_wrap': True})
        formatYellowTableWP = workbook.add_format({'font_size': 12, 'valign':'vcenter', 'align': 'centre', 'bold': True, 'bg_color':'#e8ff80', 'color':'black', 'text_wrap': True})

        formatHeaderLocationWP.set_border(1)
        formatHeaderTableWP.set_border(1)
        formatYellowTableWP.set_border(1)
        formatHeaderCompany.set_border(1)
        formatHeaderLocationWP.set_text_wrap()
        formatHeaderTableWP.set_text_wrap()
        formatYellowTableWP.set_text_wrap()
        formatHeaderCompany.set_text_wrap()

        formatHeaderCenter.set_border(1)
        formatHeaderLeft.set_border(1)
        formatHeaderTable.set_border(1)
        formatHeaderTableRight.set_border(1)
        formatHeaderDetailCenter.set_border(1)
        formatHeaderDetailCenterDate.set_border(1)
        formatHeaderDetailCenterBold.set_border(1)

        formatHeaderTable.set_text_wrap()
        formatHeaderTableRight.set_text_wrap()
        formatHeaderDetailCenter.set_text_wrap()
        formatHeaderDetailRight.set_text_wrap()
        formatHeaderDetailLeft.set_text_wrap()
        
        # Set Column Width
        datas = data.get('form', {})
        if datas.get('type', False) and datas.get('type') == 'water_prod':
            warehouse = datas.get('warehouse_id', False)
            if warehouse:
                warehouse_ids = self.env['stock.location'].sudo().search([('id', 'in', warehouse)])
            else:
                warehouse_ids = self.env['stock.location'].sudo().search([('usage', '=', 'internal')])
            for location in warehouse_ids:
                location_id = location
                water_production_daily_ids = self.env['water.prod.daily'].sudo().search([
                    ('warehouse_id', '=', location_id.id),
                    ('date', '>=', datas.get('date_from')),
                    ('date', '<=', datas.get('date_to')),
                ], order='date asc')

                title = location_id.display_name
                sheet = workbook.add_worksheet(title)
                sheet.set_column(0, 0, 5)
                sheet.set_column(1, 1, 15)
                sheet.set_column(2, 2, 10)
                sheet.set_column(3, 3, 10)
                sheet.set_column(4, 4, 10)
                sheet.set_column(5, 5, 10)
                sheet.set_column(6, 6, 10)
                sheet.set_column(7, 7, 10)
                sheet.set_column(8, 8, 10)
                sheet.set_column(9, 9, 10)
                sheet.set_column(10, 10, 10)
                sheet.set_column(11, 11, 10)
                sheet.set_column(12, 12, 10)
                sheet.set_column(13, 13, 10)
                sheet.set_column(14, 14, 35)
                sheet.set_column(15, 15, 10)
                sheet.set_column(16, 16, 10)
                sheet.set_column(17, 17, 10)  
                sheet.set_column(17, 17, 10)

                sheet.set_row(1, 35)  
                sheet.set_row(2, 35)  
                sheet.set_row(3, 25)  

                # Header        
                if self.env.company.logo:
                    company_logo = io.BytesIO(base64.b64decode(self.env.company.logo))
                    sheet.insert_image(1, 1, "image.png", {'image_data': company_logo, 'object_position': 2, 'x_scale': 0.2, 'y_scale': 0.15, 'x_offset': 15, 'y_offset': 15})
                header_title = f'PRODUCTION REPORT \"REVERSE OSMOSIS SYSTEM\" {self.env.company.name}'
                sheet.merge_range(1, 1, 2, 14, header_title, formatHeaderCompany)
                sheet.merge_range(3, 1, 3, 14, f'Location : {title}', formatHeaderLocationWP)

                # Tabel Header
                sheet.write(4, 1, 'Tanggal', formatHeaderTableWP)
                sheet.write(4, 2, 'Konsumsi Aktual RO (m3)', formatHeaderTableWP)
                sheet.write(4, 3, 'RO Read', formatHeaderTableWP)
                sheet.write(4, 4, 'LWBP', formatHeaderTableWP)
                sheet.write(4, 5, 'LWBP Read', formatHeaderTableWP)
                sheet.write(4, 6, 'WBP', formatHeaderTableWP)
                sheet.write(4, 7, 'WBP Read', formatHeaderTableWP)
                sheet.write(4, 8, 'kWh Deep Well (kWh)', formatHeaderTableWP)
                sheet.write(4, 9, 'kWh Deep Well Read', formatHeaderTableWP)
                sheet.write(4, 10, 'kWh RO (kWh)', formatHeaderTableWP)
                sheet.write(4, 11, 'kWh RO Read', formatHeaderTableWP)
                sheet.write(4, 12, 'SEC', formatHeaderTableWP)
                sheet.write(4, 13, 'Minimum Produksi / hari', formatHeaderTableWP)
                sheet.write(4, 14, 'Remarks', formatHeaderTableWP)
                sheet.write(4, 16, 'SAIDI', formatHeaderTableWP)
                sheet.write(4, 17, 'SAIFI', formatHeaderTableWP)
                row = 5
                row_start = 6
                row_end = len(water_production_daily_ids) + 5
                row_formula = str(len(water_production_daily_ids) + 6)

                # Detail Tabel
                for wpd in water_production_daily_ids:
                    sheet.write(row, 1, wpd.date or '', formatHeaderDetailCenterDate)
                    sheet.write(row, 2, wpd.aktual_ro or '', formatHeaderDetailCenter)
                    sheet.write(row, 3, wpd.ro_read or '', formatHeaderDetailCenter)
                    sheet.write(row, 4, wpd.lwbp or '', formatHeaderDetailCenter)
                    sheet.write(row, 5, wpd.lwbp_read or '', formatHeaderDetailCenter)
                    sheet.write(row, 6, wpd.wbp or '', formatHeaderDetailCenter)
                    sheet.write(row, 7, wpd.wbp_read or '', formatHeaderDetailCenter)
                    sheet.write(row, 8, wpd.deep_well or '', formatHeaderDetailCenter)
                    sheet.write(row, 9, wpd.deep_well_read or '', formatHeaderDetailCenter)
                    sheet.write(row, 10, wpd.ro_kwh or '', formatHeaderDetailCenter)
                    sheet.write(row, 11, wpd.kwh_ro_read or '', formatHeaderDetailCenter)
                    sheet.write(row, 12, round(wpd.sec, 2) or '', formatHeaderDetailCenter)
                    sheet.write(row, 13, wpd.minimum_prod or '', formatHeaderDetailCenter)
                    sheet.write(row, 14, wpd.remarks or '', formatHeaderDetailCenter)
                    sheet.write(row, 16, wpd.saidi, formatHeaderDetailCenter)
                    sheet.write(row, 17, wpd.saifi, formatHeaderDetailCenter)
                    row += 1
                sheet.write(5, 12, '', formatHeaderDetailCenter)
                
                # Calculate
                sheet.write_formula(f'C{row_formula}', f'=SUM(C{row_start}:C{row_end})', formatHeaderDetailCenterBold)
                sheet.write_formula(f'E{row_formula}', f'=SUM(E{row_start}:E{row_end})', formatHeaderDetailCenterBold)
                sheet.write_formula(f'G{row_formula}', f'=SUM(G{row_start}:G{row_end})', formatHeaderDetailCenterBold)
                sheet.write_formula(f'I{row_formula}', f'=SUM(I{row_start}:I{row_end})', formatHeaderDetailCenterBold)
                sheet.write_formula(f'K{row_formula}', f'=SUM(K{row_start}:K{row_end})', formatHeaderDetailCenterBold)
                sheet.write_formula(f'M{row_formula}', f'=(I{row_formula}+K{row_formula})/C{row_formula}', formatHeaderDetailCenterBold)
                sheet.write_formula(f'N{row_formula}', f'=SUM(N{row_start}:N{row_end})', formatHeaderDetailCenterBold)
                sheet.write_formula(f'O{row_formula}', f'=SUM(O{row_start}:O{row_end})', formatHeaderDetailCenterBold)

                sheet.write(int(row_formula)-1, 1, 'Total', formatHeaderDetailCenterBold)
                sheet.write(int(row_formula)-1, 3, '', formatHeaderDetailCenterBold)
                sheet.write(int(row_formula)-1, 5, '', formatHeaderDetailCenterBold)
                sheet.write(int(row_formula)-1, 7, '', formatHeaderDetailCenterBold)
                sheet.write(int(row_formula)-1, 9, '', formatHeaderDetailCenterBold)
                sheet.write(int(row_formula)-1, 11, '', formatHeaderDetailCenterBold)
                sheet.write(int(row_formula)-1, 14, '', formatHeaderDetailCenterBold)
                sheet.write(int(row_formula)-1, 16, '', formatHeaderDetailCenterBold)
                sheet.write(int(row_formula)-1, 17, '', formatHeaderDetailCenterBold)

class ChemicalGlsReport(models.AbstractModel):
    _name = 'report.sol_boo.chemical_gls_report_xls.xlsx'
    _inherit = 'report.report_xlsx.abstract'

    def write_data(self, sheet, row, data, text_format):
        number_of_date = 1
        column = 3
        for i in range(31):
            get_data = data.get(number_of_date, False)
            if get_data:
                sheet.write(row, column, round(get_data, 2), text_format)
            else:
                sheet.write(row, column, f'', text_format)
            column += 1
            number_of_date += 1
        if self.env.context.get('sum', False):
            sheet.write_formula(f'AI{row+1}', f'=SUM(D{row+1}:AH{row+1})', text_format)            
        else:
            sheet.write(row, column, f'', text_format)

    def write_number_of_date(self, sheet, row, text_format):
        number_of_date = 1
        column = 3
        for i in range(31):
            sheet.write(row, column, f'{number_of_date}', text_format)
            column += 1
            number_of_date += 1
    
    def write_sisa_tangki_kg(self, sheet, row, chemical_ids, text_format):
        data = {}
        for chemical in chemical_ids:
            data[chemical.date.day] = chemical.sisa_tangki_kg
        self.write_data(sheet, row, data, text_format)

    def write_stock_awal(self, sheet, row, chemical_ids, text_format):
        data = {}
        for chemical in chemical_ids:
            data[chemical.date.day] = chemical.stock_awal
        self.write_data(sheet, row, data, text_format)

    def write_penerimaan(self, sheet, row, chemical_ids, text_format):
        data = {}
        for chemical in chemical_ids:
            data[chemical.date.day] = chemical.penerimaan
        self.write_data(sheet, row, data, text_format)

    def write_penuangan(self, sheet, row, chemical_ids, text_format):
        data = {}
        for chemical in chemical_ids:
            data[chemical.date.day] = chemical.penuangan
        self.write_data(sheet, row, data, text_format)

    def write_pemakaian(self, sheet, row, chemical_ids, text_format):
        data = {}
        for chemical in chemical_ids:
            data[chemical.date.day] = chemical.pemakaian
        self.write_data(sheet, row, data, text_format)

    def write_cleaning_basa(self, sheet, row, chemical_ids, text_format):
        data = {}
        for chemical in chemical_ids:
            data[chemical.date.day] = chemical.cleaning_basa
        self.write_data(sheet, row, data, text_format)

    def write_adj_over_loss(self, sheet, row, chemical_ids, text_format):
        data = {}
        for chemical in chemical_ids:
            data[chemical.date.day] = chemical.adj_over_loss
        self.write_data(sheet, row, data, text_format)

    def write_dosing_stroke(self, sheet, row, chemical_ids, text_format):
        data = {}
        for chemical in chemical_ids:
            data[chemical.date.day] = chemical.dosing_stroke
        self.write_data(sheet, row, data, text_format)

    def write_sisa_stock(self, sheet, row, chemical_ids, text_format):
        data = {}
        for chemical in chemical_ids:
            data[chemical.date.day] = chemical.sisa_stock
        self.write_data(sheet, row, data, text_format)

    def write_sisa_tangki(self, sheet, row, chemical_ids, text_format):
        data = {}
        for chemical in chemical_ids:
            data[chemical.date.day] = chemical.sisa_tangki
        self.write_data(sheet, row, data, text_format)

    def write_dosing_stroke_percent(self, sheet, row, chemical_ids, text_format):
        data = {}
        for chemical in chemical_ids:
            data[chemical.date.day] = chemical.dosing_stroke_percent
        self.write_data(sheet, row, data, text_format)
    
    def generate_xlsx_report(self, workbook, data, lines):
        
        format0 = workbook.add_format({'font_size': 20, 'align': 'center', 'bold': True})
        format1 = workbook.add_format({'font_size': 14, 'align': 'vcenter', 'bold': True})
        formatHeaderCompany = workbook.add_format({'font_size': 14, 'align': 'center', 'bold': True})
        formatHeader = workbook.add_format({'font_size': 10, 'valign':'vcenter', 'align': 'left', 'bold': False, 'text_wrap': True})
        formatHeaderDate = workbook.add_format({'font_size': 10, 'valign':'vcenter', 'align': 'left', 'bold': False, 'text_wrap': True, 'num_format': 'dd-mm-yyyy'})        
        formatHeaderCenter = workbook.add_format({'font_size': 14, 'valign':'vcenter', 'align': 'center', 'bold': True, 'text_wrap': True})
        formatHeaderLeft = workbook.add_format({'font_size': 10, 'valign':'vcenter', 'align': 'left', 'bold': True, 'text_wrap': True})
        formatHeaderRight = workbook.add_format({'font_size': 10, 'valign':'vcenter', 'align': 'left', 'num_format': '#,##0'})
        formatHeaderTable = workbook.add_format({'font_size': 10, 'valign':'vcenter', 'align': 'centre', 'bold': True, 'bg_color':'#4ead2f', 'color':'white', 'text_wrap': True})
        formatHeaderTableRight = workbook.add_format({'font_size': 10, 'valign':'vcenter', 'align': 'right', 'bold': True, 'bg_color':'#3eaec2', 'text_wrap': True, 'num_format': '#,##0'})
        formatHeaderDetailCenter = workbook.add_format({'font_size': 10, 'valign':'vcenter', 'align': 'centre', 'text_wrap': True})
        formatHeaderDetailCenterBold = workbook.add_format({'font_size': 10, 'valign':'vcenter', 'align': 'centre', 'text_wrap': True, 'bold': True})
        formatHeaderDetailCenterNumber = workbook.add_format({'font_size': 10, 'valign':'vcenter', 'align': 'centre', 'text_wrap': True, 'num_format': '_-"Rp"* #,##0.00_-;-"Rp"* #,##0.00_-;_-"Rp"* "-"_-;_-@_-'})
        formatHeaderDetailCenterNumberBold = workbook.add_format({'font_size': 10, 'valign':'vcenter', 'align': 'centre', 'text_wrap': True, 'bold': True, 'num_format': '_-"Rp"* #,##0.00_-;-"Rp"* #,##0.00_-;_-"Rp"* "-"_-;_-@_-'})
        
        formatHeaderDetailCenterNumberDollar = workbook.add_format({'font_size': 10, 'valign':'vcenter', 'align': 'centre', 'text_wrap': True, 'num_format': '_($* #,##0.00_);_($* (#,##0.00);_($* "-"??_);_(@_)'})
        formatHeaderDetailCenterDate = workbook.add_format({'font_size': 10, 'valign':'vcenter', 'align': 'centre', 'text_wrap': True, 'num_format': 'dd-mm-yyyy'})
        formatHeaderDetailCenterNumberFour = workbook.add_format({'font_size': 10, 'valign':'vcenter', 'align': 'centre', 'text_wrap': True, 'num_format': '#,##4'})
        formatHeaderDetailLeft = workbook.add_format({'font_size': 10, 'valign':'vcenter', 'align': 'left'})
        formatHeaderDetailRight = workbook.add_format({'font_size': 10, 'valign':'vcenter', 'align': 'right', 'num_format': '#,##0'})
        format11 = workbook.add_format({'font_size': 12, 'align': 'center', 'bold': True})
        format21 = workbook.add_format({'font_size': 10, 'align': 'center', 'bold': True})
        format3 = workbook.add_format({'bottom': True, 'top': True, 'font_size': 12})
        format4 = workbook.add_format({'font_size': 12, 'align': 'left', 'bold': True})
        font_size_8 = workbook.add_format({'font_size': 8, 'align': 'center'})
        font_size_8_l = workbook.add_format({'font_size': 8, 'align': 'left'})
        font_size_8_r = workbook.add_format({'font_size': 8, 'align': 'right'})
        red_mark = workbook.add_format({'font_size': 8, 'bg_color': 'red'})
        justify = workbook.add_format({'font_size': 12})
        accounting_numformat_dolar = workbook.add_format({'num_format': '_($* #,##0.00_);_($* (#,##0.00);_($* "-"??_);_(@_)'})
        accounting_numformat_idr = workbook.add_format({'num_format': '_([$IDR] * #,##0.00_);_([$IDR] * (#,##0.00);_([$IDR] * "-"??_);_(@_)'})
        
        # Red for Due Invoices
        formatHeaderDetailCenterRed = workbook.add_format({'font_size': 10, 'valign':'vcenter', 'align': 'centre', 'text_wrap': True, 'color':'red'})
        formatHeaderDetailCenterNumberRed = workbook.add_format({'font_size': 10, 'valign':'vcenter', 'align': 'centre', 'text_wrap': True, 'num_format': '#,##0', 'color':'red'})
        formatHeaderDetailCenterDateRed = workbook.add_format({'font_size': 10, 'valign':'vcenter', 'align': 'centre', 'text_wrap': True, 'num_format': 'dd-mm-yyyy', 'color':'red'})
        formatHeaderDetailLeftRed = workbook.add_format({'font_size': 10, 'valign':'vcenter', 'align': 'left', 'color': 'red'})

        formatHeaderLocationChemical = workbook.add_format({'font_size': 14, 'align': 'center', 'bg_color':'#f0bb80', 'color': 'black', 'bold': True})
        formatHeaderTableChemical = workbook.add_format({'font_size': 10, 'valign':'vcenter', 'align': 'centre', 'bold': True, 'color':'black', 'text_wrap': True})
        formatYellowTableChemical = workbook.add_format({'font_size': 10, 'valign':'vcenter', 'align': 'centre', 'bold': True, 'bg_color':'#e8ff80', 'color':'black', 'text_wrap': True})

        formatHeaderTableChemical.set_border(2)
        formatYellowTableChemical.set_border(2)
        formatHeaderTableChemical.set_text_wrap()
        formatYellowTableChemical.set_text_wrap()

        formatHeaderCenter.set_border(1)
        formatHeaderLeft.set_border(1)
        formatHeaderTable.set_border(1)
        formatHeaderTableRight.set_border(1)
        formatHeaderDetailCenter.set_border(1)
        formatHeaderDetailCenterDate.set_border(1)
        formatHeaderDetailCenterBold.set_border(1)

        formatHeaderTable.set_text_wrap()
        formatHeaderTableRight.set_text_wrap()
        formatHeaderDetailCenter.set_text_wrap()
        formatHeaderDetailRight.set_text_wrap()
        formatHeaderDetailLeft.set_text_wrap()
        
        # Set Column Width
        datas = data.get('form', {})      
        if datas.get('type', False) and datas.get('type') == 'chemical_catridge':
            len_day = datetime.strptime(datas.get('date_to'), '%Y-%m-%d').day
            warehouse = datas.get('warehouse_id', False)
            if warehouse:
                warehouse_ids = self.env['stock.location'].sudo().search([('id', 'in', warehouse)])
            else:
                warehouse_ids = self.env['stock.location'].sudo().search([('usage', '=', 'internal')])
            product = datas.get('product_ids', False)
            if product:
                product_ids = self.env['product.product'].sudo().search([('id', 'in', product)])
            else:
                product_ids = self.env['product.product'].sudo().search([])
            for location in warehouse_ids:
                location_id = location

                title = location_id.display_name
                sheet = workbook.add_worksheet(title)

                sheet.set_column(0, 0, 5)
                sheet.set_column(1, 1, 20)
                sheet.set_column(2, 2, 10)

                # Header
                header_title = f'{self.env.company.name}'
                sheet.merge_range(1, 0, 1, 3, header_title, formatHeaderCompany)
                sheet.merge_range(1, 11, 1, 25, f'Location : {title}', formatHeaderLocationChemical)

                # Tabel Header
                row = 4
                for product in product_ids:
                    chemical_ids = self.env['chemical.catridge'].sudo().search([
                        ('product_id', '=', product.id),
                        ('warehouse_id', '=', location_id.id),
                        ('date', '>=', datas.get('date_from')),
                        ('date', '<=', datas.get('date_to')),
                    ], order='date asc')
                    sheet.merge_range(row, 1, row, 2, f'Sisa di Tangki', formatHeaderTableChemical)
                    self.write_sisa_tangki_kg(sheet, row, chemical_ids, formatHeaderDetailCenter)
                    row += 1

                    sheet.merge_range(row, 1, row+1, 2, f'{product.name}', formatHeaderTableChemical)
                    sheet.merge_range(row, 34, row+1, 34, f'Total', formatHeaderTableChemical)
                    sheet.merge_range(row, 3, row, 33, f'Tanggal', formatHeaderTableChemical)
                    row += 1
                    self.write_number_of_date(sheet, row, formatHeaderTableChemical)
                    row += 1

                    sheet.merge_range(row, 1, row, 2, f'Stock Awal ({product.uom_id.name if product.uom_id else ""})', formatHeaderTableChemical)
                    self.write_stock_awal(sheet, row, chemical_ids, formatHeaderDetailCenter)
                    row += 1

                    sheet.merge_range(row, 1, row, 2, f'Penerimaan ({product.uom_id.name if product.uom_id else ""})', formatHeaderTableChemical)
                    self.write_penerimaan(sheet, row, chemical_ids, formatHeaderDetailCenter)
                    row += 1

                    sheet.merge_range(row, 1, row, 2, f'Penuangan ({product.uom_id.name if product.uom_id else ""})', formatHeaderTableChemical)
                    self.write_penuangan(sheet, row, chemical_ids, formatHeaderDetailCenter)
                    row += 1

                    # sheet.merge_range(row, 1, row, 2, f'Pemakaian ({product.uom_id.name if product.uom_id else ""})', formatHeaderTableChemical)
                    sheet.write(row, 1, f'Pemakaian ({product.uom_id.name if product.uom_id else ""})', formatHeaderTableChemical)
                    sheet.write(row, 2, location_id.chemical_catridge_usage, formatYellowTableChemical)
                    self.with_context(sum=True).write_pemakaian(sheet, row, chemical_ids, formatHeaderDetailCenter)
                    row += 1

                    sheet.merge_range(row, 1, row, 2, f'Pemakaian Cleaning Basa ({product.uom_id.name if product.uom_id else ""})', formatHeaderTableChemical)
                    self.write_cleaning_basa(sheet, row, chemical_ids, formatHeaderDetailCenter)
                    row += 1

                    sheet.merge_range(row, 1, row, 2, f'Adjustment Over/Loss ({product.uom_id.name if product.uom_id else ""})', formatHeaderTableChemical)
                    self.write_adj_over_loss(sheet, row, chemical_ids, formatHeaderDetailCenter)
                    row += 1

                    sheet.merge_range(row, 1, row, 2, f'Dosing Stoke ({product.uom_id.name if product.uom_id else ""})', formatHeaderTableChemical)
                    self.write_dosing_stroke(sheet, row, chemical_ids, formatHeaderDetailCenter)
                    row += 1

                    sheet.merge_range(row, 1, row, 2, f'Sisa Stock ({product.uom_id.name if product.uom_id else ""})', formatHeaderTableChemical)
                    self.write_sisa_stock(sheet, row, chemical_ids, formatHeaderDetailCenter)
                    row += 1

                    sheet.merge_range(row, 1, row, 2, f'Sisa Pada Tangki (%)', formatYellowTableChemical)
                    self.write_sisa_tangki(sheet, row, chemical_ids, formatYellowTableChemical)
                    row += 1

                    sheet.merge_range(row, 1, row, 2, f'Dosing Stoke (%)', formatYellowTableChemical)
                    self.write_dosing_stroke_percent(sheet, row, chemical_ids, formatYellowTableChemical)
                    row += 2

ROW_YEARLY_1 = [
    'Januari',
    'Februari',
    'Maret',
    'April',
    'Mei',
    'Juni',
    ]
ROW_YEARLY_2 = [
    'Juli',
    'Agustus',
    'September',
    'Oktober',
    'November',
    'Desember',
    ]
class BackwashReport(models.AbstractModel):
    _name = 'report.sol_boo.backwash_report_xls.xlsx'
    _inherit = 'report.report_xlsx.abstract'

    def generate_xlsx_report(self, workbook, data, lines):
        formatHeaderCompany = workbook.add_format({'font_size': 14, 'valign':'vcenter', 'align': 'center', 'bold': True})
        formatSubTitle = workbook.add_format({'font_size': 12, 'valign':'vcenter', 'align': 'left', 'bold': False})
        formatHeaderTable = workbook.add_format({'font_size': 12, 'valign':'vcenter', 'align': 'center', 'bold': True})
        formatSubHeaderTable = workbook.add_format({'font_size': 12, 'valign':'vcenter', 'align': 'center', 'bold': False})
        formatDetailTable = workbook.add_format({'font_size': 12, 'valign':'vcenter', 'align': 'center', 'bold': False})
        formatDetailTableRed = workbook.add_format({'font_size': 12, 'valign':'vcenter', 'align': 'center', 'bold': False, 'bg_color':'red'})
        formatDetailTableBlack = workbook.add_format({'font_size': 12, 'valign':'vcenter', 'align': 'center', 'bold': False, 'bg_color':'black'})

        # formatHeaderCompany.set_border(1)
        formatHeaderTable.set_border(1)
        formatSubHeaderTable.set_border(1)
        formatDetailTable.set_border(1)
        formatDetailTableRed.set_border(1)
        formatDetailTableBlack.set_border(1)

        # formatHeaderCompany.set_text_wrap()
        formatHeaderTable.set_text_wrap()
        formatSubHeaderTable.set_text_wrap()
        formatDetailTable.set_text_wrap()
        formatDetailTableRed.set_text_wrap()
        formatDetailTableBlack.set_text_wrap()

        datas = data.get('form', {})
        ln = datas.get('location_ids', False)
        if ln:
            location_ids = self.env['stock.location'].sudo().search([('id', 'in', ln)])
        else:
            location_ids = self.env['stock.location'].sudo().search([('usage', '=', 'internal')])
        for location in location_ids:
            location_id = location
            trouble_system_ids = self.env['shutdown.system'].sudo().search([
                ('warehouse_id', '=', location_id.id),
                ('type', '=', 'backwash'),
                ('time', '>=', datas.get('date_from')),
                ('time', '<=', datas.get('date_to')),
            ], order='time asc')
            marker = {}
            for ts in trouble_system_ids:
                if ts.time.month not in marker.keys():
                    marker[ts.time.month] = []
                marker[ts.time.month].append(ts.time.day)

            title = location_id.display_name
            sheet = workbook.add_worksheet(title)

            sheet.set_column(0, 0, 5)
            sheet.set_column(1, 1, 15)

            header_title = 'Monitoring Pelaksanaan Backwash Media Filter'
            sheet.merge_range(1, 0, 2, 32, header_title, formatHeaderCompany)
            sub_title = f'Lokasi : {location_id.display_name}'
            sheet.merge_range(3, 1, 3, 3, sub_title, formatSubTitle)

            sheet.merge_range(4, 0, 5, 0, 'No', formatHeaderTable)
            sheet.merge_range(4, 1, 5, 1, 'Bulan', formatHeaderTable)
            sheet.merge_range(4, 2, 4, 32, 'Tanggal Backwash Media Filter', formatHeaderTable)
            
            column_subheader = 2
            for seq_header in range(1, 32):
                sheet.set_column(column_subheader, column_subheader, 5)
                sheet.write(5, column_subheader, str(seq_header), formatSubHeaderTable)
                column_subheader += 1
            
            row = 6
            month_number = 1
            months = ROW_YEARLY_1+ROW_YEARLY_2
            empty_date = {2: [29, 30, 31], 4: [31], 6: [31], 9: [31], 11: [31]}
            for month in months:
                sheet.set_row(row, 25) 
                sheet.write(row, 0, month_number, formatDetailTable)
                sheet.write(row, 1, month, formatDetailTable)
                for i in range(1, 32):
                    if marker.get(month_number, False) and i in marker[month_number]:
                        sheet.write(row, i+1, '', formatDetailTableRed)
                    elif empty_date.get(month_number, False) and i in empty_date[month_number]:
                        sheet.write(row, i+1, '', formatDetailTableBlack)
                    else:
                        sheet.write(row, i+1, '', formatDetailTable)
                row += 1
                month_number += 1


class GreaseReport(models.AbstractModel):
    _name = 'report.sol_boo.grease_report_xls.xlsx'
    _inherit = 'report.report_xlsx.abstract'

    def generate_xlsx_report(self, workbook, data, lines):
        formatHeaderCompany = workbook.add_format({'font_size': 14, 'valign':'vcenter', 'align': 'center', 'bold': True})
        formatSubTitle = workbook.add_format({'font_size': 12, 'valign':'vcenter', 'align': 'left', 'bold': False})
        formatHeaderTable = workbook.add_format({'font_size': 12, 'valign':'vcenter', 'align': 'center', 'bold': True})
        formatSubHeaderTable = workbook.add_format({'font_size': 12, 'valign':'vcenter', 'align': 'center', 'bold': False})
        formatDetailTable = workbook.add_format({'font_size': 12, 'valign':'vcenter', 'align': 'center', 'bold': False})
        formatDetailTableRed = workbook.add_format({'font_size': 12, 'valign':'vcenter', 'align': 'center', 'bold': False, 'bg_color':'red'})
        formatDetailTableBlack = workbook.add_format({'font_size': 12, 'valign':'vcenter', 'align': 'center', 'bold': False, 'bg_color':'black'})

        # formatHeaderCompany.set_border(1)
        formatHeaderTable.set_border(1)
        formatSubHeaderTable.set_border(1)
        formatDetailTable.set_border(1)
        formatDetailTableRed.set_border(1)
        formatDetailTableBlack.set_border(1)

        # formatHeaderCompany.set_text_wrap()
        formatHeaderTable.set_text_wrap()
        formatSubHeaderTable.set_text_wrap()
        formatDetailTable.set_text_wrap()
        formatDetailTableRed.set_text_wrap()
        formatDetailTableBlack.set_text_wrap()

        datas = data.get('form', {})
        ln = datas.get('location_ids', False)
        if ln:
            location_ids = self.env['stock.location'].sudo().search([('id', 'in', ln)])
        else:
            location_ids = self.env['stock.location'].sudo().search([('usage', '=', 'internal')])
        for location in location_ids:
            location_id = location
            trouble_system_ids = self.env['shutdown.system'].sudo().search([
                ('warehouse_id', '=', location_id.id),
                ('type', '=', 'grease'),
                ('time', '>=', datas.get('date_from')),
                ('time', '<=', datas.get('date_to')),
            ], order='time asc')
            marker = {}
            for ts in trouble_system_ids:
                if ts.time.month not in marker.keys():
                    marker[ts.time.month] = []
                marker[ts.time.month].append(ts.time.day)

            title = location_id.display_name
            sheet = workbook.add_worksheet(title)

            sheet.set_column(0, 0, 5)
            sheet.set_column(1, 1, 15)

            header_title = 'Monitoring Penggunaan Grease'
            sheet.merge_range(1, 0, 2, 32, header_title, formatHeaderCompany)
            sub_title = f'Lokasi : {location_id.display_name}'
            sheet.merge_range(3, 1, 3, 3, sub_title, formatSubTitle)

            sheet.merge_range(4, 0, 5, 0, 'No', formatHeaderTable)
            sheet.merge_range(4, 1, 5, 1, 'Bulan', formatHeaderTable)
            sheet.merge_range(4, 2, 4, 32, 'Tanggal Grease Usage', formatHeaderTable)
            
            column_subheader = 2
            for seq_header in range(1, 32):
                sheet.set_column(column_subheader, column_subheader, 5)
                sheet.write(5, column_subheader, str(seq_header), formatSubHeaderTable)
                column_subheader += 1
            
            row = 6
            month_number = 1
            months = ROW_YEARLY_1+ROW_YEARLY_2
            empty_date = {2: [29, 30, 31], 4: [31], 6: [31], 9: [31], 11: [31]}
            for month in months:
                sheet.set_row(row, 25) 
                sheet.write(row, 0, month_number, formatDetailTable)
                sheet.write(row, 1, month, formatDetailTable)
                for i in range(1, 32):
                    if marker.get(month_number, False) and i in marker[month_number]:
                        sheet.write(row, i+1, '', formatDetailTableRed)
                    elif empty_date.get(month_number, False) and i in empty_date[month_number]:
                        sheet.write(row, i+1, '', formatDetailTableBlack)
                    else:
                        sheet.write(row, i+1, '', formatDetailTable)
                row += 1
                month_number += 1



class CleaningReport(models.AbstractModel):
    _name = 'report.sol_boo.cleaning_report_xls.xlsx'
    _inherit = 'report.report_xlsx.abstract'

    def generate_xlsx_report(self, workbook, data, lines):
        formatHeaderCompany = workbook.add_format({'font_size': 14, 'valign':'vcenter', 'align': 'center', 'bold': True})
        formatSubTitle = workbook.add_format({'font_size': 12, 'valign':'vcenter', 'align': 'left', 'bold': False})
        formatHeaderTable = workbook.add_format({'font_size': 12, 'valign':'vcenter', 'align': 'center', 'bold': True})
        formatSubHeaderTable = workbook.add_format({'font_size': 10, 'valign':'vcenter', 'align': 'center', 'bold': True})
        formatDetailTable = workbook.add_format({'font_size': 12, 'valign':'vcenter', 'align': 'center', 'bold': False})
        formatDetailTableRed = workbook.add_format({'font_size': 12, 'valign':'vcenter', 'align': 'center', 'bold': True, 'bg_color':'red'})
        formatDetailTableBlack = workbook.add_format({'font_size': 12, 'valign':'vcenter', 'align': 'center', 'bold': False, 'bg_color':'black'})

        # formatHeaderCompany.set_border(1)
        formatHeaderTable.set_border(1)
        formatSubHeaderTable.set_border(1)
        formatDetailTable.set_border(1)
        formatDetailTableRed.set_border(1)
        formatDetailTableBlack.set_border(1)

        # formatHeaderCompany.set_text_wrap()
        formatHeaderTable.set_text_wrap()
        formatSubHeaderTable.set_text_wrap()
        formatDetailTable.set_text_wrap()
        formatDetailTableRed.set_text_wrap()
        formatDetailTableBlack.set_text_wrap()

        datas = data.get('form', {})
        ln = datas.get('location_ids', False)
        year_title = []
        if ln:
            location_ids = self.env['stock.location'].sudo().search([('id', 'in', ln)])
        else:
            location_ids = self.env['stock.location'].sudo().search([('usage', '=', 'internal')])
        if len(location_ids) > 1:
            trouble_system_ids = self.env['shutdown.system'].sudo().search([
                ('warehouse_id', 'in', location_ids.ids),
                ('type', '=', 'cleaning'),
                ('time', '>=', datas.get('date_from')),
                ('time', '<=', datas.get('date_to')),
            ], order='time asc')
        else:
            trouble_system_ids = self.env['shutdown.system'].sudo().search([
                ('warehouse_id', '=', location_ids.id),
                ('type', '=', 'cleaning'),
                ('time', '>=', datas.get('date_from')),
                ('time', '<=', datas.get('date_to')),
            ], order='time asc')
        marker = {}
        for ts in trouble_system_ids:
            if ts.time.year not in year_title:
                year_title.append(ts.time.year)
            if ts.warehouse_id and ts.warehouse_id.id not in marker.keys():
                marker[ts.warehouse_id.id] = {}
            if ts.time and ts.time.year not in marker[ts.warehouse_id.id].keys():
                marker[ts.warehouse_id.id][ts.time.year] = {}
            if ts.time and ts.time.month not in marker[ts.warehouse_id.id][ts.time.year].keys():
                marker[ts.warehouse_id.id][ts.time.year][ts.time.month] = []
            marker[ts.warehouse_id.id][ts.time.year][ts.time.month].append(ts.time.day)

        for year in year_title:
            string_year = str(year)
            title = string_year
            sheet = workbook.add_worksheet(title)

            sheet.set_column(0, 0, 5)
            sheet.set_column(1, 1, 15)

            header_title = f'Jadwal Pelaksanaan Cleaning Membrane Reverse Osmosis Tahun {string_year}'
            sheet.merge_range(1, 0, 2, 25, header_title, formatHeaderCompany)
            week1 = [k for k in range(1,8)]
            week2 = [k for k in range(8,17)]
            week3 = [k for k in range(17,25)]
            week4 = [k for k in range(25,32)]
            row = 4
            sheet.merge_range(row, 0, row+2, 0, 'No', formatHeaderTable)
            sheet.merge_range(row, 1, row+2, 1, 'Lokasi Hotel', formatHeaderTable)

            column = 2
            month_number = 1
            for month in ROW_YEARLY_1:
                sheet.merge_range(row, column, row, column+3, month, formatHeaderTable)
                sheet.merge_range(row+1, column, row+1, column+3, 'Minggu', formatSubHeaderTable)
                for i in range(1, 5):
                    sheet.set_column(column, column, 5)
                    sheet.write(row+2, column, i, formatSubHeaderTable)
                    column += 1
                month_number += 1

            row += 3
            location_number = 1
            for location in location_ids:
                sheet.set_row(row, 20)
                column = 0
                sheet.write(row, column, location_number, formatDetailTable)
                sheet.write(row, column+1, location.display_name, formatDetailTable)
                column += 2
                for i in range(1, 7):
                    if marker.get(location.id, False) and marker[location.id].get(year, False) and marker[location.id][year].get(i, False):
                        for j in marker[location.id][year][i]:
                            if j in week1:
                                sheet.write(row, column, j, formatDetailTableRed)
                            else:
                                sheet.write(row, column, '', formatDetailTable)
                            if j in week2:
                                sheet.write(row, column+1, j, formatDetailTableRed)
                            else:
                                sheet.write(row, column+1, '', formatDetailTable)
                            if j in week3:
                                sheet.write(row, column+2, j, formatDetailTableRed)
                            else:
                                sheet.write(row, column+2, '', formatDetailTable)
                            if j in week4:
                                sheet.write(row, column+3, j, formatDetailTableRed)
                            else:
                                sheet.write(row, column+3, '', formatDetailTable)
                    else:
                        sheet.write(row, column, '', formatDetailTable)
                        sheet.write(row, column+1, '', formatDetailTable)
                        sheet.write(row, column+2, '', formatDetailTable)
                        sheet.write(row, column+3, '', formatDetailTable)
                    column += 4
                row += 1
                location_number += 1
            
            row += 2
            sheet.merge_range(row, 0, row+2, 0, 'No', formatHeaderTable)
            sheet.merge_range(row, 1, row+2, 1, 'Lokasi Hotel', formatHeaderTable)
            column = 2
            month_number = 7
            for month in ROW_YEARLY_2:
                sheet.merge_range(row, column, row, column+3, month, formatHeaderTable)
                sheet.merge_range(row+1, column, row+1, column+3, 'Minggu', formatSubHeaderTable)
                for i in range(1, 5):
                    sheet.set_column(column, column, 5)
                    sheet.write(row+2, column, i, formatSubHeaderTable)
                    column += 1
                month_number += 1
            
            row += 3
            location_number = 1
            for location in location_ids:
                sheet.set_row(row, 20)
                column = 0
                sheet.write(row, column, location_number, formatDetailTable)
                sheet.write(row, column+1, location.display_name, formatDetailTable)
                column += 2
                for i in range(7, 13):
                    if marker.get(location.id, False) and marker[location.id].get(year, False) and marker[location.id][year].get(i, False):
                        for j in marker[location.id][year][i]:
                            if j in week1:
                                sheet.write(row, column, j, formatDetailTableRed)
                            else:
                                sheet.write(row, column, '', formatDetailTable)
                            if j in week2:
                                sheet.write(row, column+1, j, formatDetailTableRed)
                            else:
                                sheet.write(row, column+1, '', formatDetailTable)
                            if j in week3:
                                sheet.write(row, column+2, j, formatDetailTableRed)
                            else:
                                sheet.write(row, column+2, '', formatDetailTable)
                            if j in week4:
                                sheet.write(row, column+3, j, formatDetailTableRed)
                            else:
                                sheet.write(row, column+3, '', formatDetailTable)
                    else:
                        sheet.write(row, column, '', formatDetailTable)
                        sheet.write(row, column+1, '', formatDetailTable)
                        sheet.write(row, column+2, '', formatDetailTable)
                        sheet.write(row, column+3, '', formatDetailTable)
                    column += 4
                row += 1
                location_number += 1