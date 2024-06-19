from odoo import _, api, fields, models


class PlanningSlotTraining(models.Model):
    _name = 'planning.slot.training'
    _description = 'Planning Slot Training'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    
    name = fields.Char('Description')
    role_id = fields.Many2one('planning.role.training', string='Role', index = True,
                              copy = False, tracking = True, check_company=True)
    resource_id = fields.Many2one('resource.resource', string='Resource', index = True,
                                copy = False, tracking = True, check_company=True)
    resource_ids = fields.Many2many('resource.resource', string='Resource',
                                    compute='_compute_resource_ids')
    company_id = fields.Many2one('res.company', string='Company', index = True, default=lambda self: self.env.company,
                                 copy = False, required=True)
    currency_id = fields.Many2one('res.currency', string='Currency', related='company_id.currency_id',
                                  store = True)
    start_date = fields.Date('Start Date', default=lambda self: fields.Date.context_today(self))
    end_date = fields.Date('End Date', default=lambda self:fields.Date.context_today(self))
    state = fields.Selection([
        ('draft', 'Draft'),
        ('to_approve', 'To Approve'),
        ('approved', 'Approved')
    ], string='State', default='draft')
    number_of_mandays = fields.Integer(compute='_compute_number_of_mandays',
                                    string='Number of Mandays', store = True)
    point_rate = fields.Integer(compute='_compute_role_components', 
                                string='Point Rate', store = True)
    amount = fields.Monetary('Amount', compute='_compute_role_components', store = True,
                             curreny_field='currency_id')
    total_points = fields.Integer(compute='_compute_total_points', 
                                  string='Total Points', store = True)
    expected_revenue = fields.Monetary(compute='_compute_expected_revenue', 
                                       string='Expected Revenue', store = True,
                                       currency_field='currency_id', groups="sanbe_farma_training.groups_planning_shift_approver")
    line_ids = fields.One2many('planning.slot.training.line', 'slot_training_id', string='Line')
    actual_progress = fields.Float(compute='_compute_actual_progress', string='Actual Progress', 
                                store = True)
    project_id = fields.Many2one('project.project', string='Project',
                                index=True, copy = False, tracking = True)
    actual_revenue = fields.Monetary(compute='_compute_actual_revenue', string='Actual Revenue', store = True,
                                     currency_field='currency_id', groups="sanbe_farma_training.groups_planning_shift_approver")

    @api.depends('expected_revenue', 'actual_progress')
    def _compute_actual_revenue(self):
        for rec in self:
            rec.actual_revenue = rec.expected_revenue * rec.actual_progress / 100
            
    """
        Compute Actual Progress berdasarkan nilai Current Progress dan State Line IDS
        dimana Value Actual Progress yang diambil adalah Data Terupdate berdasarkan
        Tanggal dan ID yang dilakukan secara filtered kemudian disort
    """
    @api.depends('line_ids', 'line_ids.current_progress', 'line_ids.state')
    def _compute_actual_progress(self):
        for rec in self:
            if rec.line_ids:
                line_ids = rec.line_ids.filtered(lambda x : x.state == 'confirm' and x.current_progress > 0)
                actual_progress = line_ids.sorted(key = lambda x : (x.date, x.id))[-1].current_progress \
                    if line_ids else 0
                rec.actual_progress = actual_progress
            else:
                rec.actual_progress = 0

    """
        Compute Expected Revenue berdasarkan Number of Mandays dikali Amount dimana
        Number of Mandays berasal dari selisih Start Date dan End Date, sedangkan
        Amount berasal dari Amount yang telah ditentukan di Role ID
    """
    @api.depends('number_of_mandays', 'amount')
    def _compute_expected_revenue(self):
        for rec in self:
            if rec.number_of_mandays and rec.amount:
                rec.expected_revenue = rec.number_of_mandays * rec.amount
            else:
                rec.expected_revenue = 0
    
    """
        Compute Expected Revenue berdasarkan Number of Mandays dikali Point Rate dimana
        Number of Mandays berasal dari selisih Start Date dan End Date, sedangkan
        Point Rate berasal dari Point Rate yang telah ditentukan di Role ID
    """
    @api.depends('number_of_mandays', 'point_rate')
    def _compute_total_points(self):
        for rec in self:
            if rec.number_of_mandays and rec.point_rate:
                rec.total_points = rec.number_of_mandays * rec.point_rate
            else:
                rec.total_points = 0
    
    """
        Compute yang digunakan untuk menentukan 
        Nilai Point Rate dan Amount berdasarkan Role ID
        yang dipilih
    """
    @api.depends('role_id')
    def _compute_role_components(self):
        for rec in self:
            if rec.role_id:
                rec.point_rate = rec.role_id.point_rate
                rec.amount = rec.role_id.amount
            else:
                rec.point_rate = 0
                rec.amount = 0

    """
        Compute yang digunakan untuk menentukan 
        Nilai Number of Mandays dari selisih Start Date dan End Date
    """
    @api.depends('start_date', 'end_date')
    def _compute_number_of_mandays(self):
        for rec in self:
            if rec.start_date and rec.end_date:
                number_of_mandays = rec.end_date - rec.start_date
                rec.number_of_mandays = number_of_mandays.days
            else:
                rec.number_of_mandays = 0
    
    """
        Digunakan untuk Domain / Filtering Resource ID yang dapat dipilih
        berdasarkan Role ID yang dipilih
    """
    @api.depends('role_id')
    def _compute_resource_ids(self):
        for rec in self:
            if rec.role_id:
                rec.resource_ids = rec.role_id.resource_ids
            else:
                rec.resource_ids = self.env['resource.resource'].search([])
    
    # Action untuk merubah State ke To Approve
    def action_confirm(self):
        return self.write({'state' : 'to_approve'})
    
    # Action untuk merubah State ke Draft
    def action_set_to_draft(self):
        return self.write({'state' : 'draft'})
    
    # Action untuk merubah State ke Approved
    def action_approved(self):
        return self.write({'state' : 'approved'})
    
class PlanningSlotTrainingLine(models.Model):
    _name = 'planning.slot.training.line'
    _description = 'Planning Slot Training Line'
    
    project_update_id = fields.Many2one('project.update', string='Project Update', 
                                        index = True, copy = False)
    project_id = fields.Many2one('project.project', string='Project', index = True,
                                 store = True, related='project_update_id.project_id')
    slot_training_id = fields.Many2one('planning.slot.training', string='Slot Training',
                                    index = True, copy = False, tracking = True)
    date = fields.Date('Date', related='project_update_id.date', store = True)
    role_id = fields.Many2one('planning.role.training', string='Role',
                              related='slot_training_id.role_id')
    resource_id = fields.Many2one('resource.resource', string='Resource',
                                related='slot_training_id.resource_id')
    name = fields.Char('Name', related='slot_training_id.name', store = True)
    state = fields.Selection([
        ('draft', 'Draft'),
        ('confirm', 'Confirm'),
    ], string='State', default = 'draft', index = True)
    previous_progress = fields.Float('Previous Progress')
    current_progress = fields.Float('Current Progress')
