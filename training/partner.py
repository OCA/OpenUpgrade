# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution	
#    Copyright (C) 2004-2009 Tiny SPRL (<http://tiny.be>). All Rights Reserved
#    $Id$
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from osv import osv, fields
import time

class res_partner_contact_technical_skill(osv.osv):
    _name = 'res.partner.contact_technical_skill'

    _columns = {
        'name' : fields.char('Name', size=32, select=True, required=True),
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

    _defaults = {
        'matricule' : lambda *a: '',
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
        'specialisation_id' : fields.many2one('training.course_category', 'Specialisation',
                                              required=True, help="A Quality Team has a particularity")
    }

res_partner_team()

class res_partner(osv.osv):
    _inherit = 'res.partner'

    _columns = {
        'notif_contact_id' : fields.many2one('res.partner.contact', 'Contact RH'),
        'notif_participant' : fields.boolean('Participant'),
    }

res_partner()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
