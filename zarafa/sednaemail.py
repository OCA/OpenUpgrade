#!/usr/bin/env python
#coding: utf-8
#
# (c) 2008 Sednacom <http://www.sednacom.fr>
#
# authors :
#  - Brice V. < brice@sednacom.fr >

from osv import osv, fields
import time
import htmlmail
import base64

def _default_from(*args):
    obj = args[0]
    cr = args[1]
    user = args[2]
    context= args[3]
    return obj.pool.get('res.users').read(cr, user, [user, ], ['zarafa_email', ])[0]['zarafa_email']

def _default_name(*args):
    context= args[3]
    name = context.get('case_name', '')
    return name

def _default_recipients(*args):
    context = args[3]
    recipients = context.get('case_recipients', False)
    return recipients

class email(osv.osv):
    """Sednacom email"""
    _name = 'sednacom.email'

    def _make_to(self, cr, uid, eids, name, arg, context={}):
        res = {}
        for data in self.browse(cr, uid, eids, context):
            res[data.id] = ', '.join([ contact.email for contact in data.recipients if contact.email])
        return res

    _columns = {
        'name' : fields.char('Title', size=64, required=True, readonly=True,
                    states={'draft' : [('readonly', False),]}) ,
        'body' : fields.text('Message', readonly=True,
                    states={'draft' : [('readonly', False),]}) ,
        'to' : fields.function(_make_to, method=True, string='To', type='char', size=256) ,
        'recipients' : fields.many2many('res.partner.address', 'sednacom_email_recipients', 'email', 'contact', 'Contacts',
                    readonly=True, states={'draft' : [('readonly', False),]}) ,
        'exp' : fields.char('From', size=128, required=True, readonly=True,
                    states={'draft' : [('readonly', False),]}) ,
        'datetime' : fields.datetime('Date', readonly=True,
                    states={'draft' : [('readonly', False),]}) ,
        'state' : fields.selection(
            [   ('draft','Draft'),
                ('sent','Sent'),
                ('received','Received'), ] ,
            'State', readonly=True,) ,
        'crm_case' : fields.many2one('crm.case', 'Case',
                readonly=True, states={'draft' : [('readonly', False),]}) ,
    }

    _defaults = {
        'datetime' : lambda *args: time.strftime('%Y-%m-%d %H:%M:%S') ,
        'exp' : _default_from ,
        'state' : lambda *args: 'draft' ,
        'name' : _default_name ,
        'recipients' : _default_recipients ,
    }

    _order = "datetime desc"

    def add_crm_log(self, cr, uid, eids, context={}):
        o_cch = self.pool.get('crm.case.history')

        data = self.read(cr, uid, eids, ['id', 'crm_case', 'body', 'exp', ])

        canal = context.get('canal_id', False)
        name = context.get('history_name', 'Email')
        res = True
        for row in data:
            if row['crm_case']:
                case_id = row['crm_case'][0]
                vals = {
                    'name' : name ,
                    'canal_id' : canal ,
                    'case_id' : case_id ,
                    'description' : row['body'] ,
                    'email' : row['exp'] ,
                }
                res = o_cch.create(cr, uid, vals)
            else:
                continue
        return res


    def send(self, cr, uid, eids, context={}):
        if not eids:
            return True
        datas = self.browse(cr, uid , eids, context)

        o_ia = self.pool.get('ir.attachment')
        b64d = base64.decodestring

        for data in datas:
            ia_ids = o_ia.search(cr, uid,
                [('res_model','=','sednacom.email'),('res_id','=',data.id),] )
            ia_data  = list()
            if ia_ids:
                ia_raw_data = o_ia.read(cr, uid, ia_ids, ['datas_fname', 'datas',])
                ia_data = [ ( d['datas_fname'],  b64d(d['datas']) ) \
                                    for d in ia_raw_data ]

            htmlmail.email_html_send_attach(
                data.exp ,
                [a.strip() for a in str(data.to).split(',')] ,
                data.name ,
                data.body ,
                False,
                False,
                False,
                False,
                ia_data,
                False
            )

        self.write(cr, uid, eids, {'state' : 'sent'})
        self.add_crm_log(cr, uid, eids, context)
        return True

    def zarafa_send(self, cr, uid, eids, context={}):
        if not eids:
            return True
        datas = self.browse(cr, uid , eids, context)

        o_ia = self.pool.get('ir.attachment')
        b64d = base64.decodestring

        for data in datas:
            ia_ids = o_ia.search(cr, uid,
                [('res_model','=','sednacom.email'),('res_id','=',data.id),] )
            ia_data  = list()
            if ia_ids:
                ia_raw_data = o_ia.read(cr, uid, ia_ids, ['datas_fname', 'datas',])
                ia_data = [ ( d['datas_fname'],  b64d(d['datas']) ) \
                                    for d in ia_raw_data ]
            htmlmail.zarafa_email_html_send_attach(
                self, cr, uid,
                data.exp ,
                [a.strip() for a in str(data.to).split(',')] ,
                data.name ,
                data.body ,
                False,
                False,
                False,
                False,
                ia_data,
                False
            )

        self.write(cr, uid, eids, {'state' : 'sent'})
        self.add_crm_log(cr, uid, eids, context)
        return True

email()
