# -*- coding: UTF-8 -*-
# training/training.py
from osv import osv, fields
import time

class res_partner_contact_technical_skill(osv.osv):
    _name = 'res.partner.contact_technical_skill'

    _columns = {
        'name' : fields.char('Name', size=32, select=True),
    }

    _sql_constraints = [
        ('unique_name', 'unique(name)', 'Unique name for the technical skill')
    ]

res_partner_contact_technical_skill()

class res_partner_contact(osv.osv):
    _inherit = 'res.partner.contact'

    _columns = {
        'matricule' : fields.char( 'Matricule', size=32, required=True ),
        'birthplace' : fields.char( 'BirthPlace', size=64 ),
        'education_level' : fields.char( 'Education Level', size=128 ),
        'technical_skill_ids' : fields.many2many('res.partner.contact_technical_skill', 
                                                 'res_partner_contact_technical_skill_rel', 
                                                 'contact_id', 
                                                 'skill_id', 
                                                 'Technical Skill'),
    }
res_partner_contact()

class res_partner_job(osv.osv):
    _inherit = 'res.partner.job'
    _columns = {
        'external_matricule' : fields.char( 'Matricule', size=32 ),
        'departments' : fields.text( 'Departments' ),
        'orientation' : fields.text( 'Orientation' ),
    }
res_partner_job()

class training_course_category(osv.osv):
    _name = 'training.course_category'
training_course_category()

class res_partner_team(osv.osv):
    _inherit = 'res.partner.team'
    _columns = {
        'specialisation_id' : fields.many2one('training.course_category', 'Specialisation', required=True)
    }

res_partner_team()

