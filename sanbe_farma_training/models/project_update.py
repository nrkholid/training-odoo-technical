from odoo import _, api, fields, models
from dateutil.relativedelta import relativedelta

class ProjectUpdate(models.Model):
    _inherit = 'project.update'
    _description = 'Project Update'
    
    def _get_default_line_ids(self):
        res = []
        if 'active_model' in self._context and \
            not 'project.project' in self._context.get('active_model'):
            return res
        project_id = [self.project_id.id] if self.project_id else self._context.get('active_ids')
        result = self.env['project.project'].browse(project_id)
        if not result: return res
        for record in result:
            if not record.planning_shift_line_ids: return res
            result = self._prepare_values(record, self.date)
        return res + result
    
    def _prepare_values(self, record, date=False):
        res = []
        for rec in record.planning_shift_line_ids:
            line_ids = rec.line_ids.filtered(lambda r : r.state == 'confirm')
            update_line_ids = line_ids.sorted(key= lambda r : (r.date, r.id))[-1] if line_ids else []
            date_condition = False if (not date) or (not update_line_ids) else bool(update_line_ids.date > date)
            previous_progress = 0.0 if update_line_ids and date_condition else update_line_ids.current_progress if update_line_ids else 0.0
            res.append((0, 0, {
                'slot_training_id' : rec.id,
                'state' : 'draft',
                'previous_progress' : previous_progress,
                'current_progress' : previous_progress,
            }))
        return res

    line_ids = fields.One2many('planning.slot.training.line', 
                            'project_update_id', string='Line IDS',
                            default=_get_default_line_ids)

    def action_confirm_updates(self):
        self.line_ids.write({'state' : 'confirm'})
        return True
    
    def action_reset_to_draft_updates(self):
        self.line_ids.write({'state' : 'draft'})
        return True
