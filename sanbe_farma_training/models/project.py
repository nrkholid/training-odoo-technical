from odoo import _, api, fields, models

class ProjectProject(models.Model):
    _inherit = 'project.project'
    _description = 'Project'

    planning_shift_line_ids = fields.One2many('planning.slot.training', 'project_id', string='Planning Shift Line')
    planning_shift_count = fields.Integer(compute='_compute_planning_shift_count', string='Planning Shift Count')
    expected_revenue = fields.Monetary(compute='_compute_expected_revenue', 
                                       string='Expected Revenue', store = True,
                                       tracking = True, copy = False)
    total_points = fields.Integer(compute='_compute_total_points', string='Total Points',
                                  store = True, tracking = True, copy = False)
    project_actual_progress = fields.Float(compute='_compute_project_actual_progress', 
                                           string='Actual Progress')
    
    @api.depends('planning_shift_count', 'planning_shift_line_ids.actual_progress',
                 'planning_shift_line_ids.point_rate')
    def _compute_project_actual_progress(self):
        for rec in self:
            planning_shift_count = rec.planning_shift_count if rec.planning_shift_count else 1
            
            # datas = []
            # for record in rec.planning_shift_line_ids:
            #     actual_progress = record.actual_progress * record.point_rate
            #     datas.append(actual_progress)
            # project_actual_progress = round(sum(datas) / planning_shift_count, 2)
            project_actual_progress = round(sum([record.actual_progress * record.point_rate for record in rec.planning_shift_line_ids]) / planning_shift_count, 2)
            rec.project_actual_progress = project_actual_progress
        
    @api.depends('planning_shift_line_ids.total_points')
    def _compute_total_points(self):
        for rec in self:
            rec.total_points = sum(rec.planning_shift_line_ids.mapped('total_points'))
    
    @api.depends('planning_shift_line_ids.expected_revenue')
    def _compute_expected_revenue(self):
        for rec in self:
            rec.expected_revenue = sum(rec.planning_shift_line_ids.mapped('expected_revenue'))

    @api.depends('planning_shift_line_ids')
    def _compute_planning_shift_count(self):
        for rec in self:
            rec.planning_shift_count = len(rec.planning_shift_line_ids)
    
    def action_view_planning_shift(self):
        action = self.env['ir.actions.act_window']._for_xml_id('sanbe_farma_training.project_planning_slot_action')
        # action['domain'] = [('project_id', '=', self.id)]
        # action['context'] = {'search_default_project_id' : self.id, 'default_project_id' : self.id}
        return action
    