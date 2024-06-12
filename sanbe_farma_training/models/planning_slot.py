from odoo import _, api, fields, models


class PlanningSlotTraining(models.Model):
    _name = 'planning.slot.training'
    _description = 'Planning Slot Training'
    
    name = fields.Char('Description')
    role_id = fields.Many2one('planning.role.training', string='Role', index = True,
                              copy = False, tracking = True, check_company=True)
    resource_id = fields.Many2one('resource.resource', string='Resource', index = True,
                                copy = False, tracking = True, check_company=True)
    company_id = fields.Many2one('res.company', string='Company', index = True, default=lambda self: self.env.company,
                                 copy = False, required=True)
    currency_id = fields.Many2one('res.currency', string='Currency', related='company_id.currency_id',
                                  store = True)
    start_date = fields.Date('Start Date', default=lambda self: fields.Date.context_today(self))
    end_date = fields.Date('Enda Date', default=lambda self:fields.Date.context_today(self))
    state = fields.Selection([
        ('draft', 'Draft'),
        ('to_approve', 'To Approve'),
        ('approved', 'Approved')
    ], string='State', default='draft')
    number_of_mandays = fields.Integer(compute='_compute_number_of_mandays', 
                                    string='Number of Mandays', store = True)
    resource_ids = fields.Many2many('resource.resource', string='Resource',
                                    compute='_compute_resource_ids')
    point_rate = fields.Integer(compute='_compute_role_components', 
                                string='Point Rate', store = True)
    amount = fields.Monetary('Amount', compute='_compute_role_components', store = True,
                             curreny_field='currency_id')
    total_points = fields.Integer(compute='_compute_total_points', 
                                  string='Total Points', store = True)
    expected_revenue = fields.Monetary(compute='_compute_expected_revenue', 
                                       string='Expected Revenue', store = True,
                                       currency_field='currency_id')
    
    @api.depends('number_of_mandays', 'amount')
    def _compute_expected_revenue(self):
        for rec in self:
            if rec.number_of_mandays and rec.amount:
                rec.expected_revenue = rec.number_of_mandays * rec.amount
            else:
                rec.expected_revenue = 0
    
    @api.depends('number_of_mandays', 'point_rate')
    def _compute_total_points(self):
        for rec in self:
            if rec.number_of_mandays and rec.point_rate:
                rec.total_points = rec.number_of_mandays * rec.point_rate
            else:
                rec.total_points = 0
    
    @api.depends('role_id')
    def _compute_role_components(self):
        for rec in self:
            if rec.role_id:
                rec.point_rate = rec.role_id.point_rate
                rec.amount = rec.role_id.amount
            else:
                rec.point_rate = 0
                rec.amount = 0

    @api.depends('start_date', 'end_date')
    def _compute_number_of_mandays(self):
        for rec in self:
            if rec.start_date and rec.end_date:
                number_of_mandays = rec.end_date - rec.start_date
                rec.number_of_mandays = number_of_mandays.days
            else:
                rec.number_of_mandays = 0
        
    @api.depends('role_id')
    def _compute_resource_ids(self):
        for rec in self:
            if rec.role_id:
                rec.resource_ids = rec.role_id.resource_ids
            else:
                rec.resource_ids = self.env['resource.resource'].search([])
    
