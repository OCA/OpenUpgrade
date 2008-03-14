##############################################################################
#
# Copyright (c) 2007 TINY SPRL. (http://tiny.be) All Rights Reserved.
#
# WARNING: This program as such is intended to be used by professional
# programmers who take the whole responsability of assessing all potential
# consequences resulting from its eventual inadequacies and bugs
# End users who are looking for a ready-to-use solution with commercial
# garantees and support are strongly adviced to contract a Free Software
# Service Company
#
# This program is Free Software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.
#
##############################################################################

import netsvc
from osv import fields, osv

class res_partner_contact(osv.osv):
    _inherit = "res.partner.contact"
    _columns = {
        'data_private': fields.boolean('Private data'),
        'self_sufficent':fields.boolean('Keep contact',help='This contact will not be removed even if all this addresses are deleted'),
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
        'name':fields.char('Name',size=20,required=True),
        'type_id' : fields.many2one('res.partner.contact.link.type','Type',required=True),
        'contact_id' : fields.many2one('res.partner.contact','Contact',required=True),
        'current_contact_id': fields.many2one('res.partner.contact','Current contact',required=True),
   }
res_partner_contact_link()

#class res_contact_relation_type(osv.osv):
#    _name = "res.contact.relation.type"
#    _description ='res.contact.relation.type'
#    _columns = {
#        'name': fields.char('Contact',size=50, required=True),
#    }
#res_contact_relation_type()

#class res_contact_relation(osv.osv):
#    _name = "res.contact.relation"
#    _description ='res.contact.relation'
#    _columns = {
#        'contact_id': fields.many2one('res.partner.contact','Contact'),
#        'contact_relation_id':fields.char('Relation',size=50),#should be corect
#        'description':fields.text('Description'),
#        'type_id':fields.many2one('res.contact.relation.type','Type'),
#    }
#res_contact_relation()

#class res_partner_country_relation(osv.osv):
#    _name = "res.partner.country.relation"
#    _description = 'res.partner.country.relation'
#    _columns = {
#        'frequency': fields.selection([('frequent','Frequent'),('occasional','Occasionnel'),('prospect','Prospection')],'Frequency'),
#        'country_id':fields.many2one('res.country','Country'),
#        'type':fields.selection([('export','Export'),('import','Import'),('saloon','Salon')],'Types'),#should be corect
#    }

#res_partner_country_relation()

