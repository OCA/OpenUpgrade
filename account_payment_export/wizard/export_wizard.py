# -*- encoding: latin-1 -*-
##############################################################################
#
# Copyright (c) 2005-2006 TINY SPRL. (http://tiny.be) All Rights Reserved.
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
import pooler
import wizard
import base64
from osv import osv
import time
import mx.DateTime
from mx.DateTime import RelativeDateTime, now, DateTime, localtime

export_form = """<?xml version="1.0"?>
<form string="Payment Export">
   <field name="pay"/>
   <field name="note" colspan="4" nolabel="1"/>
   </form>"""

export_fields = {
    'pay' : {
        'string':'Export File',
        'type':'binary',
        'required':False,
        'readonly':True,
    },
    'note' : {'string':'Log','type':'text'},
}
trans=[(u'ￃﾩ','e'),
       (u'ￃﾨ','e'),
       (u'ￃﾠ','a'),
       (u'ￃﾪ','e'),
       (u'ￃﾮ','i'),
       (u'ￃﾯ','i'),
       (u'ￃﾢ','a'),
       (u'ￃﾤ','a')]
def tr(s):
    s= s.decode('utf-8')
    for k in trans:
        s = s.replace(k[0],k[1])
    try:
        res= s.encode('ascii','replace')
    except:
        res = s
    return res

class record:
    def __init__(self,global_context_dict):

        for i in global_context_dict:
            global_context_dict[i]= global_context_dict[i] and tr(global_context_dict[i])
        self.fields = []
        self.global_values = global_context_dict
        self.pre={'padding':'','seg_num1':'0','seg_num2':'1',
                  'seg_num3':'1','seg_num4':'1','seg_num5':'1','seg_num_t':'9',
                   'flag':'0','flag1':'\n'
                           }
        self.post={'date_value_hdr':'000000','type_paiement':'0'}
        self.init_local_context()

    def init_local_context(self):
        """
        Must instanciate a fields list, field = (name,size)
        and update a local_values dict.
        """
        raise "not implemented"

    def generate(self):
        res=''
        for field in self.fields :
            if self.pre.has_key(field[0]):
                value = self.pre[field[0]]
            elif self.global_values.has_key(field[0]):
                value = self.global_values[field[0]]

            elif self.post.has_key(field[0]):
                value = self.post[field[0]]
            else :
                pass
                #raise Exception(field[0]+' not found !')
            try:
                res = res + c_ljust(value, field[1])
            except :
                pass

        return res


class record_header(record):
    # -> total
    def init_local_context(self):
        self.fields=[
            #Header record start
            ('seg_num1',1),
            ('creation_date',6),('padding',12),
            ('institution_code',3),('app_code',2),('reg_number',10),('id_sender',11),('id_order_customer',11),('padding',1),
            ('ver_code',1),('bilateral',12),('totalisation_code',1),('padding',4),('ver_subcode',1),('padding',52),('flag1',1)

            ]

class record_trailer(record):
    # -> total
    def init_local_context(self):
        self.fields=[
            #Header record start
            ('seg_num_t',1),
            ('tot_record',6),('tot_pay_order',6),
            ('tot_amount',15),('padding',100),('flag1',1),
            ]
class record_payline(record):
    # -> total
    def init_local_context(self):
        self.fields=[
            ('seg_num2',1),('sequence',4),('sub_div1',2),('order_exe_date',6),
            ('order_ref',16),('cur_code',3),('padding',1),('code_pay',1),('amt_pay',15),('padding',1),
            ('cur_code_debit',3),('padding',6),
            ('acc_debit',12),('padding',22),('indicate_date',1),('padding',34),('flag1',1),

            ('seg_num3',1),('sequence1',4),('sub_div6',2),('benf_accnt_no',34),('benf_name',35),('benf_address',35),
            ('type_accnt',1),('bank_country_code',2),('padding',14),('flag1',1),

            ('seg_num5',1),('sequence3',4),('sub_div07',2),('benf_address_continue',35),('benf_address_place',35),('padding',10),('msg_order_benf',35),
            ('padding',6),('flag1',1),

            ('seg_num4',1),('sequence2',4),('sub_div10',2),('order_msg',35),('method_pay',3),('charge_code',3),('padding',1),
            ('cur_code_debit',3),('padding',6),('debit_cost',12),('padding',1),('benf_country_code',2),('padding',55),('flag1',1),

            ]

