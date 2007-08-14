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
import pooler
import mx.DateTime
from mx.DateTime import RelativeDateTime, DateTime

payment_form = """<?xml version="1.0"?>
<form string="Payment Export">
</form>"""
payment_fields = {
}
export_form = """<?xml version="1.0"?>
<form string="Payment Export">
   <field name="pay"/>
</form>"""

export_fields = {
    'pay' : {
        'string':'Export File',
        'type':'binary',
        'required':False,
        'readonly':True,
    },
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
                  'seg_num3':'1','seg_num4':'1','seg_num5':'05','seg_num_t':'9',
                   'flag':'0', 'zero5':'00000','flag1':'\n'
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
                print "error is there"
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

def _create_pay(self,cr,uid,data,context):
    v={}
    v1={}
    v2={}
    log=''
    v1['uid'] = str(uid)
    v1['creation_date']= time.strftime('%y%m%d')
    v1['app_code']='51'
    v1['reg_number']=''#25-34
    v1['id_sender']=''#Blank 35-44
    v1['id_order_customer']=''#Blank 46-56
    v1['ver_code']='3'
    v1['bilateral']='' #see attach ment 1.2  and 59-70
    v1['totalisation_code ']='0'#two values 0 or 1
    v1['ver_subcode']='1'
    pay_order=''
    pay_header =record_header(v1).generate()

    pool = pooler.get_pool(cr.dbname)
    bank_obj=pool.get('res.partner.bank')
    id_exp= pool.get('account.pay').create(cr,uid,{
    'name':'test',
    })
    #look in the mode for insititute_code or protocol number
    cr.execute("SELECT m.bank_id from payment_order o inner join payment_mode m on o.mode=m.id and o.id in (%s) group by bank_id;"% (data['id']))
    bank_id=cr.fetchone()
    if bank_id:
        bank = bank_obj.browse(cr, uid, bank_id[0], context)
        v['institution_code']=bank.institution_code
    pay_line_obj=pool.get('payment.line')
    pay_order1=pool.get('payment.order').browse(cr, uid, data['id'],context)
    pay_line_id = pay_line_obj.search(cr, uid, [('order_id','=',data['id'])])
    pay_line =pay_line_obj.read(cr, uid, pay_line_id,['partner_id','amount','bank_id'])
    seq=0
    total=0
    for pay in pay_line:
        seq=seq+1
        #sub1 start
        v['sequence'] = str(seq).rjust(4).replace(' ','0')
        v['sub_div1']='01'
        v['order_exe_date']=time.strftime('%d%m%y',time.strptime(pay_order1.date_done,"%Y-%m-%d")) #should be corect becaz there is three date ..see (sub01 pos 8-13)
        v['order_ref']=''#14-29
        v['cur_code']='BEF'#static set .but is available in entry line object..
        v['code_pay']='C'#two values 'C' or 'D'  *should be change
        v['amt_pay']=float2str(pay['amount'])
        total=total+pay['amount']
        v['acc_debit']=bank.acc_number
        v['indicate_date']=''# three value blank,1,2, *should be correct...blank is for order execution date .see sub01=pos 94


        #sub6 start
        v['sequence1']=str(seq).rjust(4).replace(' ','0')
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
                v['type_accnt']=''
        v['bank_country_code']=''
        part_addres_obj=pool.get('res.partner.address')
        part_address_id = part_addres_obj.search(cr, uid, [('partner_id','=',bank1['partner_id'][0])])
        part_address = part_addres_obj.browse(cr, uid, part_address_id,context)
        if bank1['bank_address_id']:
            bank2 = part_addres_obj.read(cr, uid, bank1['bank_address_id'][0])#get bank address of counrty for pos 113-114 sub06
            if bank2['country_id']:
                code_country=pool.get('res.country').read(cr,uid,bank2['country_id'][0],['code'])#get bank address of counrty for pos 113-114 sub06
                v['bank_country_code']=code_country['code']
        for i in part_address:
            v['benf_name']=i.name
            v['benf_address']=str(i.street)+str(i.street2)+str(i.city)+str(i.state_id.name)+str(i.country_id.name)#continue this record to sub07...pos 8-42


        #seg 10 start
        v['sequence2']=str(seq).rjust(4).replace(' ','0')
        v['sub_div10']='10'
        v['order_msg']=''#msg from order customer to order cutomer bank *should be correct
        v['method_pay']='EUR'#see attachment 1.5..multiple values are available *should be correct
        v['charge_code']='' #*should be correct
        v['cur_code_debit']=''#'BEF' *should be correct
        v['debit_cost']='000000000000'#field will only fill when ordering customer account debitted with charges if not field will contain blank or zero
        v['benf_country_code']=i.country_id.code
        pay_order =pay_order+record_payline(v).generate()


    #trailer record........start
    v2['tot_record']=str(seq)
    v2['tot_pay_order']=str(seq)
    v2['tot_amount']=float2str(total)
    pay_trailer=record_trailer(v2).generate()
    try:
        pay_order=pay_header+pay_order+pay_trailer
    except Exception,e :
        log= log +'\n'+ str(e) + 'CORRUPTED FILE !\n'
        raise
    pool.get('account.pay').write(cr,uid,[id_exp],{'note':log,'name':base64.encodestring(pay_order or "")})
    return {'note':log, 'pay': base64.encodestring(pay_order)}


def float2str(lst):
            #return str(lst).replace('.','')
            return str(lst).rjust(15).replace('.','0')

class wizard_pay_create(wizard.interface):
    states = {
        'init':{
        'actions' : [],
        'result' : {'type' : 'form',
                    'arch' : payment_form,
                    'fields' : payment_fields,
                    'state' : [('Create File', 'Export Payment') ]}
        },
        'Create File' : {
            'actions' : [_create_pay],
            'result' : {'type' : 'form',
                        'arch' : export_form,
                        'fields' : export_fields,
                        'state' : [('end', 'Ok') ]}
        },

    }

wizard_pay_create('account.payment_create')