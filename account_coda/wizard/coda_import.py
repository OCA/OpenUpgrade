##############################################################################
#
# Copyright (c) 2004-2006 TINY SPRL. (http://tiny.be) All Rights Reserved.
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

import pooler
import time
import datetime
import wizard
import netsvc
import base64
from osv import osv

codawiz_form = """<?xml version="1.0"?>
<form string="Import Coda Statement">
<separator colspan="4" string="Select your bank journal :" />
    <field name="journal_id" colspan="1" domain="[('type','=','cash')]" />
    <newline />
    <field name="def_payable" />
    <newline />
    <field name="def_receivable" />
    <separator string="Clic on 'New' to select your file :" colspan="4"/>
    <field name="coda"/>
</form>
"""

codawiz_fields = {
    'journal_id' : {
        'string':'Bank Journal',
        'type':'many2one',
        'relation':'account.journal',
        'required':True,
    },
    'coda' : {
        'string':'Coda File',
        'type':'binary',
        'required':True,
    },
    'def_payable' : {
        'string' : 'Default Payable Account',
        'type' : 'many2one',
        'relation': 'account.account',
        'required':True,
    },
    'def_receivable' : {
        'string' : 'Default receivable Account',
        'type' : 'many2one',
        'relation': 'account.account',
        'required':True,
    }
}

result_form = """<?xml version="1.0"?>
<form string="Import Coda Statement">
<separator colspan="4" string="Results :" />
    <field name="note" colspan="4" nolabel="1" width="500"/>
</form>
"""

result_fields = {

    'note' : {'string':'Log','type':'text'}

}

def _coda_parsing(self, cr, uid, data, context):
    print "Coda Parsing is start here..........."
    pool = pooler.get_pool(cr.dbname)
    codafile = data['form']['coda']
    jur_id = data['form']['journal_id']
    def_pay_acc = data['form']['def_payable']
    def_rec_acc = data['form']['def_receivable']
    recordlist = base64.decodestring(codafile).split('\r\n')
    recordlist.pop()
    resstatement = {}
    resstatement['journal_id'] = jur_id
    resstatement_lines = []
    bn_statement = 0
    isHeader = False
    isFooter = False
    isOldBal = False
    isNewBal = False
    str_log = ""
    err_log = ""
    for line in recordlist:
        if line[0] == '0':
            print "Header Record"
            if not isHeader:
                d = str2date(line[5:11])
                print d
                resstatement['date'] = d
                period_id = pool.get('account.period').search(cr,uid,[('date_start','<=',time.strftime("%y/%m/%d",time.strptime(d,"%d/%m/%y"))),('date_stop','>=',time.strftime("%y/%m/%d",time.strptime(d,"%d/%m/%y")))])
                resstatement['period_id'] = period_id[0]
                bn_statement = int(pool.get('account.bank.statement').create(cr,uid,resstatement))
                isHeader = True

        elif line[0] == '1':
            print "OldBalance Record"
            if not isOldBal:
                bal_start = list2float(line[43:58])
                if line[42] == '1':
                    bal_start = - bal_start
                pool.get('account.bank.statement').write(cr,uid,[bn_statement],{'balance_start': bal_start})
                isOldBal = True
        elif line[0]=='2':
            print "Details Record"
            if line[1]=='1':
                print "movement Record here "
                st_line = {}
                st_line['statement_id']=bn_statement
                st_line['name'] = line[2:10]
                st_line['date'] = str2date(line[115:121])
                st_line_amt = list2float(line[32:47])

                if line[31] == '1':
                    st_line_amt = - st_line_amt
                    st_line['account_id'] = def_pay_acc
                else:
                    st_line['account_id'] = def_rec_acc
                st_line['amount'] = st_line_amt
                bn_st_line = pool.get('account.bank.statement.line').create(cr,uid,st_line)
            elif line[1] == '3':
                print ""
                st_line_name = line[2:10]
                st_line_partner_acc = str(line[10:47]).strip()
                bank_ids = pool.get('res.partner.bank').search(cr,uid,[('number','=',st_line_partner_acc)])
                if bank_ids:
                    bank = pool.get('res.partner.bank').browse(cr,uid,bank_ids[0],context)
                    part = bank.partner_id
                    line_id = pool.get('account.bank.statement.line').search(cr,uid,[('name','=',st_line_name)])
                    if line_id:
                        _line = pool.get('account.bank.statement.line').browse(cr,uid,line_id.pop(),context)
                        if _line['amount'] < 0:
                            pool.get('account.bank.statement.line').write(cr,uid,[_line['id']],{'partner_id':part.id, 'account_id' : part.property_account_payable[0]})
                        else:
                            pool.get('account.bank.statement.line').write(cr,uid,[_line['id']],{'partner_id':part.id, 'account_id' : part.property_account_receivable[0]})

#
#                partner_id = pool.get('res.partner').search(cr,uid,[('name','=',st_line_partner_name)])
#                if partner_id:
#
#                    part = pool.get('res.partner').browse(cr, uid, partner_id[0], context)
#
#                    line_id = pool.get('account.bank.statement.line').search(cr,uid,[('name','=',st_line_name)])
#                    if line_id:
#                        _line = pool.get('account.bank.statement.line').browse(cr,uid,line_id.pop(),context)
#                        print _line['amount']
#                        print _line['id']
#                        if _line['amount'] < 0:
#                            pool.get('account.bank.statement.line').write(cr,uid,[_line['id']],{'partner_id':part.id, 'account_id' : part.property_account_payable[0]})
#                        else:
#                            pool.get('account.bank.statement.line').write(cr,uid,[_line['id']],{'partner_id':part.id, 'account_id' : part.property_account_receivable[0]})
#                #end if
        elif line[0]=='3':
            print "Information Record"
        elif line[0]=='8':
            print "New Balance"
            if not isNewBal:
                bal_end = list2float(line[42:57])
                if line[41] == '1':
                    bal_end = - bal_end
                print bal_end
                pool.get('account.bank.statement').write(cr,uid,[bn_statement],{'balance_end_real': bal_end})
                isNewBal = True
        elif line[0]=='9':
            print "Trailler Record"

    #end for
    print "Finish Loop"
    str_log = "Coda File is Imported Successfully"
    create_dict = {
        'name':codafile,
        'statement_ids':bn_statement,
        'note':str_log,
        'journal_id':data['form']['journal_id'],

        }
    print create_dict
    pool.get('account.coda').create(cr, uid,create_dict)

    return {'note':str_log}


def str2date(date_str):
            return time.strftime("%y/%m/%d",time.strptime(date_str,"%d%m%y"))
def str2float(str):
    try:
        return float(str)
    except:
        return 0.0

def list2str(lst):
            return str(lst).strip('[]').replace(',','').replace('\'','')

def list2float(lst):
            try:
                return str2float((lambda s : s[:-3] + '.' + s[-3:])(lst))
            except:
                return 0.0
def _import_data(self, cr, uid, data, context):
    data['form']['journal_id'] = 3
    data['form']['def_payable']=5
    data['form']['def_receivable']=10
    return data['form']
class coda_import(wizard.interface):
    states = {
        'init' : {
            'actions' : [],
            'result' : {'type' : 'form',
                    'arch' : codawiz_form,
                    'fields' : codawiz_fields,
                    'state' : [('end', 'Cancel'),('extraction', 'Ok') ]}
        },
        'extraction' : {
            'actions' : [_coda_parsing],
            'result' : {'type' : 'form',
                        'arch' : result_form,
                        'fields' : result_fields,
                        'state' : [('end', 'Quit') ]}
        },

    }
coda_import("account.coda_import")









