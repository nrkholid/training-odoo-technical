from odoo import _, api, fields, models
from random import randint

class PlanningRoleTraining(models.Model):
    _name = 'planning.role.training'
    _description = 'Planning Role Training'
    _order = 'name asc'
    
    # Menentukan nilai Default untuk Color secara Angka Random dari 1-11
    def _get_default_color(self):
        return randint(1, 11)
    
    sequence = fields.Integer('Sequence')
    company_id = fields.Many2one('res.company', string='Company', default = 
                                 lambda self : self.env.company)
    currency_id = fields.Many2one('res.currency', string='Currency', 
                                  related='company_id.currency_id', store = True)
    point_rate = fields.Integer('Point Rate')
    amount = fields.Monetary('Amount', curreny_field='currency_id')
    active = fields.Boolean('Active', default=True)
    name = fields.Char('Nama Role', index=True)
    color = fields.Integer('Color', default=_get_default_color)
    resource_ids = fields.Many2many(comodel_name='resource.resource', 
                                    relation='planning_resource_ids',
                                    column1='planning_role_id',
                                    column2='resource_id',
                                    string='Resource',
                                    domain="[('id', 'in', available_resource_ids)]")
    available_resource_ids = fields.Many2many('resource.resource', string='Available Resource',
                                            compute='_compute_available_resource_ids')    

    # Compute yang depends terhadap Field Active
    @api.depends('active')
    def _compute_available_resource_ids(self):
        for rec in self:
            # Digunakan untuk Mendefinisikan Model / Table yang hendak digunakan
            resource_obj = self.env['resource.resource']
            if rec.active:
                # Jika Role ID dalam posisi aktif akan dilakukan eksekusi kondisi yang ini
                # Mencari Existing Resource yang sudah terpakai pada Model ini
                used_resource_ids = list(set(self.search([('active', '=', True)]).mapped('resource_ids.id')))

                # Mencari Available Resource dan diassing Resultnya ke Field Available Resource IDS
                rec.available_resource_ids = resource_obj.search([('id', 'not in', used_resource_ids)])
            else:
                # Mencari Data Seluruh Resource yang ada tanpa terkecuali jika Role dalam kondisi tidak Aktif
                rec.available_resource_ids = resource_obj.search([])

    
    


    
        
    
    

