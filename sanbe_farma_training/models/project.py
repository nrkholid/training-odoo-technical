from odoo import _, api, fields, models

class ProjectProject(models.Model):
    _inherit = 'project.project'
    _description = 'Project'

    planning_shift_line_ids = fields.One2many('planning.slot.training', 'project_id', string='Planning Shift Line')
    planning_shift_count = fields.Integer(compute='_compute_planning_shift_count', string='Planning Shift Count')
    
    @api.depends('planning_shift_line_ids')
    def _compute_planning_shift_count(self):
        for rec in self:
            rec.planning_shift_count = len(rec.planning_shift_line_ids)
    
    def action_view_planning_shift(self):
        action = self.env['ir.actions.act_window']._for_xml_id('sanbe_farma_training.project_planning_slot_action')
        # action['domain'] = [('project_id', '=', self.id)]
        # action['context'] = {'search_default_project_id' : self.id, 'default_project_id' : self.id}
        return action
    