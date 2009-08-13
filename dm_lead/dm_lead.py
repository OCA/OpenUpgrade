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
import netsvc

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
                'case_id' : fields.many2one('crm.case', 'CRM Case', select="1", ondelete="cascade")
            }
dm_workitem()

class dm_campaign_document(osv.osv):
    _inherit = "dm.campaign.document"

    _columns = {
                'case_id' : fields.many2one('crm.case', 'CRM Case', select="1", ondelete="cascade"),
    }
dm_campaign_document()

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
        'mail_service_id' : fields.many2one('dm.mail_service','Mail Service'),
        'action_time': fields.datetime('Action Time'),
    }
    _defaults = {
        'source': lambda *a: 'case_id',
    }

    def create(self,cr,uid,vals,context={}):
        id = super(dm_event_case,self).create(cr,uid,vals,context)
        obj = self.browse(cr, uid ,id)
        tr_ids = self.pool.get('dm.offer.step.transition').search(cr, uid, [('step_from_id','=',obj.step_id.id),
            ('condition_id','=',obj.trigger_type_id.id)])
        if not tr_ids:
            netsvc.Logger().notifyChannel('dm event case', netsvc.LOG_WARNING, "There is no transition %s at this step : %s"% (obj.trigger_type_id.name, obj.step_id.code))
            osv.except_osv('Warning', "There is no transition %s at this step : %s"% (obj.trigger_type_id.name, obj.step_id.code))
            return False

        for tr in self.pool.get('dm.offer.step.transition').browse(cr, uid, tr_ids):
            if obj.action_time:
                next_action_time = datetime.datetime.strptime(obj.action_time, '%Y-%m-%d  %H:%M:%S')
            else:
                wi_action_time = datetime.datetime.now()
                kwargs = {(tr.delay_type+'s'): tr.delay}
                next_action_time = wi_action_time + datetime.timedelta(**kwargs)

                if tr.action_hour:
                    hour_str =  str(tr.action_hour).split('.')[0] + ':' + str(int(int(str(tr.action_hour).split('.')[1]) * 0.6))
                    act_hour = datetime.datetime.strptime(hour_str,'%H:%M')
                    next_action_time = next_action_time.replace(hour=act_hour.hour)
                    next_action_time = next_action_time.replace(minute=act_hour.minute)

            try:
                wi_id = self.pool.get('dm.workitem').create(cr, uid, {'step_id':tr.step_to_id.id or False, 'segment_id':obj.segment_id.id or False, 'tr_from_id':tr.id,
                    'case_id':obj.case_id.id, 'mail_service_id':obj.mail_service_id.id, 'action_time':next_action_time.strftime('%Y-%m-%d  %H:%M:%S'), 'source':obj.source})
                netsvc.Logger().notifyChannel('dm event case', netsvc.LOG_DEBUG, "Creating Workitem with action at %s"% next_action_time.strftime('%Y-%m-%d  %H:%M:%S'))
                netsvc.Logger().notifyChannel('dm event case', netsvc.LOG_DEBUG, "Workitem : %s"% vals)
            except:
                netsvc.Logger().notifyChannel('dm event case', netsvc.LOG_ERROR, "Event cannot create Workitem")
        return super(dm_event_case,self).create(cr,uid,vals,context)

dm_event_case()
