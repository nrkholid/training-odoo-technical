{
    "name" : "PT. Sanbe Farma - Training",
    "description" : "Pelatihan Technical Odoo V17 untuk PT. Sanbe Farma",
    "author" : "PT. Sanbe Farma, PT. Arkana Solusi Digital",
    "version" : "17.0.1.0.0",
    "category" : "Others",
    "license" : "OPL-1",
    "depends" : [
        "base", 
        "mail",
        "hr",
        "project",
    ],
    "data" : [
        "security/planning_slot_role.xml",
        "security/ir.model.access.csv",
        "data/hr_employee_data.xml",
        "wizard/project_reporting_wizard_view.xml",
        "views/planning_role_view.xml",
        'views/planning_slot_view.xml',
        'views/planning_menu_view.xml',
        'views/project_inherit_view.xml',
        'views/project_update_inherit_view.xml',
    ],
    "auto_install" : False, 
    "installable" : True,
    "application" : True,
    "external_dependencies" : {"python" : []}
}