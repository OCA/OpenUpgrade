# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution····
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

from osv import fields
from osv import osv
import datetime

class dm_customers_file(osv.osv):
    _inherit = "dm.customers_file"

    def __init__(self, *args):
        self._FILE_SOURCES.append(('case_id','CRM Cases'))
        return super(dm_customers_file, self).__init__(*args)

    _columns = {
                'case_ids' : fields.many2many('crm.case','crm_case_customer_file_rel','case_id','cust_file_id','CRM Cases')
            }
dm_customers_file()

class dm_workitem(osv.osv):
    _inherit = "dm.workitem"

    def __init__(self, *args):
        self._SOURCES.append(('case_id','CRM Case'))
        return super(dm_workitem, self).__init__(*args)

    _columns = {
                'case_id' : fields.many2one('crm.case','CRM Case')
            }
dm_workitem()

class dm_event_case(osv.osv_memory):
    _name = "dm.event.case"
    _rec_name = "campaign_id"
    _columns = {
        'campaign_id' : fields.many2one('dm.campaign', 'Campaign'),
        'segment_id' : fields.many2one('dm.campaign.proposition.segment', 'Segment', required=True,context="{'dm_camp_id':campaign_id}"),
        'step_id' : fields.many2one('dm.offer.step', 'Offer Step', required=True,context="{'dm_camp_id':campaign_id}"),
        'source' : fields.selection([('case_id','CRM Cases')], 'Source', required=True),
        'case_id' : fields.many2one('crm.case','CRM Case'),
        'trigger_type_id' : fields.many2one('dm.offer.step.transition.trigger','Trigger Condition',required=True),
    }
    _defaults = {
        'source': lambda *a: 'case_id',
    }

    def create(self,cr,uid,vals,context={}):
#        if 'action_time' in vals and vals['action_time']:
#            return super(dm_workitem, self).create(cr, uid, vals, context)
#        if 'trigger_type_id' in vals and vals['trigger_type_id']:
        tr_ids = self.pool.get('dm.offer.step.transition').search(cr, uid, [('step_from_id','=',vals['step_id']),
                ('condition_id','=',vals['trigger_type_id'])])
        for tr in self.pool.get('dm.offer.step.transition').browse(cr, uid, tr_ids):
            wi_action_time = datetime.datetime.now()
            kwargs = {(tr.delay_type+'s'): tr.delay}
            next_action_time = wi_action_time + datetime.timedelta(**kwargs)
            print "Next action date : ",next_action_time
#                vals['action_time'] = next_action_time
            print "Vals : ",vals
#        else:
#            vals['action_time'] = datetime.datetime.now()
#            print "Vals : ",vals

            self.pool.get('dm.workitem').create(cr, uid, {'step_id':tr.step_to_id.id or False, 'segment_id':vals['segment_id'] or False,
            (vals['source']):vals[(vals['source'])] or False, 'action_time':next_action_time, 'source':vals['source']})

        return super(dm_event_case,self).create(cr,uid,vals,context)

dm_event_case()