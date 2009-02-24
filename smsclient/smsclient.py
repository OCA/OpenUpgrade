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

from osv import fields, osv
import time
import urllib

class SMSClient(osv.osv):
    _name = 'sms.smsclient'
    _description = 'SMS Client'
    _columns = {
        'name' : fields.char('Gateway Name', size=256, required=True),
        'url' : fields.char('Gateway URL', size=256, required=True),
        'property_ids':fields.one2many('sms.smsclient.parms', 'gateway_id', 'Parameters'),
        'history_line':fields.one2many('sms.smsclient.history', 'gateway_id', 'History'),
        'method':fields.selection([
            ('http','HTTP Method')
        ],'API Method', select=True),
        'state': fields.selection([
            ('new','Not Verified'),
            ('waiting','Waiting for Verification'),
            ('confirm','Verified'),
        ],'Gateway Status', select=True, readonly=True),
        'users_id': fields.many2many('res.users', 'res_smsserver_group_rel', 'sid', 'uid', 'Users Allowed'),
        'code' : fields.char('Verification Code', size=256),
        'body' : fields.text('Message', help="The message text that will be send along with the email which is send through this server"),
    }
    _defaults = {
        'state': lambda *a: 'new',
        'method': lambda *a: 'http'
    }
    
    def check_permissions(self, cr, uid, id):
        cr.execute('select * from res_smsserver_group_rel where sid=%s and uid=%s' % (id, uid))
        data = cr.fetchall()
        if len(data) <= 0:
            return False
        
        return True
    
    def send_message(self, cr, uid, gateway, to, text):
        gate = self.browse(cr, uid, gateway)
        
        if not self.check_permissions(cr, uid, gateway):
            raise osv.except_osv(_('Permission Error!'), _('You have no permission to access %s ') % (gate.name,) )
        
        url = gate.url
        prms = {}
        for p in gate.property_ids:
            if p.type == 'to':
                prms[p.name] = to
            elif p.type == 'sms':
                prms[p.name] = text
            else:
                prms[p.name] = p.value
                
        params = urllib.urlencode(prms)
        req = url+"?"+params
        queue = self.pool.get('sms.smsclient.queue')
        queue.create(cr, uid, {
                    'name':req,
                    'gateway_id':gateway,
                    'state': 'draft',
                    'mobile':to,
                    'msg':text
                })
        return True
    
    def _check_queue(self, cr, uid, ids=False, context={}):
        queue = self.pool.get('sms.smsclient.queue')
        history = self.pool.get('sms.smsclient.history')
        
        sids = queue.search(cr, uid, [('state','!=','send'),('state','!=','sending')], limit=30)
        queue.write(cr, uid, sids, {'state':'sending'})
        error = []
        sent = []
        for sms in queue.browse(cr, uid, sids):
            f = urllib.urlopen(sms.name)
            if len(sms.msg) > 160:
                error.append(sms.id)
                continue
            
            history.create(cr, uid, {
                        'name':'SMS Sent',
                        'gateway_id':sms.gateway_id.id,
                        'sms': sms.msg,
                        'to':sms.mobile
                    })
            sent.append(sms.id)
            
        queue.write(cr, uid, sent, {'state':'send'})
        queue.write(cr, uid, error, {'state':'error', 'error':'Size of SMS should not be more then 160 char'})
        return True
SMSClient()

class SMSQueue(osv.osv):
    _name = 'sms.smsclient.queue'
    _description = 'SMS Queue'
    _columns = {
        'name' : fields.text('SMS Request', size=256, required=True, readonly=True, states={'draft':[('readonly',False)]}),
        'msg' : fields.text('SMS Text', size=256, required=True, readonly=True, states={'draft':[('readonly',False)]}),
        'mobile' : fields.char('Mobile No', size=256, required=True, readonly=True, states={'draft':[('readonly',False)]}),
        'gateway_id':fields.many2one('sms.smsclient', 'SMS Gateway', readonly=True, states={'draft':[('readonly',False)]}),
        'state':fields.selection([
            ('draft','Queued'),
            ('sending','Waiting'),
            ('send','Sent'),
            ('error','Error'),
        ],'Message Status', select=True, readonly=True),
        'error':fields.text('Last Error', size=256, readonly=True, states={'draft':[('readonly',False)]}),
        'date_create': fields.datetime('Date', readonly=True),
    }
    _defaults = {
        'date_create': lambda *a: time.strftime('%Y-%m-%d %H:%M:%S'),
        'state': lambda *a: 'draft',
    }
SMSQueue()

class Properties(osv.osv):
    _name = 'sms.smsclient.parms'
    _description = 'SMS Client Properties'
    _columns = {
        'name' : fields.char('Property name', size=256, required=True),
        'value' : fields.char('Property value', size=256, required=True),
        'gateway_id':fields.many2one('sms.smsclient', 'SMS Gateway'),
        'type':fields.selection([
            ('user','User'),
            ('password','Password'),
            ('sender','Sender Name'),
            ('to','Recipient No'),
            ('sms','SMS Message')
        ],'API Method', select=True),
    }
Properties()

class HistoryLine(osv.osv):
    _name = 'sms.smsclient.history'
    _description = 'SMS Client History'
    _columns = {
        'name' : fields.char('Description',size=160, required=True, readonly=True),
        'date_create': fields.datetime('Date', readonly=True),
        'user_id':fields.many2one('res.users', 'Username', readonly=True, select=True),
        'gateway_id' : fields.many2one('sms.smsclient', 'SMS Gateway', ondelete='set null', required=True),
        'to':fields.char('Mobile No', size=15, readonly=True),
        'sms':fields.text('SMS', size=160, readonly=True),
    }
    
    _defaults = {
        'date_create': lambda *a: time.strftime('%Y-%m-%d %H:%M:%S'),
        'user_id': lambda obj, cr, uid, context: uid,
    }
    
    def create(self, cr, uid, vals, context=None):
        super(HistoryLine,self).create(cr, uid, vals, context)
        cr.commit()
HistoryLine()
