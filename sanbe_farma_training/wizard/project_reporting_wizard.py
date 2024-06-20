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
    template = fields.Selection([
        ('template_1', 'Template 1'),
        ('template_2', 'Template 2'),
        ('pdf', 'PDF Report'),
        ('other', 'Other Report'),
    ], string='Template', default = 'template_1')
    excel_file = fields.Binary('Excel File', readonly=True)
    wbf = {}

    def action_export_project_report(self):
        if not self.project_ids:
            raise ValidationError('Please Choose the Projects')
        if self.template not in ['pdf', 'other']:
            return self._prepare_excel_template_1()
        elif self.template == 'pdf':
            return self._prepare_pdf_report()
        else:
            return self._prepare_other_report()
    
    def _prepare_excel_template_1(self):
        fp = BytesIO()
        workbook = xlsxwriter.Workbook(fp)
        workbook = self.add_workbook_format(workbook)
        wbf = self.wbf
        column, row = 0, 0
        method = 'orm'

        for project in self.project_ids:
            worksheet = workbook.add_worksheet("{}".format(project.name))
            if self.template == 'template_2':
                self._prepare_project_report_header_template_2(worksheet, wbf, project)
                row = 4
                method = 'query'

            headercolumn = 0
            content_line, linenum = row + 1, 1
            project_report_header = self._prepare_header_values()

            for header in project_report_header:
                worksheet.write(row, headercolumn, header, wbf['header'])
                worksheet.set_column(row, headercolumn, 10 if len(header) <= 4 else 25)
                headercolumn += 1

            column_length = len(project_report_header)
            planning_shift_values = self._prepare_planning_shift_values(project, method)
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
            
            if self.template == 'template_2':
                total = sum([record['expected_revenue'] for record in planning_shift_values])
                # merge_range(0, 1, 0, 8)
                # 0 : Posisi Baris ke - 1
                # 1 : Posisi Kolom ke - A,
                # 0 : Posisi Baris ke - 1,
                # 8 : Posisi Kolom ke - I,
                worksheet.merge_range(content_line + 1, 0, content_line + 2, 6, "Total", wbf['header'])
                worksheet.write(content_line + 1, 7, total, wbf['content'])
            
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
        return ["NO", "START_DATE", "END_DATE", "SHIFT_NAME", "ROLE_NAME", "RESOURCE", "ACTUAL_PROGRESS", "EXPECTED_REVENUE"]
    
    def _prepare_planning_shift_values(self, project, method):
        if method == 'orm':
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
                    'actual_progress' : res.actual_progress,
                    'expected_revenue' : res.expected_revenue,
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
        else:
            try:
                query = """
                    SELECT 
                        TO_CHAR(pst.start_date, 'DD/MM/YYYY') as START_DATE,
                        TO_CHAR(pst.end_date, 'DD/MM/YYYY') as END_DATE,
                        pst.name AS SHIFT_NAME,
                        prt.name AS ROLE_NAME,
                        rr.name AS RESOURCE,
                        pst.actual_progress as ACTUAL_PROGRESS,
                        pst.expected_revenue as EXPECTED_REVENUE
                    FROM planning_slot_training pst
                    INNER JOIN project_project pp ON pp.id = pst.project_id
                    INNER JOIN planning_role_training prt ON prt.id = pst.role_id
                    INNER JOIN resource_resource rr ON rr.id = pst.resource_id
                    WHERE pst.project_id IN %s
                """
                self._cr.execute(query, [tuple(project.ids)])
                result = self._cr.dictfetchall()
                # {'start_date' : value, 'end_date' : value}

                # result = self._cr.fetchall()
                # (value, value, value)
                return result
            except Exception as err:
                raise ValidationError("Error : {}".format(err))
    
    def _prepare_project_report_header_template_2(self, worksheet, wbf, project):
        worksheet.merge_range("A1:H1", "PROJECT PLANNING SHIFT", wbf['header'])
        worksheet.write("A3", "Nama Project", wbf['header'])
        worksheet.write("B3", project.name, wbf['header'])
        worksheet.write("A4", "Project Manager", wbf['header'])
        worksheet.write("B4", project.user_id.name, wbf['header'])
    
    def _prepare_pdf_report(self):
        result = self.env['planning.slot.training'].search([('project_id', '=', self.project_ids.ids)])
        if not result:
            raise ValidationError('Data Not Found')
        planning_shift_ids = [record.id for record in result]
        return self.env.ref('sanbe_farma_training.action_report_planning_slot_training').report_action(planning_shift_ids)
    
    def _prepare_other_report(self):
        datas = [{
            'company_name' : record.company_id.name,
            'project_name' : record.name
        } for record in self.project_ids]
        return self.env.ref('sanbe_farma_training.action_report_planning_slot_training_query').report_action(self, data=datas)