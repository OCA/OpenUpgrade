# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution	
#    Copyright (C) 2004-2008 Tiny SPRL (<http://tiny.be>). All Rights Reserved
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

import netsvc
from osv import fields, osv

class res_partner_contact(osv.osv):
    _inherit = "res.partner.contact"
    _columns = {
        'data_private': fields.boolean('Private data'),
        'self_sufficent':fields.boolean('Keep contact',help='This contact will not be removed even if all his addresses are deleted'),
        'who_date_accept':fields.date('Accept Date'),
        'who_date_last':fields.date('Last Modification'),
        'who_date_publication':fields.date('Publication'),
        'who_presence':fields.boolean('In WsW'),
        'who_description':fields.text('WsW Description',translate=True),
        'origin':fields.char('Origin',size=20,help='The DB from which the info is coming from'),
        'fse_work_status':fields.char('FSE Work Status',size=20),
        'fse_work_experience':fields.char('FSE Work Exp.',size=20),
        'fse_studies':fields.char('FSE Studies',size=20),
        'country_ids': fields.many2many('res.country','res_country_rel','contact','country',"Expertize's Countries"),
        'link_ids':fields.one2many('res.partner.contact.link','current_contact_id','Contact Link'),
        'canal_id': fields.many2one('res.partner.canal', 'Favourite Channel'),
        'national_number' : fields.char( 'National Number',size=15), 
        'magazine_subscription':fields.selection( [('never','Never'),('prospect','Prospect'),('personal','Personal'), ('postal','Postal')], "Magazine subscription"),
        'magazine_subscription_source':fields.char('Mag. Subscription Source',size=30),
        'old_id':fields.integer('Old Datman ID'),
    }
    _defaults = {
        'data_private' : lambda *a : False,
        'self_sufficent': lambda *a : False,
        'who_presence': lambda *a : True,
    }
res_partner_contact()


class res_partner_contact_link_type(osv.osv):
    _name = "res.partner.contact.link.type"
    _description = "res.partner.contact.link.type"
    _columns = {
        'name':fields.char('Name',size=20, required=True),
   }
res_partner_contact_link_type()

class res_partner_contact_link(osv.osv):
    _name = "res.partner.contact.link"
    _description = "res.partner.contact.link"
    _columns = {
        'name':fields.char('Name',size=40,required=True),
        'type_id' : fields.many2one('res.partner.contact.link.type','Type',required=True),
        'contact_id' : fields.many2one('res.partner.contact','Contact',required=True),
        'current_contact_id': fields.many2one('res.partner.contact','Current contact',required=True),
   }
res_partner_contact_link()

class project(osv.osv):
    _inherit = "project.project"
    _description = "Project"
    _columns = {
        'contact_id2': fields.many2one('res.partner.contact','Contact'),
    }
project()

class res_partner_job(osv.osv):
    _inherit = 'res.partner.job'
    _columns = {
        'login_name': fields.char('Login Name',size=80), 
        'password': fields.char('Password',size=50),
        'token': fields.char('Token',size=40),
    }

res_partner_job()


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

