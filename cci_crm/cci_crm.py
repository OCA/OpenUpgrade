##############################################################################
#
# Copyright (c) 2004 TINY SPRL. (http://tiny.be) All Rights Reserved.
#                    Fabien Pinckaers <fp@tiny.Be>
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

from osv import fields, osv
import pooler

class meeting_confidential_info(osv.osv):

    _name = 'meeting.confidential.info'
    _description = 'Meeting Confidential Info'
    _rec_name = 'group'
    _columns ={
       'description':fields.text('Description'),
       'group':fields.selection([('group1','Group1'),('group2','Group2')],'Group')
               }

meeting_confidential_info()

class crm_case(osv.osv):

    _inherit = 'crm.case'
    _desctiption = 'crm case'
    _columns = {
        'meeting_id' : fields.many2one('meeting.confidential.info','Meeting confidential'),
        'event_ids' : fields.many2many('event.event','event_case_rel','case_id','event_id','Events'),
     }

    def default_get(self, cr, uid, fields, context={}):
        data = super(crm_case, self).default_get(cr, uid, fields, context)
        if 'section_id' in context and context['section_id'] :
            data['section_id']=context['section_id']
#        if context['section_id']=='_val_rsf':
#            id_section=self.pool.get('crm.case.section').search(cr,uid,[('name','=','RSF')])[0]
#            data['section_id']=id_section
        return data

crm_case()

class event_event(osv.osv):#to be check
    _inherit = 'event.event'
    _description = 'Event Event'
    _columns = {
        'case_ids' : fields.many2many('crm.case','case_event_rel','event_id','case_id','Cases')
                }

event_event()