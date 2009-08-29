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

from osv import osv
from osv import fields
import netsvc
import time

class ServerAction(osv.osv):
    _inherit = 'ir.actions.server'
    _description = 'Email Client'
    _columns = {
        'email_server':fields.many2one('email.smtpclient', 'Email Server'),
        'report':fields.many2one('ir.actions.report.xml', 'Report', required=False),
    }
    
    def run(self, cr, uid, ids, context={}):
        logger = netsvc.Logger()
        
        act_ids = []
        
        for action in self.browse(cr, uid, ids, context):
            obj_pool = self.pool.get(action.model_id.model)
            obj = obj_pool.browse(cr, uid, context['active_id'], context=context)
            cxt = {
                'context':context, 
                'object': obj, 
                'time':time,
                'cr': cr,
                'pool' : self.pool,
                'uid' : uid
            }
            expr = eval(str(action.condition), cxt)
            if not expr:
                continue

            if action.state == 'email':                
                address = str(action.email)
                try:
                    address =  eval(str(action.email), cxt)
                except:
                    pass

                if not address:
                    logger.notifyChannel('email', netsvc.LOG_INFO, 'Partner Email address not Specified!')
                    continue

                subject = self.merge_message(cr, uid, str(action.subject), action, context)
                body = self.merge_message(cr, uid, str(action.message), action, context)
                smtp_pool = self.pool.get('email.smtpclient')

                reports = []
                if action.report:
                    reports.append(('report.'+action.report.report_name, [context['active_id']]))

                if smtp_pool.send_email(cr, uid, action.email_server.id, address, subject, body, [], reports) == True:
                    logger.notifyChannel('email', netsvc.LOG_INFO, 'Email successfully send to : %s' % (address))
                else:
                    logger.notifyChannel('email', netsvc.LOG_ERROR, 'Failed to send email to : %s' % (address))

            else:
                act_ids.append(action.id)
        
        if act_ids:
            return super(ServerAction,self).run(cr, uid, act_ids, context)
        else:
            return False

ServerAction()
