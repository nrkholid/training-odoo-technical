from odoo import _, api, fields, models
from odoo.exceptions import ValidationError
import xlsxwriter, base64
from io import BytesIO

class BaseExcelReporting(models.AbstractModel):
    _name = 'base.excel.reporting'
    _description = 'Base Excel Reporting'
    
    def add_workbook_format(self, workbook):
        self.wbf['header'] = workbook.add_format({
            "bold" : True,
            "align" : "center",
            "font_size" : "12",
            "fg_color" : "#c9c9c9",
            "border" : 1,
            "text_wrap" : True,
        })
        self.wbf['header'].set_border()
        self.wbf['content'] = workbook.add_format()
        self.wbf['content'].set_left()
        self.wbf['content'].set_right()
        return workbook
    
    def _set_values(self, worksheet, wbf, content_line, header, column_length, vals, linenum):
        length = [number for number in range(column_length)]
        for col_length in range(column_length):
            column_name = header[col_length].lower()
            if column_name == 'no':
                worksheet.write(content_line, length[col_length], linenum, wbf['content'])
            elif column_name in vals:
                worksheet.write(content_line, length[col_length], vals[column_name], wbf['content'])

class ProjectReportingWizard(models.TransientModel):
    _name = 'project.reporting.wizard'
    _description = 'Project Reporting Wizard'
    _inherit = ['base.excel.reporting']

    project_ids = fields.Many2many('project.project', 
                                   string='Project')
    excel_file = fields.Binary('Excel File', readonly=True)
    wbf = {}

    def action_export_project_report(self):
        if not self.project_ids:
            raise ValidationError('Please Choose the Projects')
        
        fp = BytesIO()
        workbook = xlsxwriter.Workbook(fp)
        workbook = self.add_workbook_format(workbook)
        wbf = self.wbf
        column, row = 0, 0

        for project in self.project_ids:
            headercolumn = 0
            content_line, linenum = row + 1, 1
            worksheet = workbook.add_worksheet("{}".format(project.name))
            project_report_header = self._prepare_header_values()

            for header in project_report_header:
                worksheet.write(row, headercolumn, header, wbf['header'])
                worksheet.set_column(row, headercolumn, 10 if len(header) <= 4 else 25)
                headercolumn += 1

            column_length = len(project_report_header)
            planning_shift_values = self._prepare_planning_shift_values(project)
            for val in planning_shift_values:
                self._set_values(
                    worksheet,
                    wbf,
                    content_line,
                    project_report_header,
                    column_length,
                    val,
                    linenum
                )
                content_line += 1
                linenum += 1
            
            # for val in planning_shift_values:
            #     worksheet.write(content_line, 0, linenum, wbf['content'])
            #     worksheet.write(content_line, 1, val['start_date'], wbf['content'])
            #     worksheet.write(content_line, 2, val['end_date'], wbf['content'])
            #     worksheet.write(content_line, 3, val['shift_name'], wbf['content'])
            #     worksheet.write(content_line, 4, val['role_name'], wbf['content'])
            #     worksheet.write(content_line, 5, val['resource'], wbf['content'])
            #     worksheet.write(content_line, 6, val['actual_progress'], wbf['content'])
            #     content_line += 1
            #     linenum += 1

        filename = "Project Excel Reporting"
        workbook.close()
        self.excel_file = base64.encodebytes(fp.getvalue())
        fp.close()

        return {
            "type": "ir.actions.act_url",
            "url": "web/content/?model={}&field="
            "excel_file&download=true&id={}&filename={}".format(
                self._name, self.id, filename
            ),
            "target": "new",
        }
    
    def _prepare_header_values(self):
        return ["NO", "START_DATE", "END_DATE", "SHIFT_NAME", "ROLE_NAME", "RESOURCE", "ACTUAL_PROGRESS"]
    
    def _prepare_planning_shift_values(self, project):
        datas = []
        result = self.env['project.project'].browse([project.id])
        if not result : return datas
        for res in result.planning_shift_line_ids:
            datas.append({
                'start_date' : res.start_date.strftime("%d %m %Y"),
                'end_date' : res.end_date.strftime("%d %m %Y"),
                'shift_name' : res.name,
                'role_name' : res.role_id.name,
                'resource' : res.resource_id.name,
                'actual_progress' : res.actual_progress
            })
        # datas = [{
        #         'start_date' : res.start_date,
        #         'end_date' : res.end_date,
        #         'shift_name' : res.name,
        #         'role_name' : res.role_id.name,
        #         'resource' : res.resource_id.name,
        #         'actual_progress' : res.actual_progress
        #     } for res in result.planning_shift_line_ids]
        return datas

    