def c_ljust(s, size):
    """
    check before calling ljust
    """
    s= s or ''
    if len(s) > size:
        s= s[:size]
    s = s.decode('utf-8').encode('latin1','replace').ljust(size)
    return s

class Log:
    def __init__(self):
        self.content= ""
        self.error= False
    def add(self,s,error=True):
        self.content= self.content + s
        if error:
            self.error= error
    def __call__(self):
        return self.content

def _create_pay(self,cr,uid,data,context):
    v={}
    v1={}
    v2={}
    log=''
    log=Log()
    blank_space=' '

    seq=0
    total=0
    pay_order=''

    #Header Record Start
    v1['uid'] = str(uid)
    v1['creation_date']= time.strftime('%y%m%d')
    v1['app_code']='51'
    v1['reg_number']=''#25-34
    v1['id_sender']=''#Blank *should be fill 35-44
    v1['id_order_customer']=''#Blank 46-56 *should be fill
    v1['ver_code']='3'
    v1['bilateral']='' #see attach ment 1.2  and 59-70
    v1['totalisation_code ']='0'#two values 0 or 1
    v1['ver_subcode']='1'

    pool = pooler.get_pool(cr.dbname)
    payment=pool.get('payment.order').browse(cr, uid, data['id'],context)
    bank_obj=pool.get('res.partner.bank')
    id_exp= pool.get('account.pay').create(cr,uid,{'name':'test'})
    #look in the mode for insititute_code or protocol number
    cr.execute("SELECT m.bank_id from payment_order o inner join payment_mode m on o.mode=m.id and o.id in (%s) group by bank_id;"% (data['id']))
    bank_id=cr.fetchone()
    if bank_id:
        bank = bank_obj.browse(cr, uid, bank_id[0], context)
        if not bank:
            return {'note':'Please provide bank for the ordering customer.'}
        v1['institution_code']=bank.institution_code
        if not v1['institution_code']:
            return {'note':'Please Provide Institution Code number for Ordering Customer'}

    pay_header =record_header(v1).generate()
    #Header Record End

    pay_line_obj=pool.get('payment.line')
    pay_line_id = pay_line_obj.search(cr, uid, [('order_id','=',data['id'])])
    pay_line =pay_line_obj.read(cr, uid, pay_line_id,['partner_id','amount','bank_id','move_line_id'])
    print pay_line
    if not pay_line:
        return {'note':'Wizard can not generate Export file ,There is no Payment Lines'}
    for pay in pay_line:
        seq=seq+1
        #sub1 Start
        v['sequence'] = str(seq).rjust(4).replace(' ','0')
        v['sub_div1']='01'
        if payment.date_prefered=='now':
            exec_date=now().strftime('%Y-%m-%d')
            v['order_exe_date']=time.strftime('%d%m%y',time.strptime(exec_date,"%Y-%m-%d")) #should be corect becaz there is three date ..see (sub01 pos 8-13)
        else:
            v['order_exe_date']=''
        v['order_ref']=''#14-29 #should be fill. see page 23
        v['cur_code']='BEF'#static set .but is available in entry line object..
        v['code_pay']='C'#two values 'C' or 'D'  *should be modified
        v['amt_pay']=float2str(pay['amount'])
        total=total+pay['amount']
        v['acc_debit']=bank.acc_number
        if not v['acc_debit']:
            return {'note':'Please provide bank account number for the ordering customer.'}
        v['indicate_date']=''# three value blank,1,2, *should be correct...blank is for order execution date .see sub01=pos 94
        #sub1 End

        #sub6 start
        v['sequence1']=str(seq).rjust(4).replace(' ','0')
        # Fetch the invoices:
        cr.execute('''select i.id,ml.ref
          from payment_line pl
           join account_move_line ml on (pl.move_line_id = ml.id)
           join account_move m on (ml.move_id = m.id)
           join account_invoice i on (i.move_id = m.id)
           join payment_order p on (pl.order_id = p.id)
          where p.id = %s and pl.move_line_id= %s
          '''%(payment.id,str(pay['move_line_id'][0])))
        res=cr.fetchall()
        if not res:
            return {'note':'Wizard can not Generate Export file,there is no Related Invoice for \nEntry line:'+str(pay['move_line_id'])+''}
        else:
            inv=pool.get('account.invoice').browse(cr, uid, res[0][0],context)
        v['sub_div6']='06'
        if pay['bank_id']:
            bank1 = bank_obj.read(cr, uid, pay['bank_id'][0])#searching pay line bank account number
            if bank1['state']=='bank':
                v['benf_accnt_no']=bank1['acc_number']
                v['type_accnt']='2'
            elif bank1['state']=='pay_iban':
                v['benf_accnt_no']=bank1['iban']
                v['type_accnt']='1'
            else:
                v['benf_accnt_no']=''#Should be corrext
                v['type_accnt']=''
        else:
            return {'note':'Please Provide Bank Account in payment line for \npartner:'+inv.partner_id.name+' Ref:'+res[0][1]+''}
        part_addres_obj=pool.get('res.partner.address')
        v['bank_country_code']=''
        if bank1['bank_address_id']:
            bank2 = part_addres_obj.read(cr, uid, bank1['bank_address_id'][0])#get bank address of counrty for pos 113-114 sub06
            if bank2['country_id']:
                code_country=pool.get('res.country').read(cr,uid,bank2['country_id'][0],['code'])#get bank address of counrty for pos 113-114 sub06
                v['bank_country_code']=code_country['code']
        v['benf_name']=inv.partner_id.name
        v['benf_address']=str(inv.address_invoice_id.street)+blank_space+str(inv.address_invoice_id.street2)
        if inv.address_invoice_id.country_id and inv.address_invoice_id.state_id:
            v['benf_address_place']=str(inv.address_invoice_id.city)+blank_space+str(inv.address_invoice_id.state_id.name)+blank_space+str(inv.address_invoice_id.country_id.name )
            if not inv.address_invoice_id.city:
                return {'note':'Please Provide city for partner address for\n' 'Bank Account:'+str(pay['bank_id'][1])+blank_space+',Partner:'+inv.partner_id.name+blank_space+',Ref:'+res[0][1]+''}
        else:
            return {'note':'Please Provide Country or State for\n' 'Bank Account:'+str(pay['bank_id'][1])+blank_space+',Partner:'+inv.partner_id.name+blank_space+',Ref:'+res[0][1]+''}
        #sub6 End

        #sub7 start
        v['sequence3']=str(seq).rjust(4).replace(' ','0')
        v['sub_div07']='07'
        v['benf_address_continue']=''#contine from v['benf_address']
        v['msg_order_benf']=''#ordering customer msg to benf customer. pos 88-122,may contain ref-number,invoice-number,etc
        #sub7 End

        #seg10 start
        v['sequence2']=str(seq).rjust(4).replace(' ','0')
        v['sub_div10']='10'
        v['order_msg']=''#msg from order customer to order cutomer bank *should be correct
        v['method_pay']='EUR'#see attachment 1.5..multiple values are available *should be correct
        v['charge_code']='' #*should be correct
        v['cur_code_debit']=''#'BEF' *should be correct
        v['debit_cost']='000000000000'#field will only fill when ordering customer account debitted with charges if not field will contain blank or zero
        v['benf_country_code']=inv.address_invoice_id.country_id.code
        if not v['benf_country_code']:
            return {'note':'Please Provide Country for payment line partner'}
        #sub10 End
        pay_order =pay_order+record_payline(v).generate()

    #Trailer Record Start
    v2['tot_record']=str(seq)
    v2['tot_pay_order']=str(seq)
    v2['tot_amount']=float2str(total)
    pay_trailer=record_trailer(v2).generate()
    #Trailer Record End

    try:
        pay_order=pay_header+pay_order+pay_trailer
    except Exception,e :
        log= log +'\n'+ str(e) + 'CORRUPTED FILE !\n'
        raise
    log.add("Successfully Exported\n--\nSummary:\nTotal amount paid : %.2f \nTotal Number of Payments:%.2f \n-- "\
            %(total,seq))

    pool.get('account.pay').write(cr,uid,[id_exp],{'note':log,'name':base64.encodestring(pay_order or "")})
    return {'note':log(), 'pay': base64.encodestring(pay_order)}


def float2str(lst):
            return str(lst).rjust(15).replace('.','0')

class wizard_pay_create(wizard.interface):
    states = {
        'init' : {
            'actions' : [_create_pay],
            'result' : {'type' : 'form',
                        'arch' : export_form,
                        'fields' : export_fields,
                        'state' : [('end', 'Ok','gtk-ok') ]}
        },

    }

wizard_pay_create('account.payment_create